# Backend deployment (ECS / Fargate)

Staging and production run the same four images on Amazon ECS (Fargate):

| Service | Image | Public? | Health |
| --- | --- | --- | --- |
| `api` | `ghcr.io/<owner>/cre8ive-api` | yes, via ALB | `GET /health`, `GET /health/db`, `GET /health/deps` |
| `worker` | `ghcr.io/<owner>/cre8ive-api` (`arq app.worker.WorkerSettings`) | no | ECS running count |
| `branding-agent` | `ghcr.io/<owner>/cre8ive-branding-agent` | no (service discovery) | `GET /health` |
| `website-agent` | `ghcr.io/<owner>/cre8ive-website-agent` | no (service discovery) | `GET /health` |
| `run-engine` | `ghcr.io/<owner>/cre8ive-run-engine` | no (service discovery) | `GET /health`, `GET /ready` |

Postgres is RDS, Redis is ElastiCache, and object storage stays on Cloudflare
R2. The frontend stays on Vercel.

## Release flow

```
pull request ──► CI · Frontend ──► Frontend CI gate
             └─► CI · Backend  ──► Backend CI gate
merge to main ──► CI · Backend ──► Deploy · Backend
                                  ├─ build + push four images after CI passes
                                  ├─ capture each registry digest
                                  ├─ staging: preflight, migrate, agents, api, smoke
                                  └─ production: approval, preflight, migrate, agents, api, smoke
```

Images are deployed as `ghcr.io/<owner>/cre8ive-<service>@sha256:...`
references, not tags. The build also publishes a commit-derived tag for
discovery, but deployment and rollback use the captured digests.

Automatic release runs only after successful backend CI for a push to `main`.
Manual **Deploy · Backend** dispatch is staging-only and independently checks
that the selected ref has a successful backend CI push run on `main`. Images
are not published by pull-request checks.

Production runs only after staging succeeds and requires approval through the
`production` GitHub Environment. Configure that environment with the chosen
reviewers and a `main` branch restriction before relying on this gate. Likewise,
configure `main` branch protection/rulesets to require `Frontend CI gate`,
`Backend CI gate`, and the team's chosen PR approval count. At the time of this
review, the repository had no branch protection/rulesets or GitHub environments,
so these controls are not yet active.

If a merged commit touches no backend paths, `preflight` sets `deploy=false`
and no images are built or rolled. The first time you merge this pipeline, the
`workflow_run` trigger only fires once both workflow files exist on `main`; use
`workflow_dispatch` for the initial run.

## One-time AWS setup

1. **GitHub OIDC provider** in IAM:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
2. **Deploy role** assumed by the workflows (`AWS_ROLE_ARN`). Trust policy
   restricted to this repository and the `staging`/`production` environments.
   The workflow grants `id-token: write` only to jobs that need AWS credentials:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": { "Federated": "arn:aws:iam::<account>:oidc-provider/token.actions.githubusercontent.com" },
       "Action": "sts:AssumeRoleWithWebIdentity",
       "Condition": {
         "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
         "StringLike": { "token.actions.githubusercontent.com:sub": "repo:<owner>/<repo>:environment:*" }
       }
     }]
   }
   ```

   Minimum permissions: `ecs:DescribeServices`, `ecs:DescribeTaskDefinition`,
   `ecs:RegisterTaskDefinition`, `ecs:UpdateService`, `ecs:RunTask`,
   `ecs:DescribeTasks`, plus `iam:PassRole` for the task execution/task roles.
3. **Clusters and services** per environment. The pipeline assumes these exist
   (created by your IaC or console):
   - cluster `cre8ive-staging` / `cre8ive-production`
   - one ECS service and one task definition family per row in the table above
   - the worker task definition overrides the API image command; container name
     is `api` by default (override with `ECS_API_CONTAINER` / matrix container)
4. **Networking**: private subnets for the tasks, a NAT gateway or VPC endpoints
   for ECR/GHCR/CloudWatch, and an ALB target group for the API with:
   - health check path `/health`
   - healthy threshold 2, interval 15s, timeout 5s
   - deregistration delay 30s

   Give the internal services Cloud Map names and point the API task definition at
   them (`BRANDING_AGENT_URL`, `WEBSITE_AGENT_URL`, `RUN_ENGINE_URL`). Set each
   service's `*_API_KEY` variable to the same value as the agent's
   `SERVICE_API_KEY`; `/health/deps` will report a mismatch immediately.
5. **ECS service settings** (recommended, not automated here):
   - deployment circuit breaker with rollback enabled
   - minimum healthy percent 100, maximum 200
   - `stopTimeout` ≥ 30s so in-flight chat streams finish
6. **GHCR pull access.** Packages are private by default. Either:
   - make the four packages public and let the task execution role pull
     anonymously, or
   - store a GHCR read token in Secrets Manager and add
     `"repositoryCredentials": {"credentialsParameter": "<secret-arn>"}` to the
     container definitions.

## Environment variables

Set these as **repository variables scoped to the `staging` and `production`
GitHub Environments** (Settings → Environments → *environment* → Variables).
They are read with `vars.*`, so no secrets are copied into workflows.

| Variable | Example |
| --- | --- |
| `AWS_ROLE_ARN` | `arn:aws:iam::123456789012:role/cre8ive-deploy` |
| `AWS_REGION` | `eu-west-1` |
| `ECS_CLUSTER` | `cre8ive-production` |
| `PUBLIC_BASE_URL` | `https://api.cre8ivedistrict.com` |
| `ECS_SUBNETS` | `subnet-aaa,subnet-bbb` |
| `ECS_SECURITY_GROUPS` | `sg-0123456789` |
| `ECS_ASSIGN_PUBLIC_IP` | `DISABLED` (default) |
| `ECS_SERVICE_API` | `cre8ive-api` |
| `ECS_TASKDEF_API` | `cre8ive-api` |
| `ECS_API_CONTAINER` | `api` (default) |
| `ECS_SERVICE_WORKER` | `cre8ive-worker` |
| `ECS_TASKDEF_WORKER` | `cre8ive-worker` |
| `ECS_SERVICE_BRANDING` | `cre8ive-branding-agent` |
| `ECS_TASKDEF_BRANDING` | `cre8ive-branding-agent` |
| `ECS_SERVICE_WEBSITE` | `cre8ive-website-agent` |
| `ECS_TASKDEF_WEBSITE` | `cre8ive-website-agent` |
| `ECS_SERVICE_RUNENGINE` | `cre8ive-run-engine` |
| `ECS_TASKDEF_RUNENGINE` | `cre8ive-run-engine` |

