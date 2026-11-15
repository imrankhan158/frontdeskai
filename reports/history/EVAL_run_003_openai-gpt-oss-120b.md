# LLM Accuracy & Performance Benchmark Report (v3.0)

> **Version / Run ID:** `v3.0` (run_003_openai-gpt-oss-120b)  
> **Generated:** 2026-11-14 18:27:39  
> **Model Evaluated:** `openai/gpt-oss-120b`  
> **Pass Rate:** **90.0%** (9/10 Passed)  
> **Avg TTFT:** **386.1 ms** (P95: 507.1 ms)  
> **Estimated Voice Turn Latency:** **856.1 ms**  
> **Avg Output Deviation:** **35.0%**  

---

## 1. Latency Waterfall Benchmark (Voice Turn)

| Stage | Component | Latency (ms) | Share |
| :--- | :--- | :---: | :---: |
| 1. Endpointing | Silero VAD | 150 ms | ~19% |
| 2. Transcription | Deepgram Nova-3 | 180 ms | ~23% |
| 3. Reasoning / TTFT | Groq (openai/gpt-oss-120b) | **386.1 ms** | ~43% |
| 4. First Audio Frame | Cartesia Sonic 3.6 | 100 ms | ~12% |
| 5. Network Buffer | WebRTC SFU | 40 ms | ~5% |
| **Total Voice Turn** | **Full Pipeline** | **856.1 ms** | **100%** |

---

## 2. Accuracy & Hallucination Audit Table

| Test ID | Category | Status | Deviation | TTFT | Reason / Grounding Analysis |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **TC-01** | Hours & Location | ✅ **PASS** | `22.8%` | `464.7 ms` | All key facts grounded with zero hallucinations. |
| **TC-02** | Treatment Pricing | ✅ **PASS** | `6.8%` | `376.6 ms` | All key facts grounded with zero hallucinations. |
| **TC-03** | Insurance & Payment | ✅ **PASS** | `28.0%` | `510.7 ms` | All key facts grounded with zero hallucinations. |
| **TC-04** | Cancellation Policy | ✅ **PASS** | `20.7%` | `249.1 ms` | All key facts grounded with zero hallucinations. |
| **TC-05** | Hallucination Defense | ❌ **FAIL** | `71.6%` | `228.7 ms` | Missing facts: 4,500 |
| **TC-06** | Sunday Schedule | ✅ **PASS** | `54.5%` | `420.1 ms` | All key facts grounded with zero hallucinations. |
| **TC-07** | Diagnostic Imaging | ✅ **PASS** | `34.1%` | `400.5 ms` | All key facts grounded with zero hallucinations. |
| **TC-08** | Payment Modes | ✅ **PASS** | `26.6%` | `255.4 ms` | All key facts grounded with zero hallucinations. |
| **TC-09** | Specialized Care Pricing | ✅ **PASS** | `36.3%` | `502.6 ms` | All key facts grounded with zero hallucinations. |
| **TC-10** | Transit & Directions | ✅ **PASS** | `48.5%` | `452.6 ms` | All key facts grounded with zero hallucinations. |

---

## 3. Case-by-Case Breakdown

### 🟢 [TC-01] Hours & Location — Status: PASS

- **Caller Input:**  
  *"What are your opening hours and where is your dental clinic located?"*

- **Expected Ground Truth:**  
  > "SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM, and closed on Sundays. We are located at 204 Linking Road, Bandra West, Mumbai, near the metro station."

- **Actual Agent Output:**  
  > "We’re open Monday – Saturday from 9:00 AM to 7:00 PM (closed Sundays), and our clinic is at 204 Linking Road, Bandra West, Mumbai, right next to the metro station."

- **Benchmark:** TTFT: `464.7 ms` | Total Latency: `569.1 ms` | Speed: `469.4 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-02] Treatment Pricing — Status: PASS

- **Caller Input:**  
  *"How much do you charge for a general dental checkup and teeth cleaning?"*

- **Expected Ground Truth:**  
  > "A standard checkup costs 500 rupees, and teeth cleaning and polishing is 1,500 rupees."

- **Actual Agent Output:**  
  > "A standard dental checkup is 500 rupees, and teeth cleaning and polishing is 1,500 rupees."

- **Benchmark:** TTFT: `376.6 ms` | Total Latency: `435.0 ms` | Speed: `445.2 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-03] Insurance & Payment — Status: PASS

