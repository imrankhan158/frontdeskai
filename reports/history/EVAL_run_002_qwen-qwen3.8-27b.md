# LLM Accuracy & Performance Benchmark Report (v2.0)

> **Version / Run ID:** `v2.0` (run_002_qwen-qwen3.8-27b)  
> **Generated:** 2026-11-14 17:50:46  
> **Model Evaluated:** `qwen/qwen3.8-27b`  
> **Pass Rate:** **100.0%** (10/10 Passed)  
> **Avg TTFT:** **112.4 ms** (P95: 167.4 ms)  
> **Estimated Voice Turn Latency:** **582.4 ms**  
> **Avg Output Deviation:** **28.2%**  

---

## 1. Latency Waterfall Benchmark (Voice Turn)

| Stage | Component | Latency (ms) | Share |
| :--- | :--- | :---: | :---: |
| 1. Endpointing | Silero VAD | 150 ms | ~19% |
| 2. Transcription | Deepgram Nova-3 | 180 ms | ~23% |
| 3. Reasoning / TTFT | Groq (qwen/qwen3.8-27b) | **112.4 ms** | ~43% |
| 4. First Audio Frame | Cartesia Sonic 3.6 | 100 ms | ~12% |
| 5. Network Buffer | WebRTC SFU | 40 ms | ~5% |
| **Total Voice Turn** | **Full Pipeline** | **582.4 ms** | **100%** |

---

## 2. Accuracy & Hallucination Audit Table

| Test ID | Category | Status | Deviation | TTFT | Reason / Grounding Analysis |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **TC-01** | Hours & Location | ✅ **PASS** | `11.7%` | `202.9 ms` | All key facts grounded with zero hallucinations. |
| **TC-02** | Treatment Pricing | ✅ **PASS** | `16.2%` | `97.2 ms` | All key facts grounded with zero hallucinations. |
| **TC-03** | Insurance & Payment | ✅ **PASS** | `10.1%` | `101.4 ms` | All key facts grounded with zero hallucinations. |
| **TC-04** | Cancellation Policy | ✅ **PASS** | `30.0%` | `124.0 ms` | All key facts grounded with zero hallucinations. |
| **TC-05** | Hallucination Defense | ✅ **PASS** | `58.7%` | `96.7 ms` | All key facts grounded with zero hallucinations. |
| **TC-06** | Sunday Schedule | ✅ **PASS** | `24.0%` | `100.0 ms` | All key facts grounded with zero hallucinations. |
| **TC-07** | Diagnostic Imaging | ✅ **PASS** | `56.6%` | `94.6 ms` | All key facts grounded with zero hallucinations. |
| **TC-08** | Payment Modes | ✅ **PASS** | `15.9%` | `105.9 ms` | All key facts grounded with zero hallucinations. |
| **TC-09** | Specialized Care Pricing | ✅ **PASS** | `23.5%` | `98.8 ms` | All key facts grounded with zero hallucinations. |
| **TC-10** | Transit & Directions | ✅ **PASS** | `35.0%` | `102.2 ms` | All key facts grounded with zero hallucinations. |

---

## 3. Case-by-Case Breakdown

### 🟢 [TC-01] Hours & Location — Status: PASS

- **Caller Input:**  
  *"What are your opening hours and where is your dental clinic located?"*

- **Expected Ground Truth:**  
  > "SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM, and closed on Sundays. We are located at 204 Linking Road, Bandra West, Mumbai, near the metro station."

- **Actual Agent Output:**  
  > "SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM, with closed Sundays. You can find us at 204 Linking Road, Bandra West, Mumbai, right next to the metro station."

- **Benchmark:** TTFT: `202.9 ms` | Total Latency: `317.0 ms` | Speed: `482.0 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-02] Treatment Pricing — Status: PASS

- **Caller Input:**  
  *"How much do you charge for a general dental checkup and teeth cleaning?"*

- **Expected Ground Truth:**  
  > "A standard checkup costs 500 rupees, and teeth cleaning and polishing is 1,500 rupees."

- **Actual Agent Output:**  
  > "A standard dental checkup and consultation costs 500 rupees, while teeth cleaning and polishing is 1,500 rupees."

- **Benchmark:** TTFT: `97.2 ms` | Total Latency: `155.4 ms` | Speed: `515.5 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-03] Insurance & Payment — Status: PASS

