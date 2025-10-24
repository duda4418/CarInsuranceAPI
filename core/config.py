"""Shared Pydantic configuration utilities.

Provides camelCase aliasing while keeping internal snake_case attribute names.
Clients can send either camelCase or snake_case. Responses default to camelCase.
"""

from pydantic import BaseModel, ConfigDict


def to_camel(s: str) -> str:
    """Convert snake_case string to camelCase string."""
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    """Base model enabling camelCase aliases and dual input support.

    - Internal attribute names remain snake_case.
    - Incoming JSON may use snake_case or camelCase.
    - Outgoing JSON (FastAPI responses) uses camelCase by default.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
