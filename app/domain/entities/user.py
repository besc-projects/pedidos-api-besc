from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Domain representation of an application user."""

    username: str
    email: str
    hashed_password: str
    company: Optional[str] = None
    id: Optional[int] = None
