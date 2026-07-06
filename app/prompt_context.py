"""Prompt-context builder for AfrekaOS Offline grounded prompts.

Uses app/retrieval.py to fetch local context, then assembles a grounded prompt
that instructs the model to give practical SME operating guidance. Does NOT call
the model. Standard library only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app import retrieval

REPO_ROOT = Path(__file__).resolve().parent.parent

ROLE_LINE = (
    "You are AfrekaOS, an offline SME operations copilot for African small "
    "business operators."
)

ANSWER_RULES = [
    "Give practical, concrete operating steps.",
    "Stay strictly on SME operations (inventory, cashflow, credit, supplier, staffing, expansion).",
    "Do NOT make accounting, banking, payroll, tax-filing, or ERP claims.",
    "Do NOT invent facts. If records or numbers are needed, say so.",
    "Do NOT include hidden chain-of-thought or a <think> block. Answer directly.",
    "Answer as a short checklist.",
    "Where the operator should verify their own records before acting, say so explicitly.",
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


def build_grounded_prompt(user_question: str, limit: int = 5) -> str:
    """Assemble a full grounded prompt: role + context + question + rules.

    Does not call the model. The returned string is meant to be handed to a
    local runtime (e.g. llama-completion) by the caller.
    """
    context = build_context_block(user_question, limit=limit)
    rules = "\n".join(f"- {r}" for r in ANSWER_RULES)

    return (
        f"{ROLE_LINE}\n\n"
        f"{context}\n\n"
        f"Operator question:\n{user_question}\n\n"
        f"Answer rules:\n{rules}\n\n"
        f"Answer:"
    )


__all__ = ["ROLE_LINE", "ANSWER_RULES", "build_context_block", "build_grounded_prompt"]
