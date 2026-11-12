# Shared contracts

This directory is the language-neutral source of truth for communication
between the platform API and independently deployed agent services.

Contracts are not an agent or runtime service. Define request/result schemas
and event schemas here, then validate or generate service-specific types from
them. Keep schemas versioned and make compatibility changes deliberate.

The v1 Branding Intake contract is in `schemas/v1/`. It supports structured
brief fields, unstructured text, and conversation history that may require
clarification. The Branding Agent validates the corresponding request and
response shapes against these JSON Schemas.

The generated Brand Package, package-version lifecycle, and service-to-service
release events are not defined yet. Establish those contracts before
implementing full package generation or the direct Website Agent handoff.
