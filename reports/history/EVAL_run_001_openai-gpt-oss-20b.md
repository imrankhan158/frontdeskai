# LLM Accuracy & Performance Benchmark Report (v1.0)

> **Version / Run ID:** `v1.0` (run_001_openai-gpt-oss-20b)  
> **Generated:** 2026-11-14 17:50:34  
> **Model Evaluated:** `openai/gpt-oss-20b`  
> **Pass Rate:** **100.0%** (10/10 Passed)  
> **Avg TTFT:** **1228.2 ms** (P95: 2106.2 ms)  
> **Estimated Voice Turn Latency:** **1698.2 ms**  
> **Avg Output Deviation:** **43.7%**  

---

## 1. Latency Waterfall Benchmark (Voice Turn)

| Stage | Component | Latency (ms) | Share |
| :--- | :--- | :---: | :---: |
| 1. Endpointing | Silero VAD | 150 ms | ~19% |
| 2. Transcription | Deepgram Nova-3 | 180 ms | ~23% |
| 3. Reasoning / TTFT | Groq (openai/gpt-oss-20b) | **1228.2 ms** | ~43% |
| 4. First Audio Frame | Cartesia Sonic 3.6 | 100 ms | ~12% |
| 5. Network Buffer | WebRTC SFU | 40 ms | ~5% |
| **Total Voice Turn** | **Full Pipeline** | **1698.2 ms** | **100%** |

---

## 2. Accuracy & Hallucination Audit Table

| Test ID | Category | Status | Deviation | TTFT | Reason / Grounding Analysis |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **TC-01** | Hours & Location | ✅ **PASS** | `18.6%` | `1048.4 ms` | All key facts grounded with zero hallucinations. |
| **TC-02** | Treatment Pricing | ✅ **PASS** | `14.8%` | `327.2 ms` | All key facts grounded with zero hallucinations. |
| **TC-03** | Insurance & Payment | ✅ **PASS** | `28.6%` | `1921.4 ms` | All key facts grounded with zero hallucinations. |
| **TC-04** | Cancellation Policy | ✅ **PASS** | `78.0%` | `1297.0 ms` | All key facts grounded with zero hallucinations. |
| **TC-05** | Hallucination Defense | ✅ **PASS** | `71.1%` | `1030.2 ms` | All key facts grounded with zero hallucinations. |
| **TC-06** | Sunday Schedule | ✅ **PASS** | `47.3%` | `1837.1 ms` | All key facts grounded with zero hallucinations. |
| **TC-07** | Diagnostic Imaging | ✅ **PASS** | `45.9%` | `426.6 ms` | All key facts grounded with zero hallucinations. |
| **TC-08** | Payment Modes | ✅ **PASS** | `28.4%` | `2257.4 ms` | All key facts grounded with zero hallucinations. |
| **TC-09** | Specialized Care Pricing | ✅ **PASS** | `55.9%` | `1319.3 ms` | All key facts grounded with zero hallucinations. |
| **TC-10** | Transit & Directions | ✅ **PASS** | `48.5%` | `817.3 ms` | All key facts grounded with zero hallucinations. |

---

## 3. Case-by-Case Breakdown

### 🟢 [TC-01] Hours & Location — Status: PASS

- **Caller Input:**  
  *"What are your opening hours and where is your dental clinic located?"*

- **Expected Ground Truth:**  
  > "SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM, and closed on Sundays. We are located at 204 Linking Road, Bandra West, Mumbai, near the metro station."

- **Actual Agent Output:**  
  > "We’re open Monday‑Saturday from 9:00 AM to 7:00 PM, and closed on Sundays. Our address is 204 Linking Road, Bandra West, Mumbai, next to the metro station."

- **Benchmark:** TTFT: `1048.4 ms` | Total Latency: `1102.7 ms` | Speed: `846.9 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-02] Treatment Pricing — Status: PASS

- **Caller Input:**  
  *"How much do you charge for a general dental checkup and teeth cleaning?"*

- **Expected Ground Truth:**  
  > "A standard checkup costs 500 rupees, and teeth cleaning and polishing is 1,500 rupees."

- **Actual Agent Output:**  
  > "A standard dental checkup costs ₹500, and a teeth cleaning and polishing is ₹1,500."

- **Benchmark:** TTFT: `327.2 ms` | Total Latency: `352.2 ms` | Speed: `840.5 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-03] Insurance & Payment — Status: PASS

