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
_THINK_OPEN_RE = re.compile(r"<think>")


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


def _visible_answer(text: str) -> str:
    """Text outside <think> blocks, with llama.cpp log lines removed."""
    out = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    out = re.sub(r"<think>.*", "", out, flags=re.DOTALL)
    cleaned = []
    for ln in out.splitlines():
        s = ln.strip()
        if re.match(r"^\d+\.\d+\.\d+\.\d+\s+[IWL]\s", ln):
            continue
        if re.match(
            r"^(?:repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|"
            r"top_n_sigma|mirostat|adaptive_|frequency_penalty|presence_penalty|"
            r"repeat_penalty|sampler|generate|llama_|common_|chat template|"
            r"interactive|Press|To return|If you want|Not using|system_info)",
            s,
            re.IGNORECASE,
        ):
            continue
        cleaned.append(ln)
    return "\n".join(cleaned).strip()


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
        "stdout_chars": 0,
        "stderr_chars": 0,
        "visible_answer_chars": 0,
        "contains_think": False,
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
    result["contains_think"] = bool(_THINK_OPEN_RE.search(out))
    result["visible_answer_chars"] = len(_visible_answer(out))

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
    "build_ungrounded_prompt",
    "run_model",
    "run_ungrounded",
    "run_grounded",
    "inference_summary",
]
