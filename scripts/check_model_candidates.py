#!/usr/bin/env python3
"""Candidate checker for the AfrekaOS Offline model bake-off.

Validates model.candidates.json against the bake-off contract:
  - exactly three candidates
  - primary   = qwen3-1.7b-q4-k-m
  - secondary = qwen3-4b-q4-k-m
  - control   = granite-4.1-3b-q4-k-m
  - every local_candidate_path is under model/candidates/
  - canonical_winning_model_path == model/afrekaos.gguf
  - prohibited_use boundaries present

Standard library only. Does not require model files, llama.cpp, or internet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANDIDATES_PATH = REPO_ROOT / "model.candidates.json"

EXPECTED_PRIMARY = "qwen3-1.7b-q4-k-m"
EXPECTED_SECONDARY = "qwen3-4b-q4-k-m"
EXPECTED_CONTROL = "granite-4.1-3b-q4-k-m"
EXPECTED_COUNT = 3
EXPECTED_WINNER_PATH = "model/afrekaos.gguf"

ROLE_BY_ID = {
    EXPECTED_PRIMARY: "primary_speed_candidate",
    EXPECTED_SECONDARY: "secondary_reasoning_candidate",
    EXPECTED_CONTROL: "control_candidate",
}


def _fail(msg: str) -> None:
    print(f"CANDIDATES CHECK FAILED: {msg}", file=sys.stderr)


def load_candidates(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"model.candidates.json not found at {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("model.candidates.json top-level must be a JSON object")
    return data


def check(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("product") != "AfrekaOS Offline":
        errors.append(f"'product' must be 'AfrekaOS Offline' (got {data.get('product')!r})")

    if data.get("selection_mode") != "qwen_first_bakeoff":
        errors.append(
            f"'selection_mode' must be 'qwen_first_bakeoff' "
            f"(got {data.get('selection_mode')!r})"
        )

    if data.get("canonical_winning_model_path") != EXPECTED_WINNER_PATH:
        errors.append(
            f"'canonical_winning_model_path' must be {EXPECTED_WINNER_PATH!r} "
            f"(got {data.get('canonical_winning_model_path')!r})"
        )

    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        errors.append("'candidates' must be a list")
        return errors

    if len(candidates) != EXPECTED_COUNT:
        errors.append(
            f"'candidates' must contain exactly {EXPECTED_COUNT} candidates "
            f"(got {len(candidates)})"
        )

    by_id: dict[str, dict] = {}
    for i, c in enumerate(candidates):
        if not isinstance(c, dict):
            errors.append(f"candidates[{i}] must be an object")
            continue
        cid = c.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"candidates[{i}].id must be a non-empty string")
            continue
        by_id[cid] = c

    # Required ids and roles
    for cid, expected_role in ROLE_BY_ID.items():
        if cid not in by_id:
            errors.append(f"missing required candidate: {cid}")
            continue
        c = by_id[cid]
        role = c.get("role")
        if role != expected_role:
            errors.append(
                f"candidate {cid!r} role must be {expected_role!r} (got {role!r})"
            )

    # Required fields + local path location for every candidate
    required_fields = ("id", "repo", "quantization", "format", "role",
                       "local_candidate_path", "selection_reason")
    for c in candidates:
        if not isinstance(c, dict):
            continue
        cid = c.get("id", "<unknown>")
        for f in required_fields:
            val = c.get(f)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"candidate {cid!r} missing non-empty field {f!r}")
        lcp = c.get("local_candidate_path", "")
        if isinstance(lcp, str) and lcp:
            norm = lcp.replace("\\", "/")
            if not norm.startswith("model/candidates/"):
                errors.append(
                    f"candidate {cid!r} local_candidate_path must be under "
                    f"'model/candidates/' (got {lcp!r})"
                )
            if not norm.endswith(".gguf"):
                errors.append(
                    f"candidate {cid!r} local_candidate_path must end with .gguf "
                    f"(got {lcp!r})"
                )
        if c.get("format") != "GGUF":
            errors.append(f"candidate {cid!r} format must be 'GGUF'")

    # prohibited_use boundaries
    prohibited = data.get("prohibited_use")
    if not isinstance(prohibited, list) or not prohibited:
        errors.append("'prohibited_use' must be a non-empty list")
    else:
        required_tokens = ("cloud", "customer", "banking", "payroll", "tax", "erp")
        joined = " ".join(prohibited).lower()
        for tok in required_tokens:
            if tok not in joined:
                errors.append(f"'prohibited_use' missing boundary token '{tok}'")

    return errors


def main() -> int:
    try:
        data = load_candidates(CANDIDATES_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        _fail(str(exc))
        return 2

    errors = check(data)
    if errors:
        for e in errors:
            _fail(e)
        print(f"\n{len(errors)} candidate contract violation(s).", file=sys.stderr)
        return 1

    candidates = data.get("candidates", [])
    print("CANDIDATES CHECK PASSED")
    print(f"  product        : {data.get('product')}")
    print(f"  selection_mode : {data.get('selection_mode')}")
    print(f"  winner path    : {data.get('canonical_winning_model_path')}")
    print(f"  candidates     : {len(candidates)} (expected {EXPECTED_COUNT})")
    for c in candidates:
        exists = (REPO_ROOT / c["local_candidate_path"]).is_file()
        print(
            f"    - {c['id']:<22} [{c['role']}] "
            f"local={'present' if exists else 'missing'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
