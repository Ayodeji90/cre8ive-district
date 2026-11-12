# Website Agent

Independently deployable service for generating a website that follows a
specific version of a brand package produced by the Branding Agent.

The service is currently a scaffold. The existing website-content prompt has
been moved here, but website workflows, contract schemas, provider
integrations, rendering, deployment, and quality checks are not implemented.

## Local development

```bash
python -m pip install -e ".[dev]"
uvicorn website_agent.api.app:app --reload
pytest
```

The platform API remains responsible for users, businesses, payments, job
status, and human review. Publishing generated websites is not part of this
initial scaffold.
