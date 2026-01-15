import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.schemas import ChatRequest, ChatResponse
from app.rag.container import get_rag
import json

router = APIRouter(tags=["Chat"])
logger = logging.getLogger("app.chat")

@router.post("/chat", response_model=ChatResponse, summary="Chat with the RAG Bot")
def chat(req: ChatRequest):
    logger.info("Received message: %s", req.message)

    # RAG container
    rag = get_rag()

    answer, citations = rag.chat(
        req.message, 
        history=req.history, 
        session_id=req.session_id
    )

    return ChatResponse(answer=answer, citations=citations)


@router.post("/chat/stream", summary="Chat with streaming tokens (SSE)")
def chat_stream(req: ChatRequest):
    logger.info("Received STREAM message: %s", req.message)

    rag = get_rag()

    def event_stream():
        prompt, citations, deny_text = rag.build_prompt_and_citations(
            question=req.message,
            history=req.history,
            session_id=req.session_id,
        )
        if prompt is None:
            if deny_text:
                for word in deny_text.split():
                    yield f"event: token\ndata: {json.dumps({'t': word + ' '})} \n\n"
            yield "event: done\ndata: {} \n\n"
            return

        #buffering the answer to send citation only if there is prompt 
        answer_buffer = []
        


        # deny path (no llm call)    
        if deny_text:
            for word in deny_text.split():
                yield f"event: token\ndata: {json.dumps({'t': word + ' '})}\n\n"
            yield "event: done\ndata: {}\n\n"
            return
        
        # streams token from llm 
        for chunk in rag.llm.generate_stream(prompt):
            if chunk:
                answer_buffer.append(chunk)
                yield f"event: token\ndata: {json.dumps({'t': chunk})}\n\n"
        
        full_answer = "".join(answer_buffer)

        if rag._is_no_answer(full_answer):
            yield "event: done\ndata: {}\n\n"
            return

        # send citations first
        yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
        yield "event: done\ndata: {}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
