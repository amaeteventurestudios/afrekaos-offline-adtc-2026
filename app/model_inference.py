"""Model inference helper for AfrekaOS Offline.

Connects the locked Qwen model (via llama.cpp) to grounded/ungrounded prompts.
Standard library only. Does not call the model at import time. Fully offline.

Binary resolution mirrors the runtime scripts: prefer llama-completion (clean
single-turn + supports --chat-template-file), then llama-cli, then llama.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from app import prompt_context, runtime_config

REPO_ROOT = Path(__file__).resolve().parent.parent
QWEN_TEMPLATE = REPO_ROOT / "templates" / "qwen3_nonthinking.jinja"

# Terms from the Task 002C prompt-1 derailment (chemistry / multiple-choice).
_DERAILMENT_RE = re.compile(
    r"mendeleev|periodic table|electron config|atomic number|"
    r"electron configuration|period of the elements",
    re.IGNORECASE,
)


def _resolve_llama_binary() -> Optional[str]:
    """Return the best available llama binary path, or None."""
    explicit = runtime_config.get_llama_binary()
    if explicit and (Path(explicit).is_file()):
        return explicit
    for name in ("llama-completion", "llama-cli", "llama"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _command_family(binary: str) -> str:
    base = Path(binary).name
    if base == "llama-completion":
        return "llama-completion"
    if base == "llama-cli":
        return "llama-cli"
    if base == "llama":
        return "llama"
    return "unknown"


def _supports_flag(binary: str, flag: str) -> bool:
    try:
        out = subprocess.run(
            [binary, "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            timeout=15,
            text=True,
        )
    except Exception:
        return False
    return flag in (out.stdout or "")


def _qwen_extra_args(binary: str) -> list[str]:
    """Build Qwen direct-mode args: template (--jinja --chat-template-file) +
    -no-cnv (llama-completion only). Honors AFREKAOS_QWEN_NO_THINK at run time
    via prompt suffixing, not here."""
    args: list[str] = []
    if QWEN_TEMPLATE.is_file() and _supports_flag(binary, "--chat-template-file"):
        args += ["--jinja", "--chat-template-file", str(QWEN_TEMPLATE)]
    if _command_family(binary) == "llama-completion" and _supports_flag(binary, "-no-cnv"):
        args += ["-no-cnv"]
    return args


def extract_visible_answer(raw_stdout: str, raw_stderr: str = "") -> dict:
    """Extract the user-visible answer from raw model output.

    This is the single source of truth for what counts as the "visible answer".
    Used by both the UI rendering path and `run_model`'s structured return, so
    `visible_answer_chars` always equals the length of the answer the user sees.

    Behavior:
    - Remove llama.cpp log lines (timestamps, I/W/L log prefixes, known log
      prefixes). This is line-based, so it does NOT strip genuine answer text
      that merely happens to start with the letters I, W, or L followed by a
      space — it requires a llama.cpp log timestamp or log-line shape.
    - Treat an empty Qwen non-thinking template block like
      ``<think>\\n\\n</think>`` as NON-fatal (the intended direct-mode marker).
    - Detect a real think trap ONLY when:
        * ``<think>`` appears without a closing ``</think>``, OR
        * substantial hidden reasoning appears inside ``<think>`` and no answer
          exists outside it.
    - Preserve answer text after a closed ``</think>``.
    - Preserve answer text when there is no ``<think>`` block at all.

    Returns a dict with:
        clean_answer, clean_answer_chars, contains_think, think_trap,
        extraction_warning
    """
    # Combine stderr into the stream for completeness; llama.cpp is usually run
    # with stderr=STDOUT, so raw_stderr is often empty.
    combined = raw_stdout if not raw_stderr else raw_stdout + "\n" + raw_stderr

    contains_think = "<think>" in combined

    # Remove closed <think>...</think> blocks (the empty template AND real
    # reasoning blocks). Non-greedy, DOTALL so newlines are included.
    stripped = re.sub(r"<think>.*?</think>", "", combined, flags=re.DOTALL)

    # After removing closed pairs, anything left with an opening <think> is an
    # UNCLOSED block — a genuine think trap. Drop it from the answer.
    unclosed_present = "<think>" in stripped
    stripped = re.sub(r"<think>.*", "", stripped, flags=re.DOTALL)

    # A real think trap: an unclosed <think> with substantial trailing content.
    # Re-derive from the combined text (consistent with the analyzer definition).
    after_last_close = combined.rsplit("</think>", 1)[-1]
    unclosed_with_content = "<think>" in after_last_close and len(after_last_close.strip()) > 40
    # Also trap if there was an unclosed <think> anywhere AND no closed pair
    # left visible answer behind.
    think_trap = bool(unclosed_with_content)

    # Remove llama.cpp log lines from the visible portion. Line-based filtering
    # keyed on the log-line SHAPE (timestamp + I/W/L, or I/W/L + log prefix, or
    # a known log prefix at line start). We intentionally do NOT strip bare
    # "I/W/L + space" lines, which would eat genuine answer sentences like
    # "I should restock..." — only log-shaped lines are removed.
    _LOG_PREFIX = (
        r"(?:repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|"
        r"top_n_sigma|mirostat|adaptive_|frequency_penalty|presence_penalty|"
        r"repeat_penalty|sampler|generate|llama_|common_|chat template|"
        r"interactive|Press|To return|If you want|Not using|system_info|"
        r"system prompt|warming up|threadpool|backend init|fitting params|"
        r"control-looking|load the model|llama_completion|llama_model_loader|"
        r"main:|load:|print_timing|save:|slot)"
    )
    log_line_re = re.compile(
        # timestamped log: "0.03.201.688 I ..." or "0.03.201.688 <prefix>"
        r"^(?:\d+\.){2,3}\d+\s+(?:[IWL]\s+)?" + _LOG_PREFIX,
        re.IGNORECASE,
    )
    log_prefix_re = re.compile(
        # "I llama_model_loader: ...", "W system_info: ...", "L print_timing: ..."
        r"^[IWL]\s+" + _LOG_PREFIX,
        re.IGNORECASE,
    )
    bare_ts_re = re.compile(r"^(?:\d+\.){2,3}\d+\s+[IWL]\s")
    ts_only_re = re.compile(r"^(?:\d+\.){2,3}\d+\s")
    prefix_only_re = re.compile(r"^" + _LOG_PREFIX, re.IGNORECASE)

    cleaned_lines = []
    for ln in stripped.splitlines():
        s = ln.strip()
        if not s:
            continue
        if (bare_ts_re.match(ln) or ts_only_re.match(ln)
                or log_line_re.match(ln) or log_prefix_re.match(ln)
                or prefix_only_re.match(s)):
            continue
        cleaned_lines.append(ln)
    clean_answer = "\n".join(cleaned_lines).strip()

    # Extraction warning: a benign note when a think marker was present but no
    # trap was detected (the normal Qwen non-thinking template case).
    extraction_warning = ""
    if think_trap:
        extraction_warning = (
            "Unclosed <think> block detected; hidden reasoning was removed."
        )
    elif contains_think and not clean_answer:
        extraction_warning = (
            "A <think> block was present but no answer text was found outside it."
        )

    return {
        "clean_answer": clean_answer,
        "clean_answer_chars": len(clean_answer),
        "contains_think": contains_think,
        "think_trap": think_trap,
        "extraction_warning": extraction_warning,
    }


def build_ungrounded_prompt(user_question: str) -> str:
    """Build a direct-answer prompt WITHOUT retrieved context.

    Still includes the AfrekaOS role and answer rules so the only variable
    between ungrounded and grounded is the local context block.
    """
    rules = "\n".join(f"- {r}" for r in prompt_context.ANSWER_RULES)
    return (
        f"{prompt_context.ROLE_LINE}\n\n"
        f"Operator question:\n{user_question}\n\n"
        f"Answer rules:\n{rules}\n\n"
        f"Answer:"
    )


def _maybe_no_think(prompt: str) -> str:
    """Append /no_think if AFREKAOS_QWEN_NO_THINK=1."""
    if os.environ.get("AFREKAOS_QWEN_NO_THINK", "") == "1":
        return f"{prompt} /no_think"
    return prompt


def run_model(
    prompt: str,
    output_path: Optional[str] = None,
    max_tokens: int = 384,
    timeout_seconds: int = 120,
) -> dict:
    """Run a single prompt through the local model.

    Returns a structured dict. Never raises on model/runtime failure; reports
    via the 'ok'/'error' fields. stdin is DEVNULL so it cannot hang on stdin.
    """
    result = {
        "ok": False,
        "model_path": str(runtime_config.get_model_path()),
        "llama_binary": None,
        "command_family": None,
        "output_path": output_path,
        "return_code": None,
        "timed_out": False,
        # Backwards-compatible raw counts.
        "stdout_chars": 0,
        "stderr_chars": 0,
        # Backwards-compatible answer fields; now derived from the unified
        # extract_visible_answer() so they match the UI.
        "visible_answer_chars": 0,
        "contains_think": False,
        # New structured answer fields (Task 004D).
        "raw_stdout_chars": 0,
        "raw_stderr_chars": 0,
        "clean_answer": "",
        "clean_answer_chars": 0,
        "think_trap": False,
        "extraction_warning": "",
        "error": None,
    }

    model_path = runtime_config.get_model_path()
    if not model_path.is_file():
        result["error"] = f"model file not found: {model_path}"
        return result

    binary = _resolve_llama_binary()
    if not binary:
        result["error"] = "no llama.cpp binary found (set LLAMA_CPP_BIN)"
        return result

    result["llama_binary"] = binary
    result["command_family"] = _command_family(binary)

    extra = _qwen_extra_args(binary)
    cmd = [binary, "-m", str(model_path)] + extra + [
        "-p", prompt,
        "-n", str(max_tokens),
        "-t", "4",
        "--temp", "0.7",
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            text=True,
        )
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["error"] = f"timed out after {timeout_seconds}s"
        out = (proc.stdout if isinstance(proc, subprocess.Popen) else "") or ""
    except Exception as exc:  # pragma: no cover - defensive
        result["error"] = f"failed to run: {exc}"
        return result
    else:
        result["return_code"] = proc.returncode
        out = proc.stdout or ""

    result["stdout_chars"] = len(out)
    result["raw_stdout_chars"] = len(out)

    # Unified extraction: the same function the UI uses, so visible_answer_chars
    # always equals the length of the answer the user sees (clean_answer_chars).
    ext = extract_visible_answer(out)
    result["contains_think"] = ext["contains_think"]
    result["visible_answer_chars"] = ext["clean_answer_chars"]  # == clean
    result["clean_answer"] = ext["clean_answer"]
    result["clean_answer_chars"] = ext["clean_answer_chars"]
    result["think_trap"] = ext["think_trap"]
    result["extraction_warning"] = ext["extraction_warning"]

    if output_path:
        opath = Path(output_path)
        opath.parent.mkdir(parents=True, exist_ok=True)
        opath.write_text(out, encoding="utf-8", errors="replace")
        result["output_path"] = str(opath)

    result["ok"] = result["return_code"] == 0 and not result["timed_out"]
    return result


def run_ungrounded(
    user_question: str,
    output_path: Optional[str] = None,
    max_tokens: int = 384,
    timeout_seconds: int = 120,
) -> dict:
    """Run an ungrounded (no retrieval) direct-answer prompt."""
    prompt = _maybe_no_think(build_ungrounded_prompt(user_question))
    return run_model(
        prompt,
        output_path=output_path,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


def run_grounded(
    user_question: str,
    output_path: Optional[str] = None,
    retrieval_limit: int = 5,
    max_tokens: int = 384,
    timeout_seconds: int = 120,
) -> dict:
    """Run a retrieval-grounded prompt."""
    grounded = prompt_context.build_grounded_prompt(user_question, limit=retrieval_limit)
    prompt = _maybe_no_think(grounded)
    return run_model(
        prompt,
        output_path=output_path,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


def inference_summary() -> dict:
    """Return a non-raising summary of the current inference config."""
    binary = _resolve_llama_binary()
    model_path = runtime_config.get_model_path()
    return {
        "model_path": str(model_path),
        "model_exists": model_path.is_file(),
        "llama_binary": binary,
        "command_family": _command_family(binary) if binary else None,
        "qwen_template_present": QWEN_TEMPLATE.is_file(),
        "qwen_no_think_env": os.environ.get("AFREKAOS_QWEN_NO_THINK", ""),
    }


__all__ = [
    "extract_visible_answer",
    "build_ungrounded_prompt",
    "run_model",
    "run_ungrounded",
    "run_grounded",
    "inference_summary",
]
