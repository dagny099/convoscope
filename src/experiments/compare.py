"""
Core comparison runner.

Collects responses from multiple provider/model pairs for a single prompt
and returns structured results with blind labels for scoring.

Design notes:
- Uses existing LLMService to avoid duplicating provider logic.
- Measures wall-clock latency; tokens and cost are estimated.
- Keeps order randomizable for blind scoring; stores mapping.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple

from .metrics import estimate_tokens, estimate_cost_usd, now_ms


BLIND_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def collect_comparisons(
    service,
    prompt_text: str,
    combos: List[Tuple[str, str]],
    temperature: float = 0.7,
    blind: bool = True,
    priming_text: str | None = None,
) -> Dict[str, Any]:
    """
    Run a prompt against multiple provider/model pairs and return results.

    Args:
        service: LLMService instance
        prompt_text: user-provided question/prompt
        combos: list of (provider, model)
        temperature: sampling temperature
        blind: if True, results are labeled A/B/C with identities hidden
        priming_text: optional system prompt

    Returns:
        dict with keys: results (list), mapping (label->(provider,model)), blind(bool)
    """
    messages = []
    if priming_text:
        messages.append({"role": "system", "content": priming_text})
    messages.append({"role": "user", "content": prompt_text})

    items: List[Dict[str, Any]] = []
    # Sequential for simplicity (2–4 models is fine). Can be parallelized later.
    for provider, model in combos:
        start = now_ms()
        try:
            text = service.get_completion(provider, model, messages, temperature=temperature) or ""
            status = "ok"
            error = None
        except Exception as e:
            text = ""
            status = "error"
            error = str(e)
        end = now_ms()

        # Token + cost estimates: transparent heuristics
        input_tokens = estimate_tokens(" ".join(m.get("content", "") for m in messages))
        output_tokens = estimate_tokens(text)
        cost = estimate_cost_usd(provider, model, input_tokens, output_tokens)

        items.append({
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "latency_ms": end - start,
            "input_tokens_est": input_tokens,
            "output_tokens_est": output_tokens,
            "estimated_cost_usd": cost,
            "response_text": text,
            "status": status,
            "error": error,
        })

    # Randomize display order for blind scoring
    order = list(range(len(items)))
    random.shuffle(order)
    ordered = [items[i] for i in order]

    label_map: Dict[str, Dict[str, Any]] = {}
    for idx, item in enumerate(ordered):
        label = BLIND_LABELS[idx]
        item["blind_label"] = label
        label_map[label] = {"provider": item["provider"], "model": item["model"]}

    return {
        "results": ordered,
        "mapping": label_map,
        "blind": bool(blind),
        "prompt_text": prompt_text,
    }
