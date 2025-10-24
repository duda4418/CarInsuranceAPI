"""SQLAlchemy base class and metadata for models."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Deterministic names for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    metadata = metadata

    def __repr__(self) -> str:
        """String representation with class name and id."""
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__} id={pk!r}>"
