from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest

from backend.database.database import Base, engine
from backend.database import models as _database_models  # noqa: F401


@pytest.fixture(autouse=True)
def recriar_schema_teste() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
