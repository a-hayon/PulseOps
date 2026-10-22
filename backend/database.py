import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    database=os.environ["POSTGRES_DB"],
)

engine = create_engine(database_url, connect_args={"connect_timeout": 5})

SessionLocal = sessionmaker(bind=engine)

def get_db() -> Iterator[Session]:
    """Give each request its own session, closed once the request is done."""
    with SessionLocal() as session:
        yield session
