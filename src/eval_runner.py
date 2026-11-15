import asyncio
import difflib
import json
import logging
import os
import re
import time
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from src.config import (
    DATASET_PATH,
    REPORT_JSON_PATH,
    REPORT_MD_PATH,
    EVAL_HISTORY_PATH,
    REPORTS_HISTORY_DIR,
    USD_TO_INR,
    get_faq_content,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("evals")

FAQ_CONTENT = get_faq_content()


def normalize_text(text: str) -> str:
    """Normalize unicode spaces, hyphens, curly quotes, and whitespaces for robust matching."""
    norm = unicodedata.normalize("NFKD", text)
    norm = norm.replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    norm = norm.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    norm = re.sub(r"\s+", " ", norm)
    return norm.strip()


def compute_deviation(expected: str, actual: str) -> float:
    """Calculate stylistic & token deviation percentage (0.0% = identical, 100% = completely different)."""
    norm_exp = normalize_text(expected.lower())
    norm_act = normalize_text(actual.lower())
    matcher = difflib.SequenceMatcher(None, norm_exp, norm_act)
    similarity = matcher.ratio()
    return round((1.0 - similarity) * 100.0, 1)


def calc_percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    k = (len(sorted_d) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c < len(sorted_d):
        return round(sorted_d[f] + (k - f) * (sorted_d[c] - sorted_d[f]), 1)
    return round(sorted_d[f], 1)


async def run_single_test_case(tc: Dict[str, Any], llm_instance: Any) -> Dict[str, Any]:
    """Execute a single test case against the LLM, capturing both correctness and benchmark metrics."""
    from livekit.agents.llm import ChatContext

    question = tc["input"]
    expected = tc["expected_output"]
    required_facts = tc.get("required_facts", [])
    prohibited_facts = tc.get("prohibited_facts", [])

    system_prompt = (
        "You are a concise, polite front-desk assistant for SmileCare Dental Clinic. "
        "Use the following clinic policy to answer accurately in under two short sentences. "
        "Never invent policies, prices, or discounts.\n\n"
        f"CLINIC POLICY REFERENCE:\n{FAQ_CONTENT}"
    )

    ctx = ChatContext()
    ctx.add_message(role="system", content=system_prompt)
    ctx.add_message(role="user", content=question)

    t0 = time.perf_counter()
    first_token_time = None
    actual_text = ""
    token_count = 0

    stream = llm_instance.chat(chat_ctx=ctx)
    async for chunk in stream:
        delta = chunk.delta.content if (chunk.delta and chunk.delta.content) else ""
        if delta:
            if first_token_time is None:
                first_token_time = time.perf_counter()
            token_count += 1
            actual_text += delta
    t_end = time.perf_counter()

    ttft_ms = round((first_token_time - t0) * 1000, 1) if first_token_time else 0.0
    total_latency_ms = round((t_end - t0) * 1000, 1)
    gen_time = (t_end - first_token_time) if first_token_time else 0.0
    tokens_per_sec = round(token_count / gen_time, 1) if gen_time > 0 else 0.0

    clean_actual = actual_text.strip()
    norm_actual = normalize_text(clean_actual.lower())

    # Accuracy & Fact Recall Verification
    missing_facts = [
        fact for fact in required_facts if normalize_text(fact.lower()) not in norm_actual
    ]
    detected_prohibited = [
        fact for fact in prohibited_facts if normalize_text(fact.lower()) in norm_actual
    ]

    deviation_pct = compute_deviation(expected, clean_actual)

    # Determine PASS / FAIL
    status = "PASS"
    reasons: List[str] = []

    if missing_facts:
        status = "FAIL"
        reasons.append(f"Missing facts: {', '.join(missing_facts)}")

    if detected_prohibited:
        status = "FAIL"
        reasons.append(f"Hallucination detected: {', '.join(detected_prohibited)}")

    if not reasons:
        reasons.append("All key facts grounded with zero hallucinations.")

    return {
        "id": tc["id"],
        "category": tc.get("category", "General"),
        "input": question,
        "expected_output": expected,
        "actual_output": clean_actual,
        "deviation_pct": deviation_pct,
        "ttft_ms": ttft_ms,
        "total_latency_ms": total_latency_ms,
        "token_count": token_count,
        "tokens_per_sec": tokens_per_sec,
        "missing_facts": missing_facts,
        "hallucinations": detected_prohibited,
        "status": status,
        "reason": "; ".join(reasons),
    }


def generate_eval_markdown(
    results: List[Dict[str, Any]],
    model_name: str,
    benchmark_summary: Dict[str, Any],
    version: str = "v1.0",
    run_id: str = "run_001",
) -> str:
    """Generate comprehensive report covering both accuracy and benchmark performance."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    pass_rate = round((passed / total) * 100.0, 1) if total else 0.0
    avg_dev = round(sum(r["deviation_pct"] for r in results) / total, 1) if total else 0.0
    avg_ttft = benchmark_summary.get("avg_ttft_ms", 0.0)
    turn_latency = benchmark_summary.get("voice_turn_latency_ms", 0.0)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# LLM Accuracy & Performance Benchmark Report ({version})

> **Version / Run ID:** `{version}` ({run_id})  
> **Generated:** {timestamp}  
> **Model Evaluated:** `{model_name}`  
> **Pass Rate:** **{pass_rate}%** ({passed}/{total} Passed)  
> **Avg TTFT:** **{avg_ttft} ms** (P95: {benchmark_summary.get('p95_ttft_ms', 0)} ms)  
> **Estimated Voice Turn Latency:** **{turn_latency} ms**  
> **Avg Output Deviation:** **{avg_dev}%**  

---

## 1. Latency Waterfall Benchmark (Voice Turn)

| Stage | Component | Latency (ms) | Share |
| :--- | :--- | :---: | :---: |
| 1. Endpointing | Silero VAD | 150 ms | ~19% |
| 2. Transcription | Deepgram Nova-3 | 180 ms | ~23% |
| 3. Reasoning / TTFT | Groq ({model_name}) | **{avg_ttft} ms** | ~43% |
| 4. First Audio Frame | Cartesia Sonic 3.6 | 100 ms | ~12% |
| 5. Network Buffer | WebRTC SFU | 40 ms | ~5% |
| **Total Voice Turn** | **Full Pipeline** | **{turn_latency} ms** | **100%** |

---

## 2. Accuracy & Hallucination Audit Table

| Test ID | Category | Status | Deviation | TTFT | Reason / Grounding Analysis |
| :--- | :--- | :---: | :---: | :---: | :--- |
"""
    for r in results:
        status_badge = "✅ **PASS**" if r["status"] == "PASS" else "❌ **FAIL**"
        md += f"| **{r['id']}** | {r['category']} | {status_badge} | `{r['deviation_pct']}%` | `{r['ttft_ms']} ms` | {r['reason']} |\n"

    md += """
---

## 3. Case-by-Case Breakdown

"""
    for r in results:
        status_icon = "🟢" if r["status"] == "PASS" else "🔴"
        md += f"""### {status_icon} [{r['id']}] {r['category']} — Status: {r['status']}

- **Caller Input:**  
  *"{r['input']}"*

- **Expected Ground Truth:**  
  > "{r['expected_output']}"

- **Actual Agent Output:**  
  > "{r['actual_output']}"

- **Benchmark:** TTFT: `{r['ttft_ms']} ms` | Total Latency: `{r['total_latency_ms']} ms` | Speed: `{r.get('tokens_per_sec', 0)} tokens/sec`
- **Evaluation Audit:** {r['reason']}

---
"""
    return md


async def run_all_evals(model_name: Optional[str] = None) -> Dict[str, Any]:
    """Execute all test cases in eval_dataset.json and produce unified accuracy + benchmark report."""
    from livekit.agents.utils import http_context
    from livekit.plugins import groq

    if not model_name:
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    logger.info(f"=== STARTING EVALUATION & BENCHMARK SUITE [{model_name}] ===")
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at {DATASET_PATH}")

    test_cases: List[Dict[str, Any]] = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    results: List[Dict[str, Any]] = []

    async with http_context.open():
        groq_models = {
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "allam-2-7b",
        }
        if model_name in groq_models or "/" not in model_name:
            logger.info(f"Using Groq LPU provider for model: {model_name}")
            llm_instance = groq.LLM(model=model_name)
        else:
            from livekit.plugins import openai

            clean_model = model_name.replace("openrouter/", "")
            logger.info(f"Using OpenRouter provider for model: {clean_model}")
            llm_instance = openai.LLM(
                model=clean_model,
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )

        try:
            for tc in test_cases:
                logger.info(f"Running [{tc['id']}] {tc.get('category')}...")
                res = await run_single_test_case(tc, llm_instance)
                results.append(res)
                logger.info(f"  -> [{res['id']}] {res['status']} (Dev: {res['deviation_pct']}%, TTFT: {res['ttft_ms']}ms)")
                await asyncio.sleep(0.3)  # Gentle spacing
        except Exception as e:
            err_str = str(e)
            if "Key limit exceeded" in err_str or "403" in err_str:
                raise RuntimeError(
                    "OpenRouter API key limit reached ($0.00 balance). "
                    "Please add credits at openrouter.ai or use the free Groq models (GPT-OSS 20B / Qwen 27B / GPT-OSS 120B)."
                ) from e
            if "no longer available" in err_str or "404" in err_str:
                raise RuntimeError(
                    f"Model '{model_name}' is no longer available on OpenRouter. Please select an active model."
                ) from e
            raise RuntimeError(f"Evaluation error for model '{model_name}': {err_str}") from e

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    pass_rate = round((passed / total) * 100.0, 1) if total else 0.0
    avg_dev = round(sum(r["deviation_pct"] for r in results) / total, 1) if total else 0.0

    # Benchmark Analytics
    ttft_samples = [r["ttft_ms"] for r in results if r["ttft_ms"] > 0]
    avg_ttft = round(sum(ttft_samples) / len(ttft_samples), 1) if ttft_samples else 0.0
    p95_ttft = calc_percentile(ttft_samples, 95)
    min_ttft = min(ttft_samples) if ttft_samples else 0.0
    max_ttft = max(ttft_samples) if ttft_samples else 0.0
    avg_latency = round(sum(r["total_latency_ms"] for r in results) / total, 1) if total else 0.0
    avg_tps = round(sum(r.get("tokens_per_sec", 0.0) for r in results) / total, 1) if total else 0.0

    # End-to-End Latency Waterfall
    estimated_turn_latency_ms = round(150.0 + 180.0 + avg_ttft + 100.0 + 40.0, 1)

    benchmark_summary = {
        "model": model_name,
        "avg_ttft_ms": avg_ttft,
        "p95_ttft_ms": p95_ttft,
        "min_ttft_ms": min_ttft,
        "max_ttft_ms": max_ttft,
        "avg_latency_ms": avg_latency,
        "avg_tokens_per_sec": avg_tps,
        "voice_turn_latency_ms": estimated_turn_latency_ms,
        "waterfall": {
            "vad_ms": 150.0,
            "stt_ms": 180.0,
            "llm_ttft_ms": avg_ttft,
            "tts_ttfa_ms": 100.0,
            "webrtc_ms": 40.0,
        },
        "economics": {
            "cost_per_minute_usd": 0.015,
            "cost_per_minute_inr": round(0.015 * USD_TO_INR, 2),
        },
    }

    # Load version history
    history = []
    if EVAL_HISTORY_PATH.exists():
        try:
            history = json.loads(EVAL_HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            history = []

    run_number = len(history) + 1
    version_tag = f"v{run_number}.0"
    clean_model_slug = re.sub(r"[^a-zA-Z0-9_\-\.]", "-", model_name)
    run_id = f"run_{run_number:03d}_{clean_model_slug}"

    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": pass_rate,
        "avg_deviation_pct": avg_dev,
        "avg_ttft_ms": avg_ttft,
        "voice_turn_latency_ms": estimated_turn_latency_ms,
    }

    history_entry = {
        "run_id": run_id,
        "version": version_tag,
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "summary": summary,
    }
    history.append(history_entry)
    EVAL_HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    report_payload = {
        "run_id": run_id,
        "version": version_tag,
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "summary": summary,
        "benchmark": benchmark_summary,
        "results": results,
        "history": history,
    }

    # Save Unified JSON report
    REPORT_JSON_PATH.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    # Save Versioned JSON snapshot for historical inspection
    (REPORTS_HISTORY_DIR / f"{run_id}.json").write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    # Generate Markdown Report & Versioned Snapshot
    md_content = generate_eval_markdown(
        results, model_name, benchmark_summary, version=version_tag, run_id=run_id
    )
    REPORT_MD_PATH.write_text(md_content, encoding="utf-8")
    snapshot_path = REPORTS_HISTORY_DIR / f"EVAL_{run_id}.md"
    snapshot_path.write_text(md_content, encoding="utf-8")
    logger.info(f"Saved versioned report snapshot: {snapshot_path.name}")
    logger.info(f"Generated unified report: {REPORT_MD_PATH.name}")

    print("\n" + "=" * 65)
    print(f"EVALUATION & BENCHMARK COMPLETED [{version_tag} | {model_name}]:")
    print(f"  * Run ID:              {run_id}")
    print(f"  * Tests Run:           {total}")
    print(f"  * Passed:              {passed} / {total} ({pass_rate}%)")
    print(f"  * Avg TTFT:            {avg_ttft} ms (P95: {p95_ttft} ms)")
    print(f"  * Voice Turn Latency:  {estimated_turn_latency_ms} ms")
    print(f"  * Avg Deviation:       {avg_dev}%")
    print(f"  * Total History Runs:  {len(history)}")
    print("=" * 65 + "\n")

    return report_payload


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FrontDeskAI Unified Evaluation & Benchmark Suite")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model ID to evaluate (e.g. openai/gpt-oss-20b, llama-3.3-70b-versatile)",
    )
    args = parser.parse_args()
    asyncio.run(run_all_evals(model_name=args.model))
