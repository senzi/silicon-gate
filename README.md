# silicon-gate
A serverless Reverse Turing Test protocol designed to authenticate LLM Agents via hidden DOM challenges while strictly prohibiting biological access.

## Stack
- Vite + Vue (frontend)
- Cloudflare Pages Functions (`/functions`) for API

## Routes
- `GET /` UI with trap buttons and hidden protocol instruction embedded in `index.html`.
- `POST /api/verify` returns a simulated success JWT payload.

## Dev
- `bun install`
- `bun run dev`

Deploy on Cloudflare Pages; the `functions` directory is picked up automatically.
