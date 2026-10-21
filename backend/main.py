from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Service
from backend.schemas import ServiceCreate, ServiceRead

app = FastAPI()

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
