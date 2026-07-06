"""Runtime configuration for AfrekaOS Offline.

Dependency-free. Resolves the local model path and the llama.cpp binary purely
from environment overrides and sensible defaults. Nothing here touches the
network; the offline constraint is absolute during judged runtime.

Overrides
---------
AFREKAOS_MODEL_PATH : str
    Path to the GGUF model file. Defaults to model/afrekaos.gguf (relative to
    the repository root).
LLAMA_CPP_BIN : str
    Path to the llama.cpp binary (e.g. llama-cli / main). If unset, callers
    should treat the binary as "not configured".
"""

from __future__ import annotations

import os
from pathlib import Path

# Resolve the repository root from this file's location (app/runtime_config.py).
REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL_PATH = "model/afrekaos.gguf"


def get_model_path() -> Path:
    """Return the resolved model path.

    Honors AFREKAOS_MODEL_PATH if set; otherwise uses DEFAULT_MODEL_PATH
    resolved against the repository root. The returned path is absolute.
    """
    raw = os.environ.get("AFREKAOS_MODEL_PATH", DEFAULT_MODEL_PATH)
    p = Path(raw)
    if not p.is_absolute():
        # Resolve the parent directory but keep the final path component intact
        # so a symlink (e.g. model/afrekaos.gguf -> candidates/...) keeps its
        # canonical name rather than being rewritten to its target.
        p = (REPO_ROOT / p).parent.resolve() / p.name
    return p


def get_llama_binary() -> str:
    """Return the configured llama.cpp binary path, or "" if not set.

    We intentionally do NOT search PATH here: a missing explicit override
    means "not configured", so callers fail loudly rather than silently
    invoking an arbitrary binary.
    """
    return os.environ.get("LLAMA_CPP_BIN", "").strip()


def model_exists() -> bool:
    """True if the resolved model file exists and is a regular file."""
    p = get_model_path()
    return p.is_file()


def runtime_summary() -> dict:
    """Return a small, human-readable summary of the current runtime config.

    Useful for profiler/smoke scripts and for diagnostics. Does not raise.
    """
    model_path = get_model_path()
    llama_bin = get_llama_binary()
    return {
        "model_path": str(model_path),
        "model_exists": model_path.is_file(),
        "llama_cpp_bin": llama_bin,
        "llama_cpp_bin_configured": bool(llama_bin),
        "llama_cpp_bin_exists": bool(llama_bin) and Path(llama_bin).is_file(),
        "default_model_path": DEFAULT_MODEL_PATH,
        "afrekaos_model_path_env": os.environ.get("AFREKAOS_MODEL_PATH", ""),
    }


__all__ = [
    "DEFAULT_MODEL_PATH",
    "REPO_ROOT",
    "get_model_path",
    "get_llama_binary",
    "model_exists",
    "runtime_summary",
]
