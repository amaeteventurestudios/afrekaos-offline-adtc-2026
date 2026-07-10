#!/usr/bin/env python3
"""Target hardware profiler for AfrekaOS Offline (Task 005C).

Collects OS, CPU, memory, disk, model, retrieval, and FTS5 information for the
current machine. Standard library only. No internet, no cloud. If a value is
unavailable, writes "not available" rather than fabricating it.

Writes: artifacts/submission/target-hardware-profile.md
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = REPO_ROOT / "artifacts" / "submission"
OUT_PATH = SUBMISSION_DIR / "target-hardware-profile.md"


def _read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return "not available"


def _try_cmd(args: list[str], timeout: int = 5) -> str:
    try:
        r = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=timeout, text=True,
        )
        return (r.stdout or "").strip()
    except Exception:
        return "not available"


def _memory_info() -> dict:
    """Total and available memory in bytes, where detectable."""
    info = {"total_bytes": "not available", "available_bytes": "not available"}
    # Linux: /proc/meminfo
    mi = _read_file("/proc/meminfo")
    if mi and mi != "not available":
        for line in mi.splitlines():
            if line.startswith("MemTotal:"):
                parts = line.split()
                if len(parts) >= 2:
                    info["total_bytes"] = int(parts[1]) * 1024
            if line.startswith("MemAvailable:"):
                parts = line.split()
                if len(parts) >= 2:
                    info["available_bytes"] = int(parts[1]) * 1024
        if info["total_bytes"] != "not available":
            return info
    # macOS: sysctl hw.memsize (total) and vm_stat (available)
    if sys.platform == "darwin":
        raw = _try_cmd(["sysctl", "-n", "hw.memsize"])
        try:
            info["total_bytes"] = int(raw)
        except ValueError:
            pass
        vm = _try_cmd(["vm_stat"])
        if vm and vm != "not available":
            # Parse page size and free/active pages.
            pg_size = 4096
            for line in vm.splitlines():
                if "page size of" in line.lower():
                    try:
                        pg_size = int(line.split()[-1].rstrip("."))
                    except Exception:
                        pass
            free_pages = 0
            for line in vm.splitlines():
                if "free" in line.lower() and ":" in line:
                    try:
                        free_pages = int(line.split(":")[1].strip().rstrip("."))
                    except Exception:
                        pass
                    break
            if free_pages:
                info["available_bytes"] = free_pages * pg_size
    return info


def _disk_free(path: str) -> str:
    try:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize
    except Exception:
        return "not available"


def _cpu_info() -> dict:
    info = {"model": "not available", "physical_cores": "not available",
            "logical_cores": "not available"}
    info["logical_cores"] = str(os.cpu_count() or "not available")
    if sys.platform == "darwin":
        info["model"] = _try_cmd(["sysctl", "-n", "machdep.cpu.brand_string"])
        pc = _try_cmd(["sysctl", "-n", "hw.physicalcpu"])
        if pc and pc != "not available":
            info["physical_cores"] = pc
    elif sys.platform.startswith("linux"):
        info["model"] = _read_file("/proc/cpuinfo")
        if info["model"] != "not available":
            for line in info["model"].splitlines():
                if line.lower().startswith("model name"):
                    info["model"] = line.split(":", 1)[1].strip()
                    break
        nproc = _try_cmd(["nproc"])
        if nproc and nproc != "not available":
            info["physical_cores"] = nproc
    return info


def _llama_binary() -> str:
    for name in ("llama-completion", "llama-cli", "llama"):
        found = shutil.which(name)
        if found:
            return found
    return "not detected"


def _fts5_available() -> bool:
    try:
        c = sqlite3.connect(":memory:")
        c.execute("CREATE VIRTUAL TABLE t USING fts5(body)")
        c.close()
        return True
    except Exception:
        return False


def _retrieval_status() -> dict:
    from pathlib import Path as P
    sys.path.insert(0, str(REPO_ROOT))
    db_path = REPO_ROOT / "data" / "afrekaos_fts.sqlite"
    status = {"exists": db_path.is_file(), "documents": "not available"}
    if db_path.is_file():
        try:
            from app import retrieval  # noqa
            s = retrieval.retrieval_summary()
            status["documents"] = s["documents"]
        except Exception:
            status["documents"] = "error reading index"
    return status


def _ubuntu_2204() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    # Check /etc/os-release
    raw = _read_file("/etc/os-release")
    if raw and raw != "not available":
        return "ubuntu" in raw.lower() and ("22.04" in raw)
    return False


def collect() -> dict:
    model_path = REPO_ROOT / "model" / "afrekaos.gguf"
    mem = _memory_info()
    cpu = _cpu_info()
    ret = _retrieval_status()

    return {
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "ubuntu_22_04_detected": _ubuntu_2204(),
        "cpu_model": cpu["model"],
        "physical_cores": cpu["physical_cores"],
        "logical_cores": cpu["logical_cores"],
        "total_memory_bytes": mem["total_bytes"],
        "available_memory_bytes": mem["available_bytes"],
        "disk_free_bytes": _disk_free(str(REPO_ROOT)),
        "model_exists": model_path.is_file(),
        "model_is_symlink": model_path.is_symlink(),
        "model_size_bytes": (model_path.stat().st_size if model_path.exists() else "not available"),
        "llama_binary": _llama_binary(),
        "retrieval_index_exists": ret["exists"],
        "indexed_documents": ret["documents"],
        "sqlite_fts5_available": _fts5_available(),
    }


def _fmt_bytes(n) -> str:
    if isinstance(n, str):
        return n
    if n >= 1073741824:
        return f"{n / 1073741824:.2f} GiB ({n} bytes)"
    if n >= 1048576:
        return f"{n / 1048576:.2f} MiB ({n} bytes)"
    return f"{n} bytes"


def render(d: dict) -> str:
    lines = []
    lines.append("# Target Hardware Profile — AfrekaOS Offline (Task 005C)")
    lines.append("")
    lines.append(f"- **OS:** `{d['os']}`")
    lines.append(f"- **Python:** `{d['python_version']}`")
    lines.append(f"- **Ubuntu 22.04 detected:** {d['ubuntu_22_04_detected']}")
    lines.append(f"- **CPU model:** {d['cpu_model']}")
    lines.append(f"- **Physical cores:** {d['physical_cores']}")
    lines.append(f"- **Logical cores:** {d['logical_cores']}")
    lines.append(f"- **Total memory:** {_fmt_bytes(d['total_memory_bytes'])}")
    lines.append(f"- **Available memory:** {_fmt_bytes(d['available_memory_bytes'])}")
    lines.append(f"- **Disk free (repo):** {_fmt_bytes(d['disk_free_bytes'])}")
    lines.append(f"- **model/afrekaos.gguf exists:** {d['model_exists']}")
    lines.append(f"- **model path is symlink:** {d['model_is_symlink']}")
    lines.append(f"- **Model size:** {_fmt_bytes(d['model_size_bytes'])}")
    lines.append(f"- **llama binary:** {d['llama_binary']}")
    lines.append(f"- **Retrieval index exists:** {d['retrieval_index_exists']}")
    lines.append(f"- **Indexed documents:** {d['indexed_documents']}")
    lines.append(f"- **SQLite FTS5 available:** {d['sqlite_fts5_available']}")
    lines.append("")
    lines.append("> Values are read live from the current machine. 'not available' "
                 "means the value could not be read on this platform — it is not "
                 "fabricated.")
    return "\n".join(lines)


def main() -> int:
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    d = collect()
    OUT_PATH.write_text(render(d), encoding="utf-8")
    # Also print to stdout.
    print(render(d))
    print(f"\nProfile written to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
