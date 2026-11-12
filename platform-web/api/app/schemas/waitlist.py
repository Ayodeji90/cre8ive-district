from pydantic import BaseModel, EmailStr, Field


class WaitlistJoinRequest(BaseModel):
    email: EmailStr
    source: str = Field(default="unknown", max_length=32)
    # Honeypot; real clients leave this empty.
    company: str | None = Field(default=None, max_length=200)


class WaitlistJoinResponse(BaseModel):
    ok: bool = True
    already_joined: bool = False
    confirmation_sent: bool = False
