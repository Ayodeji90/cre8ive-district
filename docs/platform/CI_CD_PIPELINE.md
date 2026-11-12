# CI/CD Pipeline — Cre8ive District

## Repo Layout & Deployment Strategy

One repo, two independent deployments:

```
cre8ive-district/                    ← Git root
│
├── index.html                       ── VERCEL PROJECT A ──
├── about/ contact/ services/ work/   Current static website
├── vercel.json                       cre8ivedistrict.com
│                                     Root directory: /
│
├── platform-web/                    ── VERCEL PROJECT B ──
│   ├── apps/                         AI platform frontend
│   │   ├── marketing/  (:3000)       app.cre8ivedistrict.vercel.app
│   │   ├── platform/   (:3001)       Authenticated workspace (next deployment)
│   │   └── admin/      (:3002)
│   ├── packages/
│   │   ├── api-client/  tokens/  types/  ui/
│   ├── api/                         ── CONTAINER HOST ──
│   ├── services/                     Docker images → ghcr.io
│   │   ├── branding-agent/           Railway / Fly.io / ECS
│   │   └── website-agent/
│   └── docker-compose.yml
│
└── .github/workflows/
    ├── ci-frontend.yml              Frontend lint + typecheck + test + build
    ├── ci-backend.yml               Python lint + test + Docker build check
    └── deploy-backend.yml           Build & push Docker images to GHCR
```

Both Vercel projects deploy from **`main`**. No separate branches needed.


## How Builds Stay Independent

### Problem
When you push to `main`, both Vercel projects would try to rebuild — even if
only one side changed. Wasted build minutes and noise.

### Solution: Ignored Build Step scripts

Each Vercel project gets a script that checks "did MY files actually change?"

| Vercel project | Ignored Build Step setting |
|---|---|
| Static website (existing) | `bash scripts/vercel-ignore-website.sh` |
| Platform frontend (new) | `bash scripts/vercel-ignore-platform.sh` |

**Set this in Vercel:** Project Settings → Git → Ignored Build Step → paste the command.

The scripts compare `HEAD^..HEAD` — if only the other project's files changed,
they exit 0 (skip build). If their own files changed, exit 1 (proceed).


## Pipeline Overview

### On Pull Request

```
PR opened/updated
    │
    ├─ ci-frontend.yml (if platform-web/apps or packages changed)
    │   ├── Lint          (eslint via turbo)
    │   ├── Typecheck     (tsc --noEmit via turbo)
    │   ├── Test          (vitest via turbo)
    │   └── Build         (next build via turbo, after all above pass)
    │
    ├─ ci-backend.yml (if api/ or services/ changed)
    │   ├── API Lint      (ruff check + format --check)
    │   ├── API Test      (pytest with postgres + redis services)
    │   ├── Branding Agent Lint + Test
    │   ├── Website Agent Lint + Test
    │   └── Docker Build Check  (build images without pushing)
    │
    └─ Vercel Preview Deploy (automatic via GitHub integration)
        └── Preview URL for frontend changes
```

### On Push to Main

```
Push to main
    │
    ├─ CI jobs run (same as PR, must pass)
    │
    ├─ Vercel Production Deploy (automatic)
    │   └── Only if ignored build step says "yes, my files changed"
    │
    └─ deploy-backend.yml
        ├── Detect which services changed (dorny/paths-filter)
        ├── Build only changed service Docker images
        ├── Push to ghcr.io/ayodeji90/cre8ive-{api,branding-agent,website-agent}
        └── Container host picks up new image (webhook/poll)
```


## Setting Up Vercel (Two Projects, One Repo)

### 1. Keep existing project as-is
Your current website (`cre8ivedistrict.com`) keeps deploying from root.
Add the ignored build step:
- Go to: Project Settings → Git → Ignored Build Step
- Enter: `bash scripts/vercel-ignore-website.sh`

### 2. Create a second Vercel project for the public waitlist
```bash
cd platform-web
vercel link          # creates new project
```

