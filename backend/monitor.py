import asyncio
import logging
import time

import httpx
from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import Service, ServiceCheck

TIMEOUT_SECONDS = 10.0
TICK_SECONDS = 5

logger = logging.getLogger(__name__)


async def check_service(service: Service) -> ServiceCheck:
    """Send GET to the service URL and describe the result (not saved here)."""
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(service.url)
    except httpx.HTTPError as exc:
        return ServiceCheck(
            service_id=service.id,
            status="DOWN",
            error=f"{type(exc).__name__}: {exc}",
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    return ServiceCheck(
        service_id=service.id,
        status="UP" if response.status_code < 400 else "DOWN",
        status_code=response.status_code,
        response_time_ms=round(elapsed_ms, 1),
    )


async def monitoring_loop() -> None:
    """Every few seconds, check the services whose interval has elapsed."""
    last_checked: dict[int, float] = {}
    while True:
        try:
            with SessionLocal() as db:
                services = list(db.scalars(select(Service)))

            now = time.monotonic()
            due = [
                s for s in services
                if s.id not in last_checked or now - last_checked[s.id] >= s.check_interval
            ]
            checks = await asyncio.gather(*(check_service(s) for s in due))

            with SessionLocal() as db:
                db.add_all(checks)
                db.commit()
            for s in due:
                last_checked[s.id] = now
        except Exception:
            logger.exception("Monitoring iteration failed")

        await asyncio.sleep(TICK_SECONDS)
