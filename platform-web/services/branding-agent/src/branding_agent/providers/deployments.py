from dataclasses import dataclass


@dataclass(frozen=True)
class LLMDeployment:
    provider: str
    model: str
    api_key: str
    api_base: str | None = None

    @property
    def route_name(self) -> str:
        return f"branding-{self.provider}"

    @property
    def litellm_model(self) -> str:
        return f"{self.provider}/{self.model}"
