"""
Metrics helpers for comparison runs.

We aim for transparency:
- Latency is wall-clock (ms) around the provider call.
- Tokens are estimated when vendor usage is unavailable (char/4 heuristic).
- Cost is estimated from a static pricing table in experiments/pricing.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict
import time

from .io import load_yaml


PRICING_PATH = Path("experiments/pricing.yaml")


def now_ms() -> int:
    return int(time.perf_counter() * 1000)


def estimate_tokens(text: str) -> int:
    # Simple heuristic documented openly; acceptable for relative comparison.
    if not text:
        return 0
    # Clamp at minimum 1 if non-empty
    return max(1, round(len(text) / 4))


def load_pricing() -> Dict[str, Dict[str, float]]:
    data = load_yaml(PRICING_PATH)
    return data.get("models", {})


def compose_model_key(provider: str, model: str) -> str:
    # Use the same key style as pricing.yaml: provider/model
    if provider == "google":
        # pricing.yaml uses gemini/ prefix to match our service logic
        return f"gemini/{model}"
    return f"{provider}/{model}"


def estimate_cost_usd(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = load_pricing()
    key = compose_model_key(provider, model)
    info = pricing.get(key)
    if not info:
        return 0.0
    in_rate = float(info.get("input_per_1k", 0.0)) / 1000.0
    out_rate = float(info.get("output_per_1k", 0.0)) / 1000.0
    return round(input_tokens * in_rate + output_tokens * out_rate, 6)
