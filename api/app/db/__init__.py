"""
Database module for SQLModel models
"""

from .models.prova import Prova, ProvaCreate, ProvaUpdate, ProvaRead
from .models.user import User, UserCreate, UserRead

__all__ = [
    "Prova",
    "ProvaCreate", 
    "ProvaUpdate",
    "ProvaRead",
    "User",
    "UserCreate",
    "UserRead"
]