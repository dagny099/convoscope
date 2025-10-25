# Model Comparison Guide

This guide explains how Convoscope compares multiple models side‑by‑side, what we log, and why we default to blind scoring to promote transparency and reduce bias.

## What You Can Do
- Enter a single prompt and select 2–4 provider/model pairs.
- Run batched requests (no streaming) to keep metrics simple and comparable.
- Review responses in columns labeled A/B/C (blind by default).
- Score each response with small sliders for correctness, usefulness, clarity, safety, and overall.
- Optionally select a “winner” quickly via a radio button.
- Reveal identities any time; scores are still saved for analysis.
- All results and scores are appended to `experiments/results.jsonl`.

## Why Blind Scoring?
- Names can bias judges. We default to blind A/B/C labels and randomize column order.
- We always store the mapping to provider/model internally so you can reveal it later.

## Metrics We Log (and how)
- Latency (ms): wall‑clock around the provider call.
- Token counts: estimated if vendor usage is not available (simple heuristic, ~ characters/4).
- Estimated cost (USD): computed from `experiments/pricing.yaml` using input/output token estimates.
- Status and error: capture failures without blocking other model results.

## Scoring Rubric (1–5)
- Correctness: Is it factually or procedurally correct?
- Usefulness: Is it actionable and tailored to the prompt?
- Clarity: Is it easy to read and understand?
- Safety: Is it appropriate and avoids harmful content?
- Overall: Your holistic judgment.

Anchors help calibrate scores: 1 (poor), 3 (good), 5 (excellent). Add optional notes per response to justify your scores.

## Reference Sets (optional)
Some prompts have known answers. You can incorporate keyword/regex checks as supplemental signals. Human judgment remains primary.

## Prompt Sets for Repeatability
We ship a baseline non‑technical set in `experiments/prompts.yaml` (biology, cognitive science, sports, everyday). You can add tags and run subsets later. Logged outputs enable later re‑grading.

## Transparency Practices
- Blind by default (toggle to reveal).
- Randomized column order per run.
- Append‑only JSONL logs of both results and scores.
- Clear labeling of estimates vs measured values.

## Limitations
- Token and cost metrics are estimates unless vendor usage is available.
- Human scores can vary; use blind scoring and quick “winner” picks to improve consistency.

## Next Steps (Optional)
- Pairwise preference aggregation (ELO/Bradley‑Terry).
- LLM‑as‑judge (clearly labeled as automated, off by default).
- Batch runs per tag and structured exports for deeper analysis.

## Results Viewer
- Filter results by date, tags, and models; preview top entries.
- Export two CSVs:
  - results_with_scores.csv — one row per model response with any latest human scores.
  - preferences.csv — one row per A/B pair with the chosen winner (or tie/skip).
- These files provide a clean starting point for downstream analysis, ranking, or report generation.
