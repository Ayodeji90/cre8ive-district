# Brand Generation Pipeline — Implementation Plan

*Standalone spec for the service that turns a business description into a
complete brand identity: logo, colours, typography, and a guidelines PDF.*

**Last updated:** 2026-11-07
**Owner:** Cre8ive District engineering
**Depends on:** Conversation Service (for intake data), Asset Storage (S3/R2),
Approval Queue, Billing Service (credit gate).

---

## 1. What This Delivers

A customer describes their business in plain language and receives:

| Deliverable | Formats |
|---|---|
| **Primary logo** | SVG (vector source) + PNG at 512 px, 256 px, 128 px, 64 px, 16 px (favicon ICO) |
| **Logo variations** | Icon mark, wordmark, horizontal lockup, stacked lockup — each in SVG + PNG × 4 sizes |
| **Colour palette** | Primary, secondary, accent, neutral, light bg, dark bg — hex, RGB, HSL, CMYK (print) |
| **Typography pairing** | Heading + body Google Fonts, weight scale (Regular / Medium / Bold / Extra-Bold), size ramp (14–48 px) |
| **Brand guidelines PDF** | 8–12 pages: logo usage rules, clear-space spec, colour specs, typography rules, do's & don'ts, social avatar specs |
| **Social media avatars** | Circular-cropped icon mark at 400 × 400 (IG/FB), 320 × 320 (WhatsApp), 200 × 200 (X) |

Generation target: **< 5 minutes** from intake completion to brand package ready
for review (excluding human designer review time).

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│               BRAND GENERATION PIPELINE              │
│                                                      │
│  Business Description + Intake Answers               │
│         │                                            │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │ Brand Strategy│  LLM (Claude Sonnet / Haiku)      │
│  │ Engine        │  → brand brief JSON               │
│  └──────┬───────┘                                    │
│         │                                            │
│    ┌────┴────┬──────────┐                            │
│    ▼         ▼          ▼                            │
│  Colour   Typography   Logo                          │
│  Generator Selector    Generator                     │
│  (LLM +   (LLM +      (Image Gen API                │
│   colour   Google      + prompt eng)                 │
│   math)    Fonts API)                                │
│    │         │          │                            │
│    └────┬────┴──────────┘                            │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │ Asset        │  SVG processing, PNG rendering,    │
│  │ Renderer     │  size variants, favicon, avatars   │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │ Guidelines   │  LLM writes copy → WeasyPrint      │
│  │ PDF Builder  │  renders branded PDF                │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │ Quality Gate │  Contrast checks, format            │
│  │              │  validation, completeness           │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  Approval Queue (human designer review)              │
│         ▼                                            │
│  Delivery Service → WhatsApp / email / download      │
└─────────────────────────────────────────────────────┘
```

---

## 3. Data Structures

### 3.1 Input — `BrandRequest`

```python
from pydantic import BaseModel
from enum import Enum

