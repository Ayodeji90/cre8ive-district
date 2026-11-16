from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from website_agent.persistence.models import Base, SiteJobModel


class SiteJobRepository:
    def __init__(self, database_url: str) -> None:
        self._engine = create_async_engine(database_url, echo=False)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def initialize(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_site(
        self,
        site_id: uuid.UUID,
        business_id: uuid.UUID | None,
        spec_dict: dict,
        files_dict: dict,
        quality_dict: dict,
    ) -> SiteJobModel:
        async with self._session_factory() as session:
            job = SiteJobModel(
                id=site_id,
                business_id=business_id,
                status="generated",
                spec_json=spec_dict,
                files_json=files_dict,
                quality_json=quality_dict,
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def get_site(self, site_id: uuid.UUID) -> SiteJobModel | None:
        async with self._session_factory() as session:
            return await session.get(SiteJobModel, site_id)

    async def update_deployment(self, site_id: uuid.UUID, deployment_dict: dict) -> None:
        async with self._session_factory() as session:
            job = await session.get(SiteJobModel, site_id)
            if job:
                job.deployment_json = deployment_dict
                job.status = "deployed"
                await session.commit()

    async def update_failure(self, site_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            job = await session.get(SiteJobModel, site_id)
            if job:
                job.status = "failed"
                await session.commit()

    async def close(self) -> None:
        await self._engine.dispose()
