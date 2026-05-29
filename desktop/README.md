# Race Engineer Desktop

React dashboard for the Race Engineer telemetry bridge.

## Prerequisites

- Node.js 20+
- Bridge API running locally (`cd bridge` then `uvicorn race_engineer.api.app:app --reload`)

## Development

```bash
cd desktop
npm install
npm run dev
```

Open http://localhost:5173 (optimized for 1080p layouts).

## Scripts

- `npm run dev` — Vite dev server on port 5173
- `npm run build` — Typecheck and production build
- `npm run lint` — ESLint