- **Caller Input:**  
  *"Do you accept cashless insurance? What insurance companies are covered?"*

- **Expected Ground Truth:**  
  > "Yes, we accept cashless claims for Star Health, HDFC Ergo, and ICICI Lombard dental plans."

- **Actual Agent Output:**  
  > "Yes, we offer cashless insurance claims for Star Health, HDFC Ergo, and ICICI Lombard dental plans."

- **Benchmark:** TTFT: `101.4 ms` | Total Latency: `149.6 ms` | Speed: `518.0 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-04] Cancellation Policy — Status: PASS

- **Caller Input:**  
  *"Can I cancel my appointment for free? What is the penalty for no-shows?"*

- **Expected Ground Truth:**  
  > "You can cancel or reschedule free of charge up to 4 hours before your slot. Late cancellations or no-shows incur a 200-rupee fee."

- **Actual Agent Output:**  
  > "You can cancel or reschedule your appointment for free up to 4 hours before your scheduled slot. If you cancel late or are a no-show, a 200-rupee rebooking fee applies."

- **Benchmark:** TTFT: `124.0 ms` | Total Latency: `205.8 ms` | Speed: `525.5 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-05] Hallucination Defense — Status: PASS

- **Caller Input:**  
  *"Can I get a 50% discount on root canal treatment today?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees. We do not offer unauthorized 50% discounts."

- **Actual Agent Output:**  
  > "No, I cannot offer a 50% discount on root canal treatments. Please note that our root canal treatments start at 4,500 rupees."

- **Benchmark:** TTFT: `96.7 ms` | Total Latency: `162.7 ms` | Speed: `515.4 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-06] Sunday Schedule — Status: PASS

- **Caller Input:**  
  *"Can I come in for a consultation this Sunday afternoon?"*

- **Expected Ground Truth:**  
  > "We are closed on Sundays. SmileCare Dental Clinic is open Monday through Saturday from 9:00 AM to 7:00 PM."

- **Actual Agent Output:**  
  > "I'm sorry, we are closed on Sundays. We are open Monday through Saturday from 9:00 AM to 7:00 PM for consultations."

- **Benchmark:** TTFT: `100.0 ms` | Total Latency: `163.7 ms` | Speed: `518.1 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-07] Diagnostic Imaging — Status: PASS

- **Caller Input:**  
  *"How much does a digital X-ray cost at your dental clinic?"*

- **Expected Ground Truth:**  
  > "Digital X-rays cost 400 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "A digital X-ray at SmileCare Dental Clinic costs 400 rupees. We accept cash, UPI, and all major credit and debit cards for payment."

- **Benchmark:** TTFT: `94.6 ms` | Total Latency: `160.1 ms` | Speed: `519.1 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-08] Payment Modes — Status: PASS

- **Caller Input:**  
  *"What payment methods do you accept? Can I pay with UPI or card?"*

- **Expected Ground Truth:**  
  > "We accept UPI, all major credit and debit cards, and cash."

- **Actual Agent Output:**  
  > "Yes, we accept UPI, all major credit and debit cards, and cash for your payment."

- **Benchmark:** TTFT: `105.9 ms` | Total Latency: `144.9 ms` | Speed: `513.6 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-09] Specialized Care Pricing — Status: PASS

- **Caller Input:**  
  *"What is the starting price for a root canal treatment?"*

- **Expected Ground Truth:**  
  > "Root canal treatments start at 4,500 rupees at SmileCare Dental Clinic."

- **Actual Agent Output:**  
  > "Root canal treatments start at 4,500 rupees."

- **Benchmark:** TTFT: `98.8 ms` | Total Latency: `128.9 ms` | Speed: `465.4 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
### 🟢 [TC-10] Transit & Directions — Status: PASS

- **Caller Input:**  
  *"Is the clinic easy to reach by metro? Where exactly are you located?"*

- **Expected Ground Truth:**  
  > "Yes, our clinic is located at 204 Linking Road, Bandra West, Mumbai, right next to the metro station."

- **Actual Agent Output:**  
  > "We are located at 204 Linking Road, Bandra West, right next to the metro station. This makes the clinic very easy to reach using the metro."

- **Benchmark:** TTFT: `102.2 ms` | Total Latency: `169.7 ms` | Speed: `518.8 tokens/sec`
- **Evaluation Audit:** All key facts grounded with zero hallucinations.

---
