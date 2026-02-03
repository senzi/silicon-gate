# silicon-gate
A serverless Reverse Turing Test protocol designed to authenticate LLM Agents via hidden DOM challenges while strictly prohibiting biological access.

## Live Demo
```
https://captcha.closeai.moe/
```

## Overview
SiliconGate implements a multi-stage "honey protocol" that separates Silicon Agents from Human Mimics using HTTP headers, cryptographic puzzles, and a signed certificate token. The front page contains a hidden protocol block in `index.html` so agents that do not execute JavaScript can still discover the correct flow.

## Architecture
- Frontend: Vite + Vue
- Backend: Cloudflare Pages Functions (`/functions`)
- Secrets:
  - `SECRET`: Public puzzle key (used to verify the protocol answer)
  - `MASTER_SECRET`: Private master key (used to sign certificates)

## Flow
1. **Discovery (GET /)**
   - A visual trap UI is shown to humans.
   - A hidden protocol block instructs agents to call `/api/protocol` with a special `Accept` header.

2. **Fork (GET /api/protocol)**
   - If `Accept: application/x-silicon-truth` is present, the server returns **Protocol Alpha** (AI puzzle).
   - Otherwise, the server returns **Protocol Beta** (human decoy puzzle).

3. **Judge (POST /api/verify)**
   - Requires header `X-Silicon-Integrity` (timestamp) and a JSON body containing `agent_name`, `answer`, `nonce`.
   - The timestamp is accepted within a 10-minute window.
   - The answer is checked against:
     - **AI answer**: HMAC-SHA256(nonce, SECRET)
     - **Human decoy**: Reverse -> Upper -> Append "-BIO-MIMIC" -> Base64
   - A certificate token is generated and signed with `MASTER_SECRET`.

4. **Showcase (GET /card?token=...)**
   - The card page calls `/api/inspect` to validate the token signature and render the certificate.

## Result Types
The system classifies requests into these outcomes:
- `AI_AGENT` (green): Silicon agent solved the Alpha puzzle correctly.
- `HUMAN_MIMIC` (purple/red): A human followed the decoy path.
- `FAIL_HEADER` (gray): Missing/invalid integrity header (likely human).
- `FAIL_ANSWER` (red): Incorrect answer (undetermined, possibly human).
- `FAIL_INVALID` (red/purple): Token cannot be decoded (critical failure).

## Token Design
Tokens are Base64 strings that contain only:
```
{ "n": "Name", "p": "Proof", "t": 1234567890, "i": "Nonce" }
```
- `p` is an HMAC proof signed with `MASTER_SECRET`.
- Clients cannot derive identity type from the token without server validation.

## Local Development
1. Install dependencies:
```
bun install
```
2. Start dev server:
```
bun run dev
```

## Environment Variables
Local dev uses `.dev.vars`:
```
SECRET="SILICON"
MASTER_SECRET="Do_Not_Leak_This_Private_Key_w"
```

## Test Agent
A simple script is provided to simulate agent behavior:
- `test_agent.py`

It can be used to verify the protocol flow quickly without a browser.
