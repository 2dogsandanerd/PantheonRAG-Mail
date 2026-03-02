"""
Database models for Multi-Tenancy and Access Control.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON, Float, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from .models import Base, User  # Import existing Base and User

# --- Enums ---

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

# --- Models ---

class Tenant(Base):
    """
    Tenant (Organization) model.
    Represents a customer or organization in the multi-tenant system.
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # Internal name (slug)
    display_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    # Quotas & Limits
    max_collections = Column(Integer, default=5)
    max_queries_per_day = Column(Integer, default=1000)
    max_api_keys = Column(Integer, default=5)
    
    # Features (JSON for flexibility)
    features = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant")
    api_keys = relationship("APIKey", back_populates="tenant")
    usage_records = relationship("TenantUsage", back_populates="tenant")
    collection_acls = relationship("CollectionACL", back_populates="tenant")


class CollectionACL(Base):
    """
    Access Control List for Collections.
    Defines which roles can access which collection within a tenant.
    """
    __tablename__ = "collection_acl"

    id = Column(Integer, primary_key=True, index=True)
    collection_name = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Access Control
    allowed_roles = Column(JSON, default=["admin", "user"])  # List of allowed roles
    is_public = Column(Boolean, default=False)  # If true, accessible by all tenant users
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="collection_acls")

    __table_args__ = (
        UniqueConstraint('collection_name', 'tenant_id', name='uix_collection_tenant'),
    )


class APIKey(Base):
    """
    API Key for programmatic access.
    Keys are hashed for security.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Security
    key_hash = Column(String, unique=True, index=True, nullable=False)  # SHA-256 hash
    key_prefix = Column(String(20), nullable=False)  # First few chars for display (e.g. "sk-abc...")
    name = Column(String, nullable=False)
    
    # Permissions
    scopes = Column(JSON, default=["read"])
    
    # Limits
    rate_limit = Column(Integer, default=100)  # Requests per minute
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")


class TenantUsage(Base):
    """
    Daily usage tracking for billing and quotas.
    """
    __tablename__ = "tenant_usage"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    date = Column(DateTime, nullable=False)  # Date only
    
    # Metrics
    query_count = Column(Integer, default=0)
    document_count = Column(Integer, default=0)
    token_usage = Column(BigInteger, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="usage_records")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'date', name='uix_tenant_date'),
    )