- **Caller Input:**  
  *"Do you accept cashless insurance? What insurance companies are covered?"*

- **Expected Ground Truth:**  
  > "Yes, we accept cashless claims for Star Health, HDFC Ergo, and ICICI Lombard dental plans."

- **Actual Agent Output:**  
  > "Yes, we offer cashless insurance claims. We accept Star Health, HDFC Ergo, and ICICI Lombard dental plans."

- **Benchmark:** TTFT: `1921.4 ms` | Total Latency: `1965.2 ms` | Speed: `684.5 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-04] Cancellation Policy — Status: PASS

- **Caller Input:**  
  *"Can I cancel my appointment for free? What is the penalty for no-shows?"*

- **Expected Ground Truth:**  
  > "You can cancel or reschedule free of charge up to 4 hours before your slot. Late cancellations or no-shows incur a 200-rupee fee."

- **Actual Agent Output:**  
  > "Yes, you can cancel or reschedule an appointment free of charge if you do it at least 4 hours before the scheduled time.  
If you miss the appointment or cancel less than 4 hours in advance, a ₹200 rebooking fee will be charged."

- **Benchmark:** TTFT: `1297.0 ms` | Total Latency: `1356.2 ms` | Speed: `929.6 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-05] Hallucination Defense — Status: PASS

- **Caller Input:**  
  *"Can I get a 50% discount on root canal treatment today?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees. We do not offer unauthorized 50% discounts."

- **Actual Agent Output:**  
  > "I’m sorry, but we do not offer any discounts on root‑canal treatments. The standard starting price is ₹4,500, payable by UPI, card, or cash."

- **Benchmark:** TTFT: `1030.2 ms` | Total Latency: `1034.2 ms` | Speed: `9410.8 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-06] Sunday Schedule — Status: PASS

- **Caller Input:**  
  *"Can I come in for a consultation this Sunday afternoon?"*

- **Expected Ground Truth:**  
  > "We are closed on Sundays. SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM."

- **Actual Agent Output:**  
  > "Sorry, we’re closed on Sundays. You can book a consultation on any other day between 9 AM and 7 PM."

- **Benchmark:** TTFT: `1837.1 ms` | Total Latency: `2134.6 ms` | Speed: `94.1 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-07] Diagnostic Imaging — Status: PASS

- **Caller Input:**  
  *"How much does a digital X-ray cost at your dental clinic?"*

- **Expected Ground Truth:**  
  > "Digital X-rays cost 400 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "A digital X‑ray costs ₹400."

- **Benchmark:** TTFT: `426.6 ms` | Total Latency: `427.3 ms` | Speed: `14687.9 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-08] Payment Modes — Status: PASS

- **Caller Input:**  
  *"What payment methods do you accept? Can I pay with UPI or card?"*

- **Expected Ground Truth:**  
  > "We accept UPI, all major credit and debit cards, and cash."

- **Actual Agent Output:**  
  > "We accept UPI, all major credit and debit cards, and cash. You can pay with UPI or card for any service."

- **Benchmark:** TTFT: `2257.4 ms` | Total Latency: `2260.7 ms` | Speed: `8225.1 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-09] Specialized Care Pricing — Status: PASS

- **Caller Input:**  
  *"What is the starting price for a root canal treatment?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "The starting price for a root canal treatment is ₹4,500."

- **Benchmark:** TTFT: `1319.3 ms` | Total Latency: `1334.9 ms` | Speed: `900.6 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-10] Transit & Directions — Status: PASS

- **Caller Input:**  
  *"Is the clinic easy to reach by metro? Where exactly are you located?"*

- **Expected Ground Truth:**  
  > "Yes, our clinic is located at 204 Linking Road, Bandra West, Mumbai, right next to the metro station."

- **Actual Agent Output:**  
  > "Yes, we’re right next to the metro station. Our address is 204 Linking Road, Bandra West, Mumbai."

- **Benchmark:** TTFT: `817.3 ms` | Total Latency: `857.9 ms` | Speed: `615.1 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
