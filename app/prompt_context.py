"""Prompt-context builder for AfrekaOS Offline grounded prompts.

Uses app/retrieval.py to fetch local context, then assembles a grounded prompt
that instructs the model to give practical SME operating guidance. Does NOT call
the model. Standard library only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app import language_mode, retrieval

REPO_ROOT = Path(__file__).resolve().parent.parent

ROLE_LINE = (
    "You are AfrekaOS, an offline SME operations copilot for African small "
    "business operators."
)

# Explicit delimiter marking where the model's final answer must begin.
# Extraction prefers text after this line so echoed prompt/context/rules are
# never shown to the user as the answer.
FINAL_GUIDANCE_DELIMITER = "BEGIN FINAL OPERATING GUIDANCE"

ANSWER_RULES = [
    "Give practical, concrete operating steps.",
    "Stay strictly on SME operations (inventory, cashflow, credit, supplier, staffing, expansion).",
    "Do NOT make accounting, banking, payroll, tax-filing, or ERP claims.",
    "Do NOT invent facts. If records or numbers are needed, say so.",
    "Do NOT include hidden chain-of-thought or a <think> block. Answer directly.",
    "Answer as a short checklist.",
    "Where the operator should verify their own records before acting, say so explicitly.",
]

# Instructions appended after the delimiter so the model answers only with the
# final checklist and does not repeat the prompt/context/rules.
FINAL_GUIDANCE_INSTRUCTIONS = [
    "Answer only after this line.",
    "Do not repeat the local context.",
    "Do not repeat the source list.",
    "Do not repeat the answer rules.",
    "Do not reveal hidden chain-of-thought.",
    "Give only the final checklist.",
]


def build_context_block(query: str, limit: int = 5) -> str:
    """Return a formatted block of retrieved local context for a query.

    If the index is missing or returns nothing, returns a clear placeholder
    note instead of raising.
    """
    try:
        results = retrieval.search(query, limit=limit)
    except FileNotFoundError as exc:
        return f"[no local context] {exc}"
    except RuntimeError as exc:
        return f"[retrieval error] {exc}"

    if not results:
        return "[no local context] No matching SME notes found for this query."

    lines = ["Local SME operations context (retrieved offline):"]
    for i, r in enumerate(results, 1):
        lines.append("")
        lines.append(f"{i}. [{r['category']}] {r['title']}")
        lines.append(f"   source: {r['path']}")
        lines.append(f"   {r['snippet']}")
    return "\n".join(lines)


def build_grounded_prompt(
    user_question: str, limit: int = 5, language: str = "en"
) -> str:
    """Assemble a full grounded prompt: role + context + question + rules.

    Does not call the model. The returned string is meant to be handed to a
    local runtime (e.g. llama-completion) by the caller.

    ``language`` selects the response language (normalized via language_mode;
    unknown codes fall back to English). The retrieved context remains English
    in this version; only the answer language is controlled. There is no cloud
    translation.

    The prompt ends with an explicit FINAL_GUIDANCE_DELIMITER so that if the
    runtime echoes the prompt back, extraction can keep only the text after the
    delimiter (the model's final operating guidance).
    """
    lang_code = language_mode.normalize_language_code(language)
    lang_label = language_mode.get_language_label(lang_code)
    lang_instruction = language_mode.get_language_instruction(lang_code)

    context = build_context_block(user_question, limit=limit)
    rules = "\n".join(f"- {r}" for r in ANSWER_RULES)
    final_instr = "\n".join(f"- {r}" for r in FINAL_GUIDANCE_INSTRUCTIONS)

    return (
        f"{ROLE_LINE}\n\n"
        f"{context}\n\n"
        f"Operator question:\n{user_question}\n\n"
        f"Answer rules:\n{rules}\n\n"
        f"Response language: {lang_label}\n"
        f"{lang_instruction}\n"
        f"- Do not use cloud translation or any external translation service.\n"
        f"- If a term is difficult to translate, use simple wording or keep "
        f"the business term in English.\n"
        f"- The retrieved context above may be in English; answer in the "
        f"selected response language regardless.\n\n"
        f"{FINAL_GUIDANCE_DELIMITER}\n"
        f"{final_instr}\n\n"
    )


__all__ = [
    "ROLE_LINE",
    "ANSWER_RULES",
    "FINAL_GUIDANCE_DELIMITER",
    "FINAL_GUIDANCE_INSTRUCTIONS",
    "build_context_block",
    "build_grounded_prompt",
]
