from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from website_agent.domain.spec import SiteSpec

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


class LayoutAssembler:
    """Assembles SiteSpec into a production-ready file tree of static HTML/CSS/assets."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self._base_css = self._read_file(STATIC_DIR / "base.css")

    def _read_file(self, path: Path) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _load_theme_css(self, theme_name: str) -> str:
        theme_path = STATIC_DIR / "themes" / f"{theme_name}.css"
        return self._read_file(theme_path)

    def assemble(self, site: SiteSpec) -> dict[str, str]:
        """Returns dict of {relative_file_path: file_content}."""
        files: dict[str, str] = {}
        theme_css = self._load_theme_css(site.theme.value)
        current_year = datetime.now(UTC).year

        template = self._env.get_template("base.html")

        # 1. Render all HTML pages
        for page in site.pages:
            html = template.render(
                site=site,
                page=page,
                theme_css=theme_css,
                base_css=self._base_css,
                current_year=current_year,
            )
            filename = f"{page.slug}.html" if not page.slug.endswith(".html") else page.slug
            files[filename] = html

        # 2. Add site.css (for standalone reference or CDN caching)
        files["assets/site.css"] = f"{theme_css}\n{self._base_css}"

        # 3. Add logo asset if provided
        if site.brand.logo_svg:
            files["assets/logo.svg"] = site.brand.logo_svg

        # 4. Add robots.txt
        files["robots.txt"] = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"

        # 5. Add sitemap.xml
        base_url = (
            f"https://{site.subdomain}.cre8ive.ng"
            if site.subdomain
            else "https://cre8ivedistrict.com"
        )
        sitemap_items = "\n".join(
            f"  <url><loc>{base_url}/{p.slug}.html</loc><changefreq>weekly</changefreq></url>"
            for p in site.pages
        )
        files["sitemap.xml"] = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{sitemap_items}\n"
            f"</urlset>"
        )

        return files