In Vercel dashboard:
- **Project name:** `app.cre8ivedistrict` (Vercel production URL: `app.cre8ivedistrict.vercel.app`)
- **Root Directory:** `platform-web`
- **Framework Preset:** Next.js
- **Build Command:** `pnpm --filter @cre8ive/marketing build`
- **Output Directory:** `apps/marketing/.next`
- **Ignored Build Step:** `bash ../scripts/vercel-ignore-platform.sh`
- **Node.js Version:** 22.x

### 3. Environment variables for platform project
Set these in Vercel project settings (not in code) once the API is deployed:

```
NEXT_PUBLIC_API_URL=https://api.cre8ivedistrict.com
NEXT_PUBLIC_WS_URL=wss://api.cre8ivedistrict.com
```

### 4. Custom domain
The Vercel project receives `app.cre8ivedistrict.vercel.app` automatically.
Later, assign `app.cre8ivedistrict.com` to this same project once its DNS record
is configured. The root domain stays on the static site project.


## Setting Up the Container Host

The Python backend (API + agent services) runs as Docker containers. Pick one:

### Option A: Railway (simplest)
1. Connect repo in Railway dashboard
2. Create three services, each pointing to its Dockerfile:
   - `platform-web/api/Dockerfile`
   - `platform-web/services/branding-agent/Dockerfile`
   - `platform-web/services/website-agent/Dockerfile`
3. Railway auto-deploys on push to main

### Option B: Fly.io
1. Create three Fly apps
2. Use `fly deploy` with `--dockerfile` pointing to each service
3. Or pull from GHCR: `fly deploy --image ghcr.io/ayodeji90/cre8ive-api:latest`

### Option C: AWS (ECS/Fargate)
1. ECR repositories for each image
2. ECS services with Fargate tasks
3. GitHub Actions deploy step calls `aws ecs update-service --force-new-deployment`

For all options, the services need these environment variables:

**API:**
```
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
BRANDING_AGENT_URL=http://branding-agent:8000  (or the internal URL)
BRANDING_AGENT_API_KEY=<generated-secret>
```

**Branding Agent:**
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
IDEOGRAM_API_KEY=...
SERVICE_API_KEY=<same-secret-as-above>
R2_ENDPOINT=https://...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
R2_BUCKET=cre8ive-assets
R2_PUBLIC_URL=https://assets.cre8ivedistrict.com
```


## GitHub Secrets Required

Set these in GitHub repo settings → Secrets and variables → Actions:

| Secret | Used by | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | deploy-backend.yml | Built-in, pushes to GHCR |

The Vercel deploy is handled by Vercel's GitHub App (no token needed).
Container host deploy tokens depend on which provider you choose.


## Local Development

Everything runs via docker compose + turbo:

```bash
# Start backend infrastructure
cd platform-web
make up                    # postgres, redis, branding-agent, website-agent

# Start API
make dev                   # uvicorn on :8000

# Start frontend (separate terminal)
pnpm dev                   # turbo runs all Next.js apps

# Run all checks (mirrors CI)
make lint                  # ruff across all Python
make test                  # pytest across all Python
pnpm lint                  # eslint across all frontend
pnpm typecheck             # tsc across all frontend
pnpm test                  # vitest across all frontend
```


## Pipeline Diagram

```
                    ┌──────────────────────────────┐
                    │        Push / PR              │
                    └──────────┬───────────────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
        platform-web/apps/**          platform-web/api/**
        platform-web/packages/**      platform-web/services/**
                  │                         │
                  ▼                         ▼
        ┌─────────────────┐       ┌──────────────────┐
        │ ci-frontend.yml │       │  ci-backend.yml   │
        │                 │       │                   │
        │  lint           │       │  api-lint          │
        │  typecheck      │       │  api-test (pg+redis)│
        │  test           │       │  agent-lint        │
        │  build          │       │  agent-test        │
        └────────┬────────┘       │  docker-build ✓    │
                 │                └────────┬───────────┘
                 │                         │
          (push to main)           (push to main)
                 │                         │
                 ▼                         ▼
        ┌─────────────────┐       ┌──────────────────────┐
        │ Vercel auto-     │       │ deploy-backend.yml    │
        │ deploy (if files │       │                       │
        │ changed)         │       │ changed? → build →    │
        │                  │       │ push to ghcr.io →     │
        │ app.cre8ive...   │       │ container host pulls  │
        └─────────────────┘       └──────────────────────┘
```
