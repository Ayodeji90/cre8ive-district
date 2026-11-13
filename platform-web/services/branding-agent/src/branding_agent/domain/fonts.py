"""Curated font pair library — all fonts verified on Google Fonts."""

from branding_agent.domain.ai_models import FontPair, FontSpec

FONT_PAIRS: list[dict] = [
    {
        "heading": {"family": "Space Grotesk", "weight": 700},
        "body": {"family": "Inter", "weight": 400},
        "personality": ["modern", "tech", "clean"],
    },
    {
        "heading": {"family": "Playfair Display", "weight": 700},
        "body": {"family": "Source Sans 3", "weight": 400},
        "personality": ["elegant", "luxury", "classic"],
    },
    {
        "heading": {"family": "Plus Jakarta Sans", "weight": 800},
        "body": {"family": "Plus Jakarta Sans", "weight": 400},
        "personality": ["friendly", "contemporary", "approachable"],
    },
    {
        "heading": {"family": "DM Serif Display", "weight": 400},
        "body": {"family": "DM Sans", "weight": 400},
        "personality": ["editorial", "sophisticated", "warm"],
    },
    {
        "heading": {"family": "Sora", "weight": 700},
        "body": {"family": "Nunito", "weight": 400},
        "personality": ["geometric", "startup", "fresh"],
    },
    {
        "heading": {"family": "Outfit", "weight": 700},
        "body": {"family": "Outfit", "weight": 400},
        "personality": ["bold", "energetic", "youthful"],
    },
    {
        "heading": {"family": "Fraunces", "weight": 700},
        "body": {"family": "Commissioner", "weight": 400},
        "personality": ["creative", "artisan", "distinctive"],
    },
    {
        "heading": {"family": "Montserrat", "weight": 700},
        "body": {"family": "Open Sans", "weight": 400},
        "personality": ["professional", "corporate", "trustworthy"],
    },
    {
        "heading": {"family": "Bricolage Grotesque", "weight": 700},
        "body": {"family": "Nunito Sans", "weight": 400},
        "personality": ["playful", "fun", "informal"],
    },
    {
        "heading": {"family": "Cormorant Garamond", "weight": 600},
        "body": {"family": "Lato", "weight": 400},
        "personality": ["refined", "premium", "timeless"],
    },
    {
        "heading": {"family": "Archivo Black", "weight": 400},
        "body": {"family": "Work Sans", "weight": 400},
        "personality": ["powerful", "impactful", "urban"],
    },
    {
        "heading": {"family": "Libre Baskerville", "weight": 700},
        "body": {"family": "Libre Franklin", "weight": 400},
        "personality": ["traditional", "authoritative", "literary"],
    },
    {
        "heading": {"family": "Poppins", "weight": 700},
        "body": {"family": "Poppins", "weight": 400},
        "personality": ["versatile", "balanced", "dependable"],
    },
    {
        "heading": {"family": "Lexend", "weight": 700},
        "body": {"family": "Lexend", "weight": 400},
        "personality": ["accessible", "clear", "inclusive"],
    },
    {
        "heading": {"family": "Bebas Neue", "weight": 400},
        "body": {"family": "Roboto", "weight": 400},
        "personality": ["dramatic", "cinematic", "attention-grabbing"],
    },
    {
        "heading": {"family": "Merriweather", "weight": 700},
        "body": {"family": "Source Sans 3", "weight": 400},
        "personality": ["warm", "readable", "grounded"],
    },
    {
        "heading": {"family": "Raleway", "weight": 700},
        "body": {"family": "Raleway", "weight": 400},
        "personality": ["minimal", "sleek", "design-forward"],
    },
    {
        "heading": {"family": "Crimson Pro", "weight": 600},
        "body": {"family": "Inter", "weight": 400},
        "personality": ["intellectual", "cultured", "editorial"],
    },
    {
        "heading": {"family": "Rubik", "weight": 700},
        "body": {"family": "Rubik", "weight": 400},
        "personality": ["rounded", "welcoming", "modern-friendly"],
    },
    {
        "heading": {"family": "Josefin Sans", "weight": 700},
        "body": {"family": "Nunito", "weight": 400},
        "personality": ["retro", "stylish", "boutique"],
    },
]


def get_font_pair(index: int) -> FontPair:
    pair = FONT_PAIRS[index % len(FONT_PAIRS)]
    return FontPair(
        heading=FontSpec(**pair["heading"]),
        body=FontSpec(**pair["body"]),
    )
