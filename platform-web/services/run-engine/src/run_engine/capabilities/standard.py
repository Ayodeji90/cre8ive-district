from __future__ import annotations

import logging

from run_engine.domain.run import BusinessContext, RunTask

logger = logging.getLogger(__name__)


class BrandImprovementCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        focus = task.input_data.get("focus", "positioning")
        logger.info("Executing brand improvement for %s (focus: %s)", context.business_name, focus)
        return {
            "focus": focus,
            "status": "improved",
            "tagline_suggestion": f"{context.business_name} — Crafted for Growth.",
            "voice_notes": ["Confident", "Culturally resonant", "Pragmatic"],
            "recommendations": [
                "Align website copy with revised value proposition",
                "Update social media bios to reflect brand pillars",
            ],
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Delivering brand improvement: %s", task.title)


class WebsiteImprovementCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        section = task.input_data.get("section", "hero")
        logger.info(
            "Executing website improvement for %s (section: %s)", context.business_name, section
        )
        return {
            "section": section,
            "optimized_headline": f"Build and scale your {context.industry or 'business'} faster with {context.business_name}",
            "optimized_subheadline": "Trusted, streamlined, and built to turn interest into customers.",
            "cta_button": task.input_data.get("cta", "Get Started Today"),
            "target_url": context.website_url,
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Publishing website improvement to %s", task.channel or "website")


class SocialPostCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        platform = task.input_data.get("platform", "instagram")
        format_type = task.input_data.get("format", "single_image")
        logger.info(
            "Drafting social post for %s on %s (%s)", context.business_name, platform, format_type
        )
        return {
            "platform": platform,
            "format": format_type,
            "caption": (
                f"Big things are taking shape at {context.business_name}! 🚀 "
                f"We are helping {context.target_audience or 'our customers'} thrive with effortless solutions. "
                "Drop your thoughts below or click the link in bio to explore more! #Cre8iveDistrict #Growth"
            ),
            "media_prompt": f"Minimalist, elegant promotional visual for {context.business_name} in {context.industry} style",
            "scheduled_for": None,
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Publishing social post to %s", result.get("platform"))


class OutreachEmailCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        target = task.input_data.get("target_segment", "prospective partners")
        logger.info(
            "Drafting cold outreach email for %s targeting %s", context.business_name, target
        )
        return {
            "target_segment": target,
            "subject": f"Quick question regarding your creative & growth needs — {context.business_name}",
            "body": (
                "Hi there,\n\n"
                f"I noticed your impressive work and wanted to connect. At {context.business_name}, we specialize in "
                f"delivering modern, high-impact brand and digital experiences tailored for businesses like yours.\n\n"
                "Would you be open to a brief 5-minute chat this week to share notes?\n\n"
                f"Warm regards,\nTeam {context.business_name}"
            ),
            "intended_recipients_count": 1,
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Delivering outreach email draft to approval/sending queue")


class CompetitorResearchCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        logger.info("Conducting competitor research for %s", context.business_name)
        return {
            "industry": context.industry,
            "competitors_analyzed": context.known_competitors or ["Industry benchmark standard"],
            "differentiators": [
                "Faster delivery and direct founder support",
                "Seamless local payment options (Paystack)",
                "Full-stack AI autonomy paired with human creative review",
            ],
            "opportunities": [
                "Highlight localized trust signals on marketing pages",
                "Offer transparent pricing models compared to manual agencies",
            ],
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Storing competitor research insights")


class ContentCreationCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        topic = task.input_data.get("topic", "Industry Guide")
        return {
            "topic": topic,
            "article_title": f"The Modern Guide to Thriving in {context.industry or 'Business'}",
            "summary": "Key insights on brand positioning, digital distribution, and customer trust.",
            "sections": [
                "1. Identifying Your Edge",
                "2. Building Consistency",
                "3. Converting Visitors",
            ],
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Publishing created content to CMS/Blog")


class SEOOptimizationCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        return {
            "keywords": [
                f"{context.business_name}",
                f"best {context.industry}",
                "Lagos digital brand agency",
            ],
            "meta_description": f"Discover {context.business_name}: innovative branding, digital presence, and high-impact strategy.",
            "title_tag": f"{context.business_name} | Modern Digital Brand Solutions",
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Updated SEO metadata for task %s", task.id)


class AnalyticsReviewCapability:
    async def execute(self, task: RunTask, context: BusinessContext) -> dict:
        return {
            "orders": context.total_orders,
            "revenue": context.total_revenue,
            "reply_rate": context.outreach_reply_rate,
            "summary": "Key conversion channels are healthy. Recommend doubling down on social engagement.",
        }

    async def deliver(self, task: RunTask, result: dict) -> None:
        logger.info("Logged analytics review")
