# Cre8ive District Platform Web

Frontend monorepo for the Cre8ive District brand launch platform. It contains separate Next.js applications for the marketing site, customer workspace, and internal admin; shared UI, design tokens, domain types, and a typed API client live in `packages/`.

## Run locally

Requirements: Node.js 20.9 or newer and Corepack.

```bash
corepack enable
corepack prepare pnpm@9.15.9 --activate
pnpm install
pnpm dev
```

The apps run at `http://localhost:3000` (marketing), `http://localhost:3001` (platform), and `http://localhost:3002` (admin). Copy `.env.example` to the app-specific `.env.local` files when backend/auth integrations are available.

```bash
pnpm lint
pnpm typecheck
pnpm build
```

## Workspace layout

```text
apps/marketing   Public site (port 3000)
apps/platform    Customer workspace (port 3001)
apps/admin       Designer and operations dashboard (port 3002)
packages/ui      Shared, vendored React components
packages/tokens  Cre8ive District design tokens
packages/types   Shared TypeScript domain types
packages/api-client  Typed backend API wrapper and endpoint methods
```

Tailwind CSS 4 uses the shared CSS-first theme at `packages/tokens/src/tokens.css`. The `tailwind-preset.ts` token map is provided only for legacy Tailwind 3 consumers; Tailwind 4 does not load JavaScript presets. Components are authored in TypeScript and styled with Tailwind utilities.

The previous static interface prototype remains at the repository root as a visual/content reference. The new Next.js apps are the frontend implementation path.

## Backend

The platform API lives in [`api/`](api/README.md): FastAPI, async SQLAlchemy, Alembic, Redis, Paystack, R2, Resend, and the AI service seam. See `api/README.md` for setup; use the root `docker-compose.yml` and `Makefile` for local services.
