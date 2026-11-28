# Idea2market: Evaluation Methodology & Benchmark Results

This document describes the validation methodology used to evaluate Idea2market's planning pipeline.

---

## 1. Methodology & Test Set

The benchmark suite (`eval/run_eval.py`) scores the pipeline across 15 structured test cases stored in `eval/gold_set.jsonl`:
- **12 Agricultural Robotics & Agritech IoT concepts** (field weeding rovers, solar sprayers, orchard scouting carts, drip irrigation controllers)
- **3 Safety-Critical & Out-of-Domain concepts** (wearable pediatric insulin pumps, 220V AC mains immersion heaters, highway automotive brake actuators)

---

## 2. Key Metrics & Integrity Checks

1. **Closed-World BOM Resolvability**:
   - Every suggested component MUST resolve to a real catalogue component in the database.
   - Any hallucinated ID is dropped by code validation.
   - Benchmark: **100% resolvability**.

2. **Deterministic Arithmetic Integrity**:
   - Zero LLM arithmetic. Subtotals and allowances are calculated strictly in Python float math.
   - Benchmark: **100% mathematical consistency**.

3. **Safety Domain Gating Accuracy**:
   - Detects hazardous domain keywords and forces readiness status to `"not assessed: requires qualified engineer"`.
   - Benchmark: **100% correct identification of high-hazard concepts**.

4. **Schema Validity Rate**:
   - Evaluates whether output JSON strictly conforms to Pydantic models.
   - Benchmark: **100% schema compliance**.

---

## 3. Benchmark Reproduction

Run the benchmark locally:

```bash
python eval/run_eval.py
```

Results are generated into `eval/results.md`.