class StyleDirection(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    PLAYFUL = "playful"
    BOLD = "bold"
    MINIMAL = "minimal"
    LUXURY = "luxury"
    HANDCRAFTED = "handcrafted"

class BrandRequest(BaseModel):
    business_id: str                    # UUID — the tenant
    business_name: str                  # e.g. "Naija Drip"
    tagline: str | None = None         # optional, LLM generates if absent
    description: str                    # what the business does, 1–3 sentences
    industry: str                       # e.g. "fashion", "food", "beauty"
    target_audience: str                # e.g. "young professionals in Lagos"
    style_preferences: list[StyleDirection] = []
    existing_colors: list[str] | None = None   # hex codes if they have preferences
    notes: str | None = None           # anything else from conversation
```

### 3.2 Intermediate — `BrandBrief`

```python
class BrandPersonality(BaseModel):
    adjectives: list[str]              # 5 keywords: e.g. ["bold", "urban", "warm"]
    tone_of_voice: str                 # e.g. "confident and approachable"
    visual_direction: str              # e.g. "geometric shapes, high contrast"
    avoid: list[str]                   # e.g. ["clip-art", "overly corporate"]

class BrandBrief(BaseModel):
    business_name: str
    tagline: str                       # generated or provided
    personality: BrandPersonality
    industry_context: str              # relevant conventions
    logo_concept_directions: list[str] # 3 concept briefs for logo gen
    suggested_style: StyleDirection
```

### 3.3 Output — `BrandPackage`

```python
class ColourSwatch(BaseModel):
    name: str                          # e.g. "Primary"
    hex: str                           # "#F36B35"
    rgb: tuple[int, int, int]
    hsl: tuple[int, int, int]
    cmyk: tuple[int, int, int, int]
    role: str                          # e.g. "Primary brand colour"

class FontSpec(BaseModel):
    family: str                        # Google Fonts name
    weights: list[int]                 # e.g. [400, 500, 700]
    role: str                          # "heading" | "body"
    google_fonts_url: str              # import URL
    fallback_stack: str                # e.g. "'Plus Jakarta Sans', sans-serif"

class LogoVariant(BaseModel):
    variant_name: str                  # "primary", "icon", "wordmark", etc.
    svg_key: str                       # S3/R2 object key
    png_keys: dict[int, str]           # {512: "key", 256: "key", ...}

class BrandPackage(BaseModel):
    business_id: str
    brand_brief: BrandBrief
    colours: list[ColourSwatch]        # 6 swatches
    fonts: list[FontSpec]              # 2 fonts (heading + body)
    logo_variants: list[LogoVariant]   # 4–5 variants
    favicon_key: str                   # ICO file in S3/R2
    social_avatars: dict[str, str]     # {"instagram": key, "whatsapp": key, ...}
    guidelines_pdf_key: str            # S3/R2 key for the PDF
    status: str                        # "generated" | "reviewing" | "approved" | "delivered"
    generated_at: str                  # ISO timestamp
    cost_breakdown: dict[str, float]   # {"llm": 0.12, "image_gen": 0.08, ...}
```

---

## 4. Detailed Component Implementation

### 4.1 Brand Strategy Engine — `services/brand/strategy.py`

**Purpose:** Analyse the business description and produce a structured `BrandBrief`.

**LLM:** Claude Sonnet 5.5 (best balance of quality and speed for structured output).

**Prompt template:**

```
You are a brand strategist at a creative studio. Given a business description,
produce a brand brief as a JSON object.

BUSINESS:
- Name: {business_name}
- Description: {description}
- Industry: {industry}
- Target audience: {target_audience}
- Style preferences: {style_preferences}
- Customer notes: {notes}

Produce a JSON object with these exact keys:

{{
  "tagline": "a short, memorable tagline (max 8 words)",
  "personality": {{
    "adjectives": ["5 brand personality keywords"],
    "tone_of_voice": "describe the brand's voice in one sentence",
    "visual_direction": "describe the visual style in one sentence",
    "avoid": ["things this brand should never look or sound like"]
  }},
  "industry_context": "key visual/branding conventions in this industry",
  "logo_concept_directions": [
    "concept 1: brief description of a logo idea",
    "concept 2: brief description of a logo idea",
    "concept 3: brief description of a logo idea"
  ],
  "suggested_style": "one of: modern, classic, playful, bold, minimal, luxury, handcrafted"
}}

RULES:
- The tagline must work for a Nigerian business audience.
- Logo concepts should be simple enough to work as a small favicon.
- Visual direction should be specific (name shapes, patterns, moods), not vague.
- "avoid" must include at least 3 items.
- Return ONLY the JSON, no markdown fences or commentary.
```

**Implementation:**

```python
async def generate_brand_brief(request: BrandRequest) -> BrandBrief:
    prompt = BRAND_STRATEGY_PROMPT.format(
        business_name=request.business_name,
        description=request.description,
        industry=request.industry,
        target_audience=request.target_audience,
        style_preferences=", ".join(request.style_preferences) or "no preference",
        notes=request.notes or "none",
    )
    response = await llm.generate(
        messages=[{"role": "user", "content": prompt}],
        model="claude-sonnet-5-5",
        max_tokens=1024,
        temperature=0.7,
    )
    data = json.loads(response.content)
    return BrandBrief(business_name=request.business_name, **data)
```

**Cost:** ~2,500 input tokens + ~500 output tokens → ~$0.005 per call.

**Fallback:** If JSON parsing fails, retry once with `temperature=0.3` and an
explicit "respond with valid JSON only" suffix. If that fails, use a
minimal default brief derived from the industry field.

---

### 4.2 Colour Palette Generator — `services/brand/colors.py`

**Purpose:** Generate a harmonious, accessible 6-colour palette.

**Approach:** LLM picks seed colours based on the brand brief, then a
deterministic algorithm validates and adjusts them.

**Step 1 — LLM seed generation:**

```
Given this brand brief, suggest a colour palette as a JSON array of 6 objects.
Each object: {{"name": "...", "hex": "#XXXXXX", "role": "..."}}.

Brand personality: {adjectives}
Visual direction: {visual_direction}
Industry: {industry}

Roles (in order): Primary, Secondary, Accent, Neutral, Light Background, Dark Background.

RULES:
- Primary must be vibrant enough to work as a button colour on white.
- Light Background must have lightness > 90% in HSL.
- Dark Background must have lightness < 15% in HSL.
- Neutral must be desaturated (saturation < 15% in HSL).
- All colours must be distinct — no two within 20° hue AND 15% lightness of each other.
- Return ONLY the JSON array.
```

**Step 2 — Deterministic validation (`validate_palette`):**

```python
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colours."""
    def relative_luminance(hex_color: str) -> float:
        r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
        channels = []
        for c in (r, g, b):
            channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def validate_palette(colours: list[ColourSwatch]) -> list[str]:
    """Return list of issues. Empty = pass."""
    issues = []
    primary = next(c for c in colours if c.name == "Primary")
    light_bg = next(c for c in colours if c.name == "Light Background")
    dark_bg = next(c for c in colours if c.name == "Dark Background")

    # WCAG AA: text on background must have contrast >= 4.5:1
    if wcag_contrast_ratio(primary.hex, light_bg.hex) < 4.5:
        issues.append("Primary on Light Background fails WCAG AA (< 4.5:1)")
    if wcag_contrast_ratio(primary.hex, dark_bg.hex) < 4.5:
        issues.append("Primary on Dark Background fails WCAG AA (< 4.5:1)")

    # Check distinctness via CIE2000 delta-E
    for i, c1 in enumerate(colours):
        for c2 in colours[i+1:]:
            rgb1 = sRGBColor(c1.rgb[0]/255, c1.rgb[1]/255, c1.rgb[2]/255)
            rgb2 = sRGBColor(c2.rgb[0]/255, c2.rgb[1]/255, c2.rgb[2]/255)
            lab1 = convert_color(rgb1, LabColor)
            lab2 = convert_color(rgb2, LabColor)
            if delta_e_cie2000(lab1, lab2) < 12:
                issues.append(f"{c1.name} and {c2.name} too similar (ΔE < 12)")

    return issues
```

If validation finds issues, regenerate just the failing colours (up to 2 retries)
by passing the issues back to the LLM with: "Fix these specific problems while
keeping the colours that passed."

**Step 3 — Colour conversion:**

```python
def hex_to_all_formats(hex_color: str) -> ColourSwatch:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    h, s, l = colorsys.rgb_to_hls(r/255, g/255, b/255)
    # CMYK approximation (true CMYK needs ICC profile, but this is close enough for guidelines)
    c = 1 - r/255; m = 1 - g/255; y = 1 - b/255
    k = min(c, m, y)
    if k < 1:
        c, m, y = ((c-k)/(1-k)*100, (m-k)/(1-k)*100, (y-k)/(1-k)*100)
    else:
        c, m, y = (0, 0, 0)
    k *= 100
    return ColourSwatch(
        hex=hex_color, rgb=(r, g, b),
        hsl=(int(h*360), int(s*100), int(l*100)),
        cmyk=(int(c), int(m), int(y), int(k)),
        ...
    )
```

**Cost:** ~1,500 input + ~300 output tokens → ~$0.003. Retry adds $0.003.

---

### 4.3 Typography Selector — `services/brand/typography.py`

**Purpose:** Select a Google Fonts heading + body pairing that fits the brand.

**Approach:** Pre-curate a library of ~40 proven pairings (stored as JSON), then
use the LLM to select the best match.

**Pairing library** (`data/font_pairings.json`):

```json
[
  {
    "id": "jakarta-inter",
    "heading": {"family": "Plus Jakarta Sans", "weights": [600, 700, 800]},
    "body": {"family": "Inter", "weights": [400, 500]},
    "mood": ["modern", "clean", "professional"],
    "industries": ["tech", "saas", "consulting"]
  },
  {
    "id": "fraunces-inter",
    "heading": {"family": "Fraunces", "weights": [400, 500, 700]},
    "body": {"family": "Inter", "weights": [400, 500]},
    "mood": ["warm", "editorial", "premium"],
    "industries": ["food", "hospitality", "beauty"]
  },
  {
    "id": "space-grotesk-dm-sans",
    "heading": {"family": "Space Grotesk", "weights": [500, 700]},
    "body": {"family": "DM Sans", "weights": [400, 500]},
    "mood": ["bold", "geometric", "urban"],
    "industries": ["fashion", "streetwear", "music"]
  }
  // ... 37 more pairings
]
```

**LLM selection prompt:**

```
Given this brand brief and a list of font pairing options, select the best match.
Return ONLY the pairing ID.

Brand: {business_name}
Personality: {adjectives}
Visual direction: {visual_direction}
Industry: {industry}

Options:
{pairings_summary}

If none are a great fit, return the closest match and explain in one sentence why.
```

**Output:** Two `FontSpec` objects + a `google_fonts_url` for the `<link>` tag
and a `font_face_css` snippet.

**Cost:** ~800 input + ~50 output tokens → ~$0.001.

---

### 4.4 Logo Generator — `services/brand/logo.py`

**Purpose:** Generate logo concepts using an image generation API, then process
them into clean, usable assets.

**Recommended API:** Ideogram v3 (`api.ideogram.ai/v1/generate`)

- Best current model for text-in-image rendering (critical for logos with the
  business name).
- $0.03–$0.08 per image depending on resolution and model tier.
- Alternative: DALL-E 3 via OpenAI ($0.04–$0.08/image, weaker at text rendering).
- Fallback: Flux 1.1 Pro via Replicate (~$0.03/image).

**Generation strategy — 3-pass approach:**

**Pass 1 — Concept generation (3 concepts × 2 variants = 6 images):**

```python
LOGO_PROMPT_TEMPLATE = """
A professional logo design for "{business_name}", a {industry} business.
{concept_direction}

Style: {visual_direction}. Colour palette: {primary_hex} (primary), {secondary_hex} (secondary), {accent_hex} (accent) on a clean white background.

Requirements:
- Simple, memorable, works at small sizes (favicon)
- The business name "{business_name}" must be legible
- Flat design, no gradients, no photorealism, no 3D effects
- Vector-style clean edges suitable for SVG conversion
- {avoid_directions}
"""

async def generate_logo_concepts(brief: BrandBrief, colours: list[ColourSwatch]) -> list[str]:
    primary = next(c for c in colours if c.name == "Primary")
    secondary = next(c for c in colours if c.name == "Secondary")
    accent = next(c for c in colours if c.name == "Accent")
    image_urls = []

    for concept in brief.logo_concept_directions:
        prompt = LOGO_PROMPT_TEMPLATE.format(
            business_name=brief.business_name,
            industry=brief.personality.industry_context,
            concept_direction=concept,
            visual_direction=brief.personality.visual_direction,
            primary_hex=primary.hex,
            secondary_hex=secondary.hex,
            accent_hex=accent.hex,
            avoid_directions=", ".join(brief.personality.avoid),
        )
        # Generate 2 variants per concept
        for _ in range(2):
            response = await ideogram_client.generate(
                prompt=prompt,
                model="V_3",
                aspect_ratio="ASPECT_1_1",
                style_type="DESIGN",
                magic_prompt_option="ON",
            )
            image_urls.append(response.data[0].url)

    return image_urls  # 6 images total
```

**Pass 2 — Selection (LLM picks the best):**

Send all 6 images to Claude Sonnet (multimodal) with the brand brief and ask
it to rank them 1–6 with reasoning. Select the top-ranked concept.

```python
async def select_best_logo(images: list[bytes], brief: BrandBrief) -> int:
    content = [{"type": "text", "text": LOGO_SELECTION_PROMPT.format(brief=brief)}]
    for i, img in enumerate(images):
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png",
                       "data": base64.b64encode(img).decode()},
        })
        content.append({"type": "text", "text": f"Logo option {i+1}"})
    response = await llm.generate(
        messages=[{"role": "user", "content": content}],
        model="claude-sonnet-5-5",
        max_tokens=256,
    )
    # Parse ranking from response
    return extract_top_pick(response.content)
```

**Pass 3 — Refinement (1–2 more generations of the winning concept):**

Take the selected concept and generate 2 more variations with tighter prompting
(referencing the specific concept direction, adding "refine", "cleaner lines",
"more balanced composition"). Select the final winner.

**Total images generated per brand:** 6 (concepts) + 2 (refinements) = **8 images**.

**Cost:** 8 × $0.05 avg = **$0.40** for logo generation. Selection LLM call with
6 images ≈ $0.02. Total logo step: **~$0.42 / ₦630**.

---

### 4.5 Asset Renderer — `services/brand/assets.py`

**Purpose:** Take the winning logo image and produce all required format/size
variants, plus social media avatars.

**Pipeline:**

1. **Background removal** — Use `rembg` (local, free) to isolate the logo from
   its background, producing a transparent PNG.

2. **SVG tracing** — Use `vtracer` (Rust-based, local) or Potrace to convert the
   cleaned PNG to SVG vector format. This gives us the scalable source file.

   ```python
   import vtracer
   svg_string = vtracer.convert_image_to_svg_py(
       image_bytes,
       colormode="color",
       filter_speckle=4,
       corner_threshold=60,
       length_threshold=4.0,
       splice_threshold=45,
   )
   ```

3. **PNG size variants** — Render the SVG at 512, 256, 128, 64 px using `cairosvg`:

   ```python
   import cairosvg
   for size in (512, 256, 128, 64):
       png_bytes = cairosvg.svg2png(
           bytestring=svg_bytes,
           output_width=size, output_height=size,
       )
       await storage.upload(f"brands/{business_id}/logo-primary-{size}.png", png_bytes)
   ```

4. **Favicon** — Render at 16 px and 32 px, convert to ICO using `Pillow`:

   ```python
   from PIL import Image
   img16 = Image.open(io.BytesIO(png_16))
   img32 = Image.open(io.BytesIO(png_32))
   ico_buffer = io.BytesIO()
   img16.save(ico_buffer, format="ICO", sizes=[(16, 16), (32, 32)])
   ```

5. **Logo variations** — For icon mark (symbol only) and wordmark (text only),
   use the LLM + image gen to produce separate versions:
   - **Icon mark:** re-prompt the image gen with "icon only, no text, symbol mark"
     using the same concept direction.
   - **Wordmark:** generate using SVG text rendering with the brand's heading font,
     colour-matched. This is deterministic, not AI-generated:

   ```python
   def generate_wordmark_svg(name: str, font: FontSpec, primary: ColourSwatch) -> str:
       return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 80">
         <style>@import url('{font.google_fonts_url}');</style>
         <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle"
               font-family="{font.family}" font-weight="700" font-size="48"
               fill="{primary.hex}">{name}</text>
       </svg>'''
   ```

6. **Social media avatars** — Crop the icon mark into circles at platform sizes:
   - Instagram / Facebook: 400 × 400 px
   - WhatsApp: 320 × 320 px
   - X: 200 × 200 px

   ```python
   from PIL import Image, ImageDraw
   def make_circular_avatar(icon_png: bytes, size: int) -> bytes:
       img = Image.open(io.BytesIO(icon_png)).resize((size, size), Image.LANCZOS)
       mask = Image.new("L", (size, size), 0)
       ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
       img.putalpha(mask)
       buf = io.BytesIO()
       img.save(buf, format="PNG")
       return buf.getvalue()
   ```

7. **Upload all assets** to S3/R2, keyed under `brands/{business_id}/`.

**Dependencies:** `rembg`, `vtracer`, `cairosvg`, `Pillow`. All run locally, no
API costs.

---

### 4.6 Guidelines PDF Builder — `services/brand/guidelines.py`

**Purpose:** Compile all brand elements into a professional-looking PDF.

**Approach:** LLM generates the copy for each page, then WeasyPrint renders
HTML templates into a styled PDF.

**Page structure (8–12 pages):**

| Page | Content |
|---|---|
| 1 | Cover — logo centred, business name, "Brand Guidelines" |
| 2 | Brand story — tagline, personality, tone of voice (from BrandBrief) |
| 3 | Logo — primary logo displayed with clear-space measurements |
| 4 | Logo variations — icon, wordmark, horizontal, stacked |
| 5 | Logo don'ts — "Do not stretch, recolour, add effects, place on busy backgrounds" |
| 6 | Colour palette — all 6 swatches with hex/RGB/CMYK values |
| 7 | Typography — heading + body fonts, weight scale, size ramp |
| 8 | Social media — avatar placement, profile guidelines |
| 9+ | (Optional) Industry-specific: business card mockup, WhatsApp display, storefront signage |

**Implementation:**

```python
async def generate_guidelines_pdf(package: BrandPackage) -> bytes:
    # 1. Generate copy for each section
    copy = await llm.generate(
        messages=[{"role": "user", "content": GUIDELINES_COPY_PROMPT.format(
            brand_brief=package.brand_brief.model_dump_json(),
            colours=[c.model_dump() for c in package.colours],
            fonts=[f.model_dump() for f in package.fonts],
        )}],
        model="claude-haiku-4-5",
        max_tokens=2000,
    )

    # 2. Render HTML template with brand data
    template = jinja_env.get_template("guidelines/base.html")
    html = template.render(
        brand=package.brand_brief,
        colours=package.colours,
        fonts=package.fonts,
        logo_variants=package.logo_variants,
        copy=json.loads(copy.content),
        logo_images={v.variant_name: storage.get_url(v.png_keys[512])
                     for v in package.logo_variants},
    )

    # 3. Convert to PDF
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return pdf_bytes
```

**Template styling:** The HTML template uses the brand's own colours and fonts,
so the guidelines document itself is a demonstration of the brand. CSS
`@page` rules handle margins, page breaks, and consistent headers/footers.

**Cost:** Haiku for copy generation: ~2,000 input + ~1,500 output tokens → ~$0.01.
WeasyPrint: local, free.

---

### 4.7 Quality Gate — `services/brand/quality.py`

Automated checks before the brand enters the approval queue:

```python
def run_quality_checks(package: BrandPackage) -> list[str]:
    issues = []

    # 1. Colour contrast (WCAG AA)
    primary = get_swatch(package, "Primary")
    light_bg = get_swatch(package, "Light Background")
    dark_bg = get_swatch(package, "Dark Background")
    if wcag_contrast_ratio(primary.hex, light_bg.hex) < 4.5:
        issues.append("FAIL: Primary on light bg contrast < 4.5:1")
    if wcag_contrast_ratio(primary.hex, dark_bg.hex) < 4.5:
        issues.append("FAIL: Primary on dark bg contrast < 4.5:1")

    # 2. All required assets exist in storage
    for variant in package.logo_variants:
        if not storage.exists(variant.svg_key):
            issues.append(f"MISSING: SVG for {variant.variant_name}")
        for size, key in variant.png_keys.items():
            if not storage.exists(key):
                issues.append(f"MISSING: PNG {size}px for {variant.variant_name}")

    # 3. PDF exists and is > 100KB (sanity check)
    if not storage.exists(package.guidelines_pdf_key):
        issues.append("MISSING: Guidelines PDF")
    elif storage.size(package.guidelines_pdf_key) < 100_000:
        issues.append("WARN: Guidelines PDF suspiciously small (< 100KB)")

    # 4. Social avatars exist
    for platform, key in package.social_avatars.items():
        if not storage.exists(key):
            issues.append(f"MISSING: {platform} avatar")

    # 5. Font availability
    for font in package.fonts:
        if not google_fonts_exists(font.family):
            issues.append(f"WARN: Font {font.family} not found on Google Fonts")

    return issues
```

If any `FAIL` issues: retry the failing component (up to 2 retries). If `WARN`
issues: flag for human review but don't block. If all clear: push to approval
queue.

---

## 5. File Structure

```
cre8ive-platform/
  services/
    brand/
      __init__.py
      strategy.py          # BrandBrief generation (§4.1)
      colors.py            # Palette generation + validation (§4.2)
      typography.py         # Font pairing selection (§4.3)
      logo.py              # Logo generation orchestration (§4.4)
      assets.py            # SVG/PNG rendering pipeline (§4.5)
      guidelines.py        # PDF builder (§4.6)
      quality.py           # Automated quality checks (§4.7)
      pipeline.py          # Orchestrates the full pipeline end-to-end
      models.py            # Pydantic models (§3)
      prompts.py           # All LLM prompt templates
    brand/templates/
      guidelines/
        base.html          # WeasyPrint HTML template for the PDF
        cover.html         # Cover page partial
        colours.html       # Colour palette page
        typography.html    # Typography page
        logo_usage.html    # Logo rules page
    brand/data/
      font_pairings.json   # Curated pairing library (§4.3)
      industry_defaults.json  # Default style preferences per industry
```

---

## 6. Dependencies

### Python Packages

| Package | Purpose | License |
|---|---|---|
| `anthropic` | Claude API client (strategy, copy, logo selection) | MIT |
| `httpx` | Async HTTP for image gen APIs | BSD |
| `Pillow` | PNG manipulation, avatars, favicon | PIL |
| `cairosvg` | SVG → PNG rendering | LGPL |
| `vtracer` | Raster → SVG vectorisation | MIT |
| `rembg` | Background removal | MIT |
| `weasyprint` | HTML → PDF rendering | BSD |
| `Jinja2` | HTML templating for guidelines | BSD |
| `colormath` | Colour space conversions, ΔE calculations | BSD |
| `pydantic` | Data validation | MIT |

### External APIs

| API | Purpose | Pricing |
|---|---|---|
| Claude Sonnet 5.5 | Brand strategy, logo selection, guidelines copy | ~$3 / 1M input, ~$15 / 1M output |
| Claude Haiku 4.5 | Guidelines copy (cheaper tier) | ~$1 / 1M input, ~$5 / 1M output |
| Ideogram v3 | Logo image generation | ~$0.05 / image |
| Google Fonts API | Font metadata + availability | Free |

### Storage

- **S3-compatible** (Cloudflare R2 recommended — no egress fees): ~$0.015/GB/month
- Per brand package: ~5–15 MB of assets → negligible at scale

---

## 7. Deliverables Checklist

- [ ] `BrandRequest` → `BrandBrief` generation with structured JSON output
- [ ] Colour palette generation with WCAG contrast validation
- [ ] Typography pairing selection from curated library
- [ ] Logo concept generation (3 concepts × 2 variants)
- [ ] Multimodal logo selection (LLM ranks concepts)
- [ ] Logo refinement pass (2 additional variants of winner)
- [ ] Background removal + SVG tracing pipeline
- [ ] PNG rendering at 4 size variants
- [ ] Favicon ICO generation
- [ ] Wordmark SVG generation (deterministic)
- [ ] Icon mark generation (AI)
- [ ] Social media avatar generation (3 platform sizes)
- [ ] Guidelines PDF generation (8+ pages, branded)
- [ ] Automated quality gate (contrast, completeness, format)
- [ ] Full pipeline orchestration (end-to-end in < 5 minutes)
- [ ] Asset upload to S3/R2
- [ ] Integration with Approval Queue
- [ ] Integration with Conversation Service (receive intake, send previews)
- [ ] Error handling + retry logic for all API calls
- [ ] Cost tracking per brand generated

---

## 8. Estimated Timeline

| Week | Tasks |
|---|---|
| **Week 1** | Data models + brand strategy engine + colour palette generator (with validation). Unit tests for colour math and WCAG contrast. |
| **Week 2** | Typography selector + font pairing library. Logo generation pipeline (concept generation + selection). Integration with Ideogram API. |
| **Week 3** | Asset rendering pipeline (rembg → vtracer → cairosvg → Pillow). All format variants. Guidelines PDF template + WeasyPrint rendering. |
| **Week 4** | Quality gate. Full pipeline orchestration. Integration with Approval Queue and Conversation Service. End-to-end testing with 10 diverse business descriptions. |

**Buffer:** 1 week for logo quality iteration (prompt engineering is the biggest
unknown — expect to spend time tuning prompts for consistent, usable logos).

---

## 9. Cost Per Brand Generated

| Component | API Calls | Cost (USD) | Cost (₦) |
|---|---|---|---|
| Brand strategy (Claude Sonnet) | 1 call | $0.005 | ₦7.50 |
| Colour palette (Claude Sonnet) | 1–3 calls | $0.003–$0.009 | ₦4.50–₦13.50 |
| Typography selection (Claude Sonnet) | 1 call | $0.001 | ₦1.50 |
| Logo generation (Ideogram × 8) | 8 images | $0.40 | ₦600 |
| Logo selection (Claude Sonnet multimodal) | 1 call | $0.02 | ₦30 |
| Guidelines copy (Claude Haiku) | 1 call | $0.01 | ₦15 |
| Asset rendering | Local | $0.00 | ₦0 |
| Storage (R2, amortised) | — | $0.001 | ₦1.50 |
| **Total per brand** | | **~$0.44** | **~₦660** |

At a ₦15,000 minimum package price, the brand generation COGS is **~₦660 /
₦15,000 = 4.4%** — leaving **95.6% gross margin** on the AI generation step
alone (before platform costs, support, and human review time).

Even at the most aggressive ₦5,000 entry price (if you ever offer one), COGS
is only 13% — the unit economics are extremely favourable.

**Note:** The main cost driver is logo image generation. If Ideogram prices
change, Flux on Replicate (~$0.03/image) or DALL-E 3 ($0.04/image) are
drop-in alternatives. The provider-agnostic pattern from Balance applies here too.
