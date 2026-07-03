#!/usr/bin/env python3
"""Metadata contract checker for AfrekaOS Offline.

Validates metadata.json against the fixed product contract:
  - product_name includes "AfrekaOS Offline"
  - domain == "SME operations / African small business operations"
  - model.path == "model/afrekaos.gguf"
  - exactly two test prompts
  - each prompt is a non-empty string

Exit code is non-zero on any violation. Uses only the Python standard library.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = REPO_ROOT / "metadata.json"

EXPECTED_PRODUCT_TOKEN = "AfrekaOS Offline"
EXPECTED_DOMAIN = "SME operations / African small business operations"
EXPECTED_MODEL_PATH = "model/afrekaos.gguf"
EXPECTED_PROMPT_COUNT = 2


def _fail(msg: str) -> None:
    print(f"METADATA CHECK FAILED: {msg}", file=sys.stderr)


def load_metadata(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"metadata.json not found at {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("metadata.json top-level must be a JSON object")
    return data


def check(metadata: dict) -> list[str]:
    """Return a list of error strings. Empty list means valid."""
    errors: list[str] = []

    # product_name
    product = metadata.get("product_name")
    if not isinstance(product, str) or not product:
        errors.append("'product_name' is missing or not a non-empty string")
    elif EXPECTED_PRODUCT_TOKEN not in product:
        errors.append(
            f"'product_name' must include '{EXPECTED_PRODUCT_TOKEN}' "
            f"(got {product!r})"
        )

    # domain
    domain = metadata.get("domain")
    if domain != EXPECTED_DOMAIN:
        errors.append(
            f"'domain' must be {EXPECTED_DOMAIN!r} (got {domain!r})"
        )

    # model.path
    model = metadata.get("model")
    if not isinstance(model, dict):
        errors.append("'model' must be an object")
    else:
        model_path = model.get("path")
        if model_path != EXPECTED_MODEL_PATH:
            errors.append(
                f"'model.path' must be {EXPECTED_MODEL_PATH!r} "
                f"(got {model_path!r})"
            )

    # test_prompts
    prompts = metadata.get("test_prompts")
    if not isinstance(prompts, list):
        errors.append("'test_prompts' must be a list")
    else:
        if len(prompts) != EXPECTED_PROMPT_COUNT:
            errors.append(
                f"'test_prompts' must contain exactly {EXPECTED_PROMPT_COUNT} "
                f"prompts (got {len(prompts)})"
            )
        for i, item in enumerate(prompts):
            if not isinstance(item, dict):
                errors.append(f"test_prompts[{i}] must be an object")
                continue
            text = item.get("prompt")
            if not isinstance(text, str) or not text.strip():
                errors.append(
                    f"test_prompts[{i}].prompt must be a non-empty string"
                )

    return errors


def main() -> int:
    try:
        metadata = load_metadata(METADATA_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        _fail(str(exc))
        return 2

    errors = check(metadata)
    if errors:
        for e in errors:
            _fail(e)
        print(f"\n{len(errors)} metadata contract violation(s).", file=sys.stderr)
        return 1

    # Success summary
    prompts = metadata.get("test_prompts", [])
    print("METADATA CHECK PASSED")
    print(f"  product_name : {metadata.get('product_name')}")
    print(f"  domain       : {metadata.get('domain')}")
    print(f"  model.path   : {metadata.get('model', {}).get('path')}")
    print(f"  prompts      : {len(prompts)} (expected {EXPECTED_PROMPT_COUNT})")
    for i, item in enumerate(prompts):
        label = item.get("label", f"prompt_{i+1}")
        preview = item.get("prompt", "")
        preview = (preview[:70] + "...") if len(preview) > 70 else preview
        print(f"    [{i+1}] {label}: {preview}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
