from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from app.api.schemas import ChatTurn

@dataclass(frozen=True)
class PromptBuilderConfig:
    pass


class PromptBuilder:
    """
        Builds the final LLM Prompt from the templates + runtime history inputs.
    
    """

    def __init__(self, *, system_prompt: str, answer_prompt: str) -> None:
        self.system_prompt = (system_prompt or "").strip()
        self.answer_prompt = (answer_prompt or "").strip()

    def format_history(self, history: list[ChatTurn], max_turns:int) -> str:
        """ 
            Format chat history into a single string for context.
        """
        if not history:
            return ""
        recent = history[-max_turns:]

        lines = []
        for turn in recent:
            role = "User" if turn.role == "user" else "Assistant"
            txt = (turn.text or "").strip()
            if txt:
                lines.append(f"{role}: {txt}")
        return "\n".join(lines).strip()

    def build(self, *, history: str, context: str, question: str, weak: bool, require_quotes_in_weak_mode: bool)-> str:
        """
            Returns a single prompt string:
            Expects 'context' to already be packed into a string
        """

        weak_rules = ""
        weak_answer_format=""
        if weak and require_quotes_in_weak_mode:
            weak_rules = (
                "IMPORTANT: The retrieved match is weak. Only answer if you can include ONE short verbatim quote "
                "from the reference information. If you cannot include a quote, respond with: "
                "\"Sorry — I couldn't find information about <topic> in the knowledge base.\""
            )
            weak_answer_format = (
                "\nAnswer format:\n"
                "<your answer here>\n"
                "Support/Citation: \"<one sentence quote from context>\""
            )

        prompt = self.system_prompt.format(weak_rules = weak_rules).strip()+"\n\n"
        prompt += self.answer_prompt.format(
            history=history or "",
            context=context or "",
            question=question or "",
            weak_answer_format=weak_answer_format, 
        ).strip()

        # print("prompt looks like this : ", prompt) 

        return prompt