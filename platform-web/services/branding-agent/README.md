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

```bash
python -m pip install -e ".[dev]"
AI_STUB=true SERVICE_API_KEY=local-development-key \
  uvicorn branding_agent.api.app:app --reload --port 8001
pytest
```

The platform calls `/v1/chat/*` and `/v1/brand/*` using the `X-Agent-Key`
header. Configure model/image provider and R2 settings in this service only.
`POST /v1/intake/analyze` uses the same service authentication and returns a
normalized brief, verified user-provided evidence, marked inferences, or focused
clarification questions. The shared v1 JSON Schemas live in
`../../contracts/schemas/v1/`.

The platform API remains responsible for users, businesses, payments, job
status, and human review. Keep those responsibilities out of this service.
