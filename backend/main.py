import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Service, ServiceCheck
from backend.monitor import monitoring_loop
from backend.schemas import ServiceCheckRead, ServiceCreate, ServiceRead


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(monitoring_loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_db)]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/services", response_model=ServiceRead, status_code=201)
def create_service(payload: ServiceCreate, db: SessionDep) -> Service:
    service = Service(**payload.model_dump(mode="json"))
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@app.get("/services", response_model=list[ServiceRead])
def list_services(db: SessionDep) -> list[Service]:
    return list(db.scalars(select(Service).order_by(Service.id)))


@app.get("/services/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: SessionDep) -> Service:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.delete("/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: SessionDep) -> None:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()


@app.get("/services/{service_id}/checks", response_model=list[ServiceCheckRead])
def list_service_checks(
    service_id: int,
    db: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ServiceCheck]:
    if db.get(Service, service_id) is None:
        raise HTTPException(status_code=404, detail="Service not found")
    query = (
        select(ServiceCheck)
        .where(ServiceCheck.service_id == service_id)
        .order_by(ServiceCheck.checked_at.desc())
        .limit(limit)
    )
    return list(db.scalars(query))