Application secrets (database URL, `JWT_SECRET`, Paystack, Resend, R2, service
keys) belong in **AWS Secrets Manager** and are referenced from the task
definitions via `secrets`. They are not GitHub variables and never pass through
the workflow.

## Migration handling

Migrations run as a **one-off ECS task before any service is updated**:

1. The pipeline registers a new revision of the API task definition with the
   new image, without touching the service.
2. It runs `alembic upgrade head` in that revision using `aws ecs run-task`.
3. It waits for the task to stop and fails the release if the exit code is not
   `0`. Agents and API are not touched in that case.
4. Only then are the agents, worker and API rolled.

Because the same image and task definition are used, the migration runs exactly
the code you are deploying.

**Rules for migration authors:**

- Migrations are **forward-only**. Several existing revisions intentionally
  raise on downgrade; rollback never runs `alembic downgrade`.
- Use expand/contract for breaking changes: add the new column/table in release
  N, migrate reads/writes, drop the old shape in release N+1. A rollback to
  release N must still work against the schema written by N+1.
- Keep migrations idempotent-friendly. CI applies `alembic upgrade head` twice
  and runs `alembic check` to catch model drift on every PR.

## Health checks and smoke tests

`GET /health/deps` checks Postgres, Redis, and each agent's authenticated
`/v1/ping` in parallel and returns `503` if any is down or rejects the service
key. It is the release smoke test:

```
GET /health       -> liveness
GET /health/db    -> Postgres round-trip
GET /health/deps  -> Postgres + Redis + branding + website + run-engine
```

The `smoke` job retries each endpoint (up to 45 attempts for `/health/deps`)
before failing, which covers ALB registration and container warm-up.

For local diagnosis, run `make doctor` or `./platform-web/scripts/doctor.sh`.
It prints the same dependency report plus container health and the
service-to-service key checks that explain most "chat does not start" reports.

## Rollback

**Automatic.** If agents, API, or smoke fail, the `rollback` job restores the
task definition ARNs captured before the deploy, API first, then worker and
agents, and waits for each service to stabilize.

**Manual.** Run **Actions → Rollback · Backend** with:

- `environment`: `staging` or `production`
- `api_digest`
- `branding_agent_digest`
- `website_agent_digest`
- `run_engine_digest`

Copy all four `sha256:...` values from the release run summary for the desired
version. The workflow re-registers and rolls those digest-pinned images with
`run_migrations: false`. A production manual rollback passes through the
`production` environment and requires its configured approval; automatic
rollback restores the task definitions captured before deployment.

**Emergency CLI fallback:**

```bash
aws ecs update-service --cluster "$ECS_CLUSTER" --service cre8ive-api \
  --task-definition cre8ive-api:<previous-revision>
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services cre8ive-api
```

Check the previous revision in the failed run's log (`preflight` prints every
rollback target) or with:

```bash
aws ecs describe-services --cluster "$ECS_CLUSTER" \
  --services cre8ive-api --query 'services[0].deployments'
```

## Verifying the pipeline

```bash
# YAML and expression sanity (locally, if actionlint is installed)
actionlint .github/workflows/*.yml

# Compose definition that CI validates
cd platform-web && docker compose config -q

# Full backend checks, same as CI
cd platform-web && make lint && make test
```

The first real release requires the AWS resources above. Until the `staging`
environment variables and GitHub environment protections are configured, the
deploy preflight will fail before any ECS service is touched; images may already
have been built and pushed, but deployments continue to reference their immutable
digests.
