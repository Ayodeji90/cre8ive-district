from __future__ import annotations

import re

from website_agent.domain.spec import QualityIssue, QualityReport


class WebsiteQualityChecker:
    """Verifies that generated site files pass structural, accessibility, SEO, and WhatsApp standards."""

    def check(self, file_tree: dict[str, str]) -> QualityReport:
        issues: list[QualityIssue] = []
        html_files = {k: v for k, v in file_tree.items() if k.endswith(".html")}

        if not html_files:
            return QualityReport(
                passed=False,
                score=0,
                issues=[
                    QualityIssue(
                        severity="error",
                        check="html_presence",
                        message="No HTML files were generated",
                    )
                ],
            )

        score = 100

        # Check 1: index.html must exist
        if "index.html" not in html_files:
            issues.append(
                QualityIssue(
                    severity="error", check="entrypoint", message="Missing index.html entrypoint"
                )
            )
            score -= 20

        # Check each HTML page
        for filename, content in html_files.items():
            # DOCTYPE and HTML tags
            if "<!DOCTYPE html>" not in content:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        check="doctype",
                        message=f"{filename}: Missing <!DOCTYPE html>",
                    )
                )
                score -= 3

            if '<meta name="viewport"' not in content:
                issues.append(
                    QualityIssue(
                        severity="error",
                        check="viewport",
                        message=f"{filename}: Missing mobile viewport meta tag",
                    )
                )
                score -= 10

            # Meta description
            if '<meta name="description"' not in content:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        check="seo_meta",
                        message=f"{filename}: Missing meta description",
                    )
                )
                score -= 5

            # Title
            title_match = re.search(r"<title>(.*?)</title>", content)
            if not title_match or not title_match.group(1).strip():
                issues.append(
                    QualityIssue(
                        severity="error",
                        check="title",
                        message=f"{filename}: Missing or empty <title> tag",
                    )
                )
                score -= 10

            # WhatsApp CTA presence
            if "wa.me/" not in content:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        check="whatsapp_cta",
                        message=f"{filename}: Missing WhatsApp link CTA",
                    )
                )
                score -= 5

            # Check internal links resolution
            internal_links = re.findall(r'href="([a-zA-Z0-9_-]+\.html)"', content)
            for link in internal_links:
                if link not in file_tree:
                    issues.append(
                        QualityIssue(
                            severity="error",
                            check="broken_link",
                            message=f"{filename}: Broken internal link to {link}",
                        )
                    )
                    score -= 10

        # Check CSS variable definitions
        sample_html = next(iter(html_files.values()))
        if "--brand-primary:" not in sample_html:
            issues.append(
                QualityIssue(
                    severity="warning",
                    check="brand_tokens",
                    message="Missing --brand-primary CSS token",
                )
            )
            score -= 5

        # Bound score between 0 and 100
        final_score = max(0, min(100, score))
        has_errors = any(i.severity == "error" for i in issues)

        return QualityReport(
            passed=not has_errors and final_score >= 80,
            score=final_score,
            issues=issues,
        )
