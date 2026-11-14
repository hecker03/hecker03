<div align="center">

# Shrishailya Keskar

**I build LLM-integrated apps, and the tooling that keeps them safe.**

B.E. Information Technology · PES Modern College of Engineering, Pune · 2023–2027

</div>

---

## About

I like projects where a model sits inside a real system and something has to be built around it: data flow, trust boundaries, evaluation. Most work below was built for a deadline or for my own daily use. I've marked which is which.

## Featured work

### Vanguard: security fabric for banking
*SuRaksha Cyber Hackathon 2.0 (Canara Bank) · Jun–Jul 2026 · team of five · built on synthetic data*

One architecture replacing isolated checkpoints with four connected pillars:

- **Behavioural identity:** Isolation Forest scoring 12+ device and behaviour signals, driving adaptive MFA (passkey, step-up TOTP, session block)
- **Document forensics:** forgery detection with Error Level Analysis, metadata extraction and a heatmap overlay
- **Agentic compliance:** LangGraph multi-agent workflow with Gemini, including vision-based checking of uploaded evidence
- **Insider governance:** an agent-based second approval for risky admin actions, plus a local redaction layer that strips PII before text reaches cloud LLMs

**Stack:** Python, FastAPI, LangGraph, Gemini, scikit-learn, OpenCV, PyMuPDF, React, ChromaDB, Redis, privacyIDEA, Docker Compose
**My part:** *[write exactly what you built]*
[Repository](https://github.com/hecker03/cyber-suraksha-hackathon-project)

### Prompt Scrubber
*Personal project · v1.2 · in use on my own machine*

Redacts usernames, paths, GitHub handles, emails and secrets from text before it goes into an AI prompt. A Firefox extension and a Python clipboard agent share one rule file and one set of tests. Next step: a scope-aware version for pentest output, with a measured leakage-versus-utility evaluation.

**Stack:** JavaScript, Python, WebExtensions
[Repository](https://github.com/hecker03/prompt_scrubber)

### ForensIQ: digital forensics platform
*Personal project · Mar–May 2026*

Full-stack web app with JWT auth, a Dockerized dev stack, production Dockerfiles with an AWS Amplify build spec, and a standalone Python memory-forensics script.

**Stack:** React (Vite), Node.js, Express, MongoDB, Docker Compose, AWS Amplify
[Repository](https://github.com/hecker03/prompt_scrubber)

### Smaller tools I use myself

| Tool | What it does |
|---|---|
| [Daily Tracker](https://github.com/hecker03/daily_tracker) | Firefox extension that times my study blocks and logs minutes to a Google Sheet |
| [Site Visit Tracker](https://github.com/hecker03/site-visit-tracker) | Cross-browser extension that logs top-level page visits to a Google Sheet during VAPT; offline queue, cross-platform installer, 99 automated tests |

## Where LLMs show up in my work

| Area | What I did | Status |
|---|---|---|
| Multi-agent workflows | LangGraph compliance agents with Gemini (Vanguard) | Hackathon prototype, team project |
| Vision-model checking | Evidence screenshots audited by a vision model (Vanguard) | Hackathon prototype, team project |
| Data privacy before LLMs | Local redaction layers: Vanguard's PII filter, Prompt Scrubber | Prototype / personal use |
| Securing LLM applications | Final-year project on protecting LLM-integrated apps | In progress |

## Now

- Final-year project on securing LLM-integrated applications
- Evaluating scope-aware redaction on lab data

## Stack

Python · FastAPI · scikit-learn · LangGraph · React · Node.js · MongoDB · Docker · Git · Linux
Also used: Burp Suite, Wireshark, Nessus, Kali Linux

## Background

National finalist, IndiaSkills 2025–26 (Cyber Security). Internships in web application security testing at Farchase Solutions and ScaleFull Technologies.

## Contact

[LinkedIn](https://linkedin.com/in/shrishailyakeskar-12s6511)>