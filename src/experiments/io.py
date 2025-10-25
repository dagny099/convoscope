"""
Lightweight IO helpers for model comparison runs.

Responsibilities:
- Append JSONL records safely
- Ensure directories exist
- Load prompt sets from YAML (with tag filtering)
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


EXPERIMENTS_DIR = Path("experiments")
RESULTS_PATH = EXPERIMENTS_DIR / "results.jsonl"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_prompt_set(path: Path, include_tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Load a prompt set YAML file and optionally filter prompts by tags.
    Expected schema:
      version: 1
      metadata: {...}
      combos: [{provider, model}, ...]
      prompts: [{id, text, tags: [...]}, ...]
    """
    data = load_yaml(path)
    prompts = data.get("prompts", [])
    if include_tags:
        include = set([t.strip() for t in include_tags])
        prompts = [p for p in prompts if include.intersection(set(p.get("tags", [])))]
    data["prompts"] = prompts
    return data


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read a JSONL file into a list of dicts. Skips malformed lines."""
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def build_prompt_index(path: Path) -> Dict[str, Dict[str, Any]]:
    """Return a mapping from sha256(text) -> {id, text, tags} for prompt sets."""
    index: Dict[str, Dict[str, Any]] = {}
    data = load_yaml(path) if path.exists() else {}
    for p in data.get("prompts", []):
        text = p.get("text", "")
        h = sha256_text(text)
        index[h] = {"id": p.get("id"), "text": text, "tags": p.get("tags", [])}
    return index
