# Contract schemas

Versioned JSON Schema documents are the language-neutral contracts. The
Branding Agent currently implements v1 intake, normalized brief, and
strategy-package models in `services/branding-agent/src/branding_agent/domain/`;
changes to either side must preserve the same field names, limits, and lifecycle
rules.

`v1/` defines:

- `intake-request.schema.json`: structured brief, free-form brief, and
  user/assistant conversation inputs.
- `brand-brief.schema.json`: normalized facts with source provenance and
  explicit inferred assumptions.
- `intake-result.schema.json`: ready/needs-clarification result and focused
  follow-up questions with rationale, required/optional status, and optional
  suggested answer choices.
- `strategy-package-request.schema.json`: normalized brief submitted for
  strategy generation.
- `strategy-package.schema.json`: validated strategy for human review, or a
  blocked result with deterministic validation issues after bounded retries.

The intake endpoint is `POST /v1/intake/analyze`. It requires the agent service
credential. A clear business offering is the only required content for intake
to be ready; audience, industry, geography, and style can remain unknown or be
marked as inferred. A missing business name is allowed when name suggestions
are enabled. Uploaded-file parsing and the generated Brand Package contract
are not part of this initial contract version. `POST /v1/brand/strategy-package`
accepts a normalized brief only after its offering and naming choice are ready;
it returns a strategy marked ready for human review only after deterministic
validation passes.

Intake is stateless in the Branding Agent: the platform owns conversation
history and submits the prior turns with each new user answer. The agent
re-analyzes both structured and conversational input on every turn, returns at
most three clarification questions, and includes optional choices when useful.
Choices remain suggestions until the user confirms or edits one in a user
message. Optional clarification can be skipped; required questions and the
deterministic core-offering/name-permission gates keep the result in
`needs_clarification`.
