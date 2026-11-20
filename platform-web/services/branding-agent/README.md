# Branding Agent

Independently deployable service for turning an approved brand brief into a
versioned brand package. The package can include identity strategy, logos,
guidelines, marketing flyers, and social media assets.

The service provides authenticated chat, separate brand-generation operations,
asset rendering, and a v1 brief intake/normalization endpoint. End-to-end brand
package orchestration, marketing collateral formats, and the complete generated
package contract remain to be implemented. The current intake contract supports
structured JSON, unstructured text, and conversation history; uploaded-file
parsing is not included.

## Local development

Run these commands from the repository root:

```bash
cd platform-web/services/branding-agent
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
AI_STUB=true SERVICE_API_KEY=local-development-key .venv/bin/python -m uvicorn \
  branding_agent.api.app:app --reload --port 8001
```

In another terminal, run the tests from the repository root:

```bash
cd platform-web/services/branding-agent
.venv/bin/python -m pytest
```

The platform calls `/v1/chat/*` and `/v1/brand/*` using the `X-Agent-Key`
header. Configure model/image provider and R2 settings in this service only.
`POST /v1/intake/analyze` uses the same service authentication and returns a
normalized brief, verified user-provided evidence, marked inferences, or focused
clarification questions. The shared v1 JSON Schemas live in
`../../contracts/schemas/v1/`.

## LLM provider routing

Copy `.env.example` to `.env` and add keys for the providers you want to use.
`LLM_ROUTING_ORDER` controls the sequential order; a deployment is included only
when both its API key and model are configured. The default order is Groq,
NVIDIA NIM, OpenRouter, Anthropic, then OpenAI. NVIDIA NIM and OpenRouter can
also use their respective optional API base URL settings.

The router retries the same request context on the next configured provider only
for rate limits, connection errors, server errors, and timeouts. Other errors
are returned immediately. Every fallback is a new provider request and may use
that provider's quota or incur charges. `LLM_PROVIDER_TIMEOUT_SECONDS` sets the
per-provider timeout. For streaming, failover is allowed only before the first
content chunk, so an interrupted partial response is returned as an error rather
than being silently restarted.

The platform API remains responsible for users, businesses, payments, job
status, and human review. Keep those responsibilities out of this service.
