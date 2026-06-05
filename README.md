# GenAI Research Radar 🚀

An autonomous, enterprise-grade research agent that tracks, analyzes, and summarizes the latest breakthroughs in text-to-video generation and diffusion models. Built using Python, the Google GenAI SDK, and GitHub Actions, this pipeline runs completely headless on a daily schedule to deliver structured engineering insights.

---

## 🏗️ Architecture & Failsafe Design

This agent is built with a **Highly Available (HA) Data Pipeline** architecture to ensure that upstream server dependencies or API rate limits never break the automation flow.

```text
                  [ Daily GitHub Actions Cron (08:00 UTC) ]
                                     │
                                     ▼
                        [ Fetch Latest Research ]
                                     │
             ┌───────────────────────┴───────────────────────┐
             ▼ (Primary)                                     ▼ (Fallback)
     📊 ArXiv API Query                              🤗 Hugging Face Daily Papers
   (all:diffusion+video)                           (Custom User-Agent Spoofing)
             │                                               │
             ├─────────────── API Down / 0 Entries? ─────────┘
             │
             ▼
   [ Paper Metadata List ]
             │
             ▼
    [ Gemini 2.5 Flash ] ───► (Exponential Backoff Retry for 429/503 errors)
             │
             ▼
  [ Markdown Report Gen ] ───► Written to `/reports/digest_YYYY-MM-DD.md`
             │
             ▼
 [ Automated Git Commit/Push ]
```

### Key Engineering Features
* **Dual-Source Ingestion:** Uses ArXiv's query system as a primary source, seamlessly falling back to Hugging Face's Trending Daily Papers API if ArXiv encounters a `503 Service Unavailable` or unexpected schema errors.
* **Smart Anti-Throttling:** Implements custom `User-Agent` string headers on HTTP requests to bypass strict automated bot/scraping filters on web entry points.
* **Fault-Tolerant LLM Execution:** Configured with an **Exponential Backoff Retry Strategy** to smoothly absorb temporary API rate limits (`429 Resource Exhausted`) or downstream server strain.
* **High-Quota Operational Balance:** Leverages the `gemini-2.5-flash` model structure to accommodate high-volume daily evaluations under standard free-tier execution windows (up to 1,500 requests/day).

---

## 📁 Repository Structure

```text
genai-research-radar/
│
├── .github/
│   └── workflows/
│       └── daily_agent.yml     # GitHub Actions workflow scheduling configuration
│
├── reports/                    # Auto-generated daily markdown summaries (Git-managed)
│   └── digest_YYYY-MM-DD.md
│
├── agent.py                    # Core pipeline logic, execution, and LLM orchestration
└── requirements.txt            # Explicit third-party runtime dependencies
```

---

## ⚡ Local Development & Testing

To set up the environment locally for debugging or tuning prompt parameters:

### 1. Environment Isolation
Initialize and activate a clean Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Dependency Management
Install the verified library manifest:
```bash
pip install -r requirements.txt
```

### 3. Credential Injection & Execution
Export your Gemini API Key directly into your local terminal session environment variables and trigger the agent runtime execution:
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
python agent.py
```

---

## 🤖 CI/CD Automation Setup (GitHub Actions)

The agent runs autonomously every single day at **08:00 UTC**. To set up this production workflow in your repository:

1. Navigate to your GitHub repository settings: **Settings -> Secrets and variables -> Actions**.
2. Click **New repository secret**.
3. Name the secret **`GEMINI_API_KEY`** and paste your Google AI Studio API key as the value.
4. Ensure your repository permissions allow workflows to commit data. Go to **Settings -> Actions -> General -> Workflow permissions** and select **Read and write permissions**.

---

## 📝 Generated Output Specification

The agent analyzes each paper abstract from a senior engineering lens, bypasses raw academic fluff, and outputs a highly structured markdown layout located within the `reports/` directory:

```markdown
# AI Research Digest - YYYY-MM-DD

> *Automated daily analysis of the latest text-to-video and diffusion model research.*

### [Paper Title Example]
[Read Full Paper](https://arxiv.org/abs/...)

**The TL;DR:** A single concise statement summarizing the absolute core concept of the study.
**Architectural Innovation:** Structural deep dive highlighting explicit adjustments to DiTs, U-Nets, Latent Spaces, or customized Attention Kernels.
**Engineering Takeaway:** Pragmatic deployment insight focusing on compute cost optimization, inference latency, or training stability.
```
