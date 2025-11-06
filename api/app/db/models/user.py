"""
SQLModel for User management
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class UserBase(SQLModel):
    """Base model for User with common fields"""
    username: str = Field(
        unique=True, 
        index=True, 
        description="Unique username for user"
    )
    pin_hash: str = Field(
        description="Hashed PIN for authentication"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Timestamp when user was created"
    )
    last_login: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp of last login"
    )


class User(UserBase, table=True):
    """User table model"""
    __tablename__ = "users"
    
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for user"
    )
    
    # Relationships
    provas: List["Prova"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"lazy": "select"}
    )


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pin: str = Field(description="Plain text PIN (will be hashed)")


class UserRead(UserBase):
    """Schema for reading user data"""
    id: UUID = Field(description="Unique identifier for user")