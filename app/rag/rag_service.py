from __future__ import annotations
from typing import List, Optional, Tuple, Any, Dict
from pathlib import Path
import logging

from app.core.config import get_settings

from app.api.schemas import ChatTurn
from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig
from app.rag.embeddings.embedder_base import Embedder
from app.rag.llm.llm_base import LLM

#rag components
from app.rag.prompts.loader import PromptLoader
from app.rag.retrieve.prompt_builder import PromptBuilder
from app.rag.retrieve.context_packer import ContextPacker, ContextPackerConfig
from app.rag.retrieve.query_rewriter import QueryRewriter, QueryRewriterConfig
from app.rag.retrieve.retriever import Retriever, RetrieverConfig
from app.rag.retrieve.query_router import QueryRouter
from app.rag.retrieve.intent_router import IntentRouter

#cite 
import re
_CITE_RE = re.compile(r"\[(\d{1,3})\]") 

class RAGService:
    """
        Retrieval-Augmented Generation (RAG) Service

        This service ties together the vector store and the embedder to provide
        retrieval-augmented responses.
    """

    def __init__(self, embedder: Embedder, llm: LLM, store = None):
        
        self.embedder = embedder
        self.llm = llm
        
        settings = get_settings()

        # storage
        self.persist_directory = Path(settings.rag.persist_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = settings.rag.collection_name

        # retrieval knobs
        self.top_k = settings.rag.top_k
        self.retrieval_pool_k = settings.rag.retrieval_pool_k
        self.good_threshold = settings.rag.distance.good_threshold
        self.weak_threshold = settings.rag.distance.weak_threshold

        # prompt packing knobs
        self.max_context_chars = settings.rag.max_context_chars
        self.max_chunks_in_prompt = settings.rag.max_chunks_in_prompt
        self.max_history = settings.rag.max_history

        # rewrite knobs
        self.enable_rewrite_query = settings.rag.rewrite.enabled
        self.rewrite_max_history_turns = settings.rag.rewrite.max_history_turns
        self.rewrite_trigger_max_words = settings.rag.rewrite.trigger_max_words

        #policy
        self.no_answer_text = settings.policy.deny_message
        self.require_quotes_in_weak_mode = settings.policy.require_quotes_in_weak_mode
        
        # store creation
        if store is None:
            from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig
            store_cfg = ChromaStoreConfig(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
            self.store = ChromaStore(store_cfg)
        else:
            self.store = store

        #logger
        self.logger = logging.getLogger(__name__)

        # prompts 
        self.prompt_loader = PromptLoader()
        prompts = self.prompt_loader.load()
        self.system_prompt = prompts.system
        self.answer_prompt = prompts.answer
        self.rewrite_prompt = prompts.rewrite

        #prompt builder
        self.prompt_builder = PromptBuilder(
            system_prompt=self.system_prompt,
            answer_prompt=self.answer_prompt,
        )

        # context packer
        self.context_packer = ContextPacker(
            ContextPackerConfig(
                max_context_chars=self.max_context_chars,
                max_chunks_in_prompt=self.max_chunks_in_prompt,
            )
        )

        # rewriter
        self.rewriter = QueryRewriter(
            llm=self.llm,
            rewrite_template=self.rewrite_prompt,
            cfg = QueryRewriterConfig(
                enabled=self.enable_rewrite_query,
                max_history_turns=self.rewrite_max_history_turns,
                trigger_max_words=self.rewrite_trigger_max_words,
            )
        )

        # retriever
        self.retriever = Retriever(
            embedder=self.embedder,
            store=self.store,
            cfg=RetrieverConfig(top_k=self.top_k, retrieval_pool_k= self.retrieval_pool_k),
        )

        # query router
        self.query_router = QueryRouter()

        #intent router
        self.intent_router = IntentRouter.build(self.embedder)

    def _user_only_history(self, history: Optional[List[ChatTurn]]) -> List[ChatTurn]:
        if not history:
            return []
        return [t for t in history if getattr(t, "role", None) == "user"]
    
    def _select_used_citations(self, answer: str, citations: List[Dict], max_used: int = 3) -> List[Dict]:
        """
            Keep only citation use din the answer
        """
        if not citations:
            return
        
        if not answer:
            return citations[:max_used]

        used_nums = []
        seen = set()
        for m in _CITE_RE.finditer(answer):
            n = int (m.group(1))
            if n not in seen:
                seen.add(n)
                used_nums.append(n)
        
        used = []
        for n in used_nums:
            idx = n-1
            if 0 <= idx < len(citations):
                used.append(citations[idx])
        
        if not used:
            return citations[:max_used]

        return used[:max_used]

    def _is_no_answer(self, answer:str) -> bool:
        a = (answer or "").strip().lower()
        if not a:
            return True
        
        triggers = [
            "i couldn't find",
            "i could not find",
            "i can't find",
            "i cannot find",
            "not in the provided context",
            "provided context does not contain",
            "context does not contain",
            "based on the provided context",
            "I don't have enough information",
            "I do not have enough information",
            "I apologize",
            "unable to answer",
            "could you please provide"
        ]
        return any(t in a for t in triggers)

    def build_prompt_and_citations(
        self, 
        question:str,
        history: Optional[List[ChatTurn]] =None,
        session_id: Optional[str] = None,
    ) -> Tuple[Optional[str], List[dict]]:
        """
            Builds the final prompt + return citations (as a plain dicts) without calling the llm and if the retrieval is insuffienct , returns (None, [])
    
        """

        if self.intent_router.is_closing(question):
            return None, [], "No Problem - glad I could help! If you need anything else later, just ask."

        history = self._user_only_history(history)
        history = history[-4:] or []

        # print("HISTORY : ", history)
        rewrite_hist_text = self.prompt_builder.format_history(
            history or [],
            self.rewrite_max_history_turns
        )
        retrieve_question = self.rewriter.maybe_rewrite(question, rewrite_hist_text)
        
        where = self.query_router.route_where(retrieve_question)
        docs, citations, dists = self.retriever.retrieve(retrieve_question, where=where)
        
        if not docs:
            return None, [], self.no_answer_text

        best = dists[0] if dists else None
        if best is None or best > self.weak_threshold:
            return None, [], self.no_answer_text
        
        weak = best > self.good_threshold
        try:
            self.logger.info(f"RAG Chat: best_distance={best:.3f} weak={weak} question='{question}' session_id='{session_id}'")
        except Exception:
            pass
        # print("DEBUG: RAGService.chat best distance:", dists)

        history_text = self.prompt_builder.format_history(history or [], self.max_history)

        number_docs = [f"[{i+1}] {d} " for i , d in enumerate(docs)]
        context_text = self.context_packer.pack(number_docs)

        prompt = self.prompt_builder.build(
            history=history_text,
            context=context_text,
            question=question,
            weak=weak,
            require_quotes_in_weak_mode=self.require_quotes_in_weak_mode
        )
        if self._is_no_answer(prompt):
            print("*"*80)
            return None, [], self.no_answer_text
            
        cite_dicts = self._to_cite_dicts(citations)
        cite_dicts = self._select_used_citations(prompt, cite_dicts, max_used=3)

        return prompt, cite_dicts, None

    def _to_cite_dicts(self, citations) -> list[dict]:

        #gets citations as JSON-friendly dicts
        cite_dicts: List[dict] = []
        for c in citations:
            if hasattr(c, "model_dump"):
                cite_dicts.append(c.model_dump())
            else:
                cite_dicts.append({
                    "source": getattr(c, "source", None),
                    "doc_type": getattr(c, "doc_type", None),
                    "page": getattr(c, "page", None),
                    "chunk_id": getattr(c, "chunk_id", None),
                    "snippet": getattr(c, "snippet", None),
                })
            
        return cite_dicts

    def chat(self, question: str, history: Optional[List[ChatTurn]] = None, session_id: Optional[str] = None):
        """
        Full RAG pipeline: retrieve documents and generate an answer.

        Returns:
            - Generated answer string
            - List of corresponding citations
        """
        history = self._user_only_history(history)
        history = history[-4:] or []

        print("HISTORY : ", history)
        rewrite_hist_text = self.prompt_builder.format_history(
            history or [],
            self.rewrite_max_history_turns
        )
        retrieve_question = self.rewriter.maybe_rewrite(question, rewrite_hist_text)
        
        where = self.query_router.route_where(retrieve_question)
        docs, citations, dists = self.retriever.retrieve(retrieve_question, where=where)
        
        if not docs:
            return self.no_answer_text, []
        
        best = dists[0] if dists else None

        if best is None or best > self.weak_threshold:
            return self.no_answer_text, []
        
        weak = best > self.good_threshold

        try:
            self.logger.info(f"RAG Chat: best_distance={best:.3f} weak={weak} question='{question}' session_id='{session_id}'")
        except Exception:
            pass
        print("DEBUG: RAGService.chat best distance:", dists)

        history_text = self.prompt_builder.format_history(history or [], self.max_history)

        context_text = self.context_packer.pack(docs)

        prompt = self.prompt_builder.build(
            history=history_text,
            context=context_text,
            question=question,
            weak=weak,
            require_quotes_in_weak_mode=self.require_quotes_in_weak_mode
        )
        
        answer = self.llm.generate(prompt)

        return answer, citations