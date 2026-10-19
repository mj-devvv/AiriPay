# AiriPay

An offline-first, cryptographic transaction verification engine designed to sustain retail commerce during high-latency network failures and central banking API downtimes.

---

## The Problem
In emerging markets, network infrastructure instability causes frequent merchant terminal drops. Merchants are forced to wait for high-latency cloud API pings to confirm payments or risk losing revenue to sophisticated fraud, such as fake credit alert applications. AiriPay shifts the burden of transactional trust from a live network connection to local, edge-computed mathematics.

## Core Architecture & Technical Highlights
* Asynchronous Verification Engine: Generates and validates transaction tokens completely disconnected from the internet grid (simulated local airplane mode).
* Symmetric Payload Hashing: Packages operational primitives (Terminal ID, Amount, and a local Unix Timestamp) into a compressed data payload protected by a truncated MD5 cryptographic signature block ([:8]) to ensure absolute tamper prevention.
* Zero-Allocation Data Transit: Dynamically processes high-density QR matrices entirely in-memory using Byte IO streams, encoding them straight into Base64 formats to prevent disk I/O bottlenecks.
* Human-Centric Minimalist Design: Built using a clean, utility-first UI architecture optimized for speed, clarity, and structural performance.

---

## Repository Structure
```text
airipay/
│
├── app.py                 # Flask server executing cryptographic payload signing
├── requirements.txt       # Local library package requirements
│
├── templates/             
│   └── index.html         # Structural minimalist portal interface (Tailwind CSS)
│
└── static/                
    ├── css/
    │   └── style.css      # Custom functional layout & state animations
    └── js/
        └── main.js        # Client-side validation logic & async API orchestration
```

---

## Local Sandbox Deployment

### 1. Clone & Navigate
```bash
git clone https://github.com/yourusername/airipay.git
cd airipay
```

### 2. Configure Dependencies
Ensure your environment is running Python 3.8+ and install required libraries:
```bash
pip install -r requirements.txt
```

### 3. Launch Local Edge Node
```bash
python app.py
```
Open your browser and navigate to the local loopback address: http://127.0.0.1:5000

---

## Security & Tamper Simulation Verification
The architecture is designed to mathematically reject altered packets. You can test the payload integrity inside the sandbox environment:
1. Compile a secure token on the Merchant Dashboard panel.
2. Copy the generated string payload from the console block.
3. Alter a single character or number inside the string (e.g., change the amount value or terminal id).
4. Paste the modified string into the verification portal and run the client diagnostics check.
5. The system will instantly catch the signature mismatch and trigger a TAMPER EXPLOIT ATTEMPT security warning without ever pinging an external database.

---
*Developed as a portfolio piece for hyper-local infrastructure optimization.*