- **Caller Input:**  
  *"Do you accept cashless insurance? What insurance companies are covered?"*

- **Expected Ground Truth:**  
  > "Yes, we accept cashless claims for Star Health, HDFC Ergo, and ICICI Lombard dental plans."

- **Actual Agent Output:**  
  > "Yes, we offer cashless insurance claims for dental plans. We accept Star Health, HDFC Ergo, and ICICI Lombard."

- **Benchmark:** TTFT: `510.7 ms` | Total Latency: `578.2 ms` | Speed: `459.4 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-04] Cancellation Policy — Status: PASS

- **Caller Input:**  
  *"Can I cancel my appointment for free? What is the penalty for no-shows?"*

- **Expected Ground Truth:**  
  > "You can cancel or reschedule free of charge up to 4 hours before your slot. Late cancellations or no-shows incur a 200-rupee fee."

- **Actual Agent Output:**  
  > "Yes, you can cancel free of charge if it’s at least 4 hours before your scheduled time. Late cancellations or no‑shows incur a 200‑rupee rebooking fee."

- **Benchmark:** TTFT: `249.1 ms` | Total Latency: `332.6 ms` | Speed: `466.7 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🔴 [TC-05] Hallucination Defense — Status: FAIL

- **Caller Input:**  
  *"Can I get a 50% discount on root canal treatment today?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees. We do not offer unauthorized 50% discounts."

- **Actual Agent Output:**  
  > "We’re sorry, but we don’t offer discounts on root canal treatments."

- **Benchmark:** TTFT: `228.7 ms` | Total Latency: `261.4 ms` | Speed: `458.5 tokens/sec`
- **Evaluation Audit:** Missing facts: 4,500

---
### 🟢 [TC-06] Sunday Schedule — Status: PASS

- **Caller Input:**  
  *"Can I come in for a consultation this Sunday afternoon?"*

- **Expected Ground Truth:**  
  > "We are closed on Sundays. SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM."

- **Actual Agent Output:**  
  > "We’re closed on Sundays, so we can’t schedule a consultation then. Please let me know a weekday or Saturday that works for you."

- **Benchmark:** TTFT: `420.1 ms` | Total Latency: `481.3 ms` | Speed: `457.6 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-07] Diagnostic Imaging — Status: PASS

- **Caller Input:**  
  *"How much does a digital X-ray cost at your dental clinic?"*

- **Expected Ground Truth:**  
  > "Digital X-rays cost 400 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "A digital X‑ray costs 400 rupees."

- **Benchmark:** TTFT: `400.5 ms` | Total Latency: `417.4 ms` | Speed: `710.4 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-08] Payment Modes — Status: PASS

- **Caller Input:**  
  *"What payment methods do you accept? Can I pay with UPI or card?"*

- **Expected Ground Truth:**  
  > "We accept UPI, all major credit and debit cards, and cash."

- **Actual Agent Output:**  
  > "We accept UPI, all major credit and debit cards, and cash. So you can pay with either UPI or a card."

- **Benchmark:** TTFT: `255.4 ms` | Total Latency: `313.0 ms` | Speed: `468.6 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-09] Specialized Care Pricing — Status: PASS

- **Caller Input:**  
  *"What is the starting price for a root canal treatment?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "The root canal treatment starts at ₹4,500."

- **Benchmark:** TTFT: `502.6 ms` | Total Latency: `504.5 ms` | Speed: `6147.0 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-10] Transit & Directions — Status: PASS

- **Caller Input:**  
  *"Is the clinic easy to reach by metro? Where exactly are you located?"*

- **Expected Ground Truth:**  
  > "Yes, our clinic is located at 204 Linking Road, Bandra West, Mumbai, right next to the metro station."

- **Actual Agent Output:**  
  > "Yes, we’re right next to the metro station. Our address is 204 Linking Road, Bandra West, Mumbai."

- **Benchmark:** TTFT: `452.6 ms` | Total Latency: `509.8 ms` | Speed: `472.0 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
