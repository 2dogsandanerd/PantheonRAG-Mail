"""
Feature limits for different editions of the application.
"""

from typing import Dict, Any, Optional
from enum import Enum
import os


class Edition(Enum):
    DEVELOPER = "developer"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class FeatureLimits:
    """
    Defines feature limits based on the edition of the application.
    """
    
    # Default limits for Developer Edition
    DEFAULT_LIMITS = {
        # Collection limits
        "max_collections": 1,
        "max_documents_per_collection": 100,
        "max_total_documents": 100,
        
        # File format limits
        "allowed_file_formats": [".pdf"],  # Only PDF in free version
        "max_file_size_mb": 10,
        
        # Feature flags
        "enable_advanced_rag": False,
        "enable_cross_encoder_reranking": False,
        "enable_learning_system": False,
        "enable_auto_draft": False,
        "enable_multi_collection_search": False,
        "enable_ranked_collections": False,
        "enable_batch_processing": False,
        "enable_team_sharing": False,
        "enable_advanced_analytics": False,
        
        # Performance limits
        "max_concurrent_queries": 1,
        "query_timeout_seconds": 30,
        
        # API rate limits (per hour)
        "api_query_limit": 1000,
    }
    
    # Limits for Team Edition
    TEAM_LIMITS = {
        # Collection limits
        "max_collections": 10,
        "max_documents_per_collection": 5000,
        "max_total_documents": 10000,
        
        # File format limits
        "allowed_file_formats": [".pdf", ".docx", ".txt", ".md", ".html"],
        "max_file_size_mb": 50,
        
        # Feature flags
        "enable_advanced_rag": True,
        "enable_cross_encoder_reranking": True,
        "enable_learning_system": True,
        "enable_auto_draft": True,
        "enable_multi_collection_search": True,
        "enable_ranked_collections": True,
        "enable_batch_processing": True,
        "enable_team_sharing": True,
        "enable_advanced_analytics": True,
        
        # Performance limits
        "max_concurrent_queries": 5,
        "query_timeout_seconds": 60,
        
        # API rate limits (per hour)
        "api_query_limit": 5000,
    }
    
    # Limits for Enterprise Edition
    ENTERPRISE_LIMITS = {
        # Collection limits
        "max_collections": -1,  # Unlimited
        "max_documents_per_collection": -1,  # Unlimited
        "max_total_documents": -1,  # Unlimited
        
        # File format limits
        "allowed_file_formats": [".pdf", ".docx", ".txt", ".md", ".html", ".pptx", ".xlsx", ".rtf"],
        "max_file_size_mb": 100,
        
        # Feature flags
        "enable_advanced_rag": True,
        "enable_cross_encoder_reranking": True,
        "enable_learning_system": True,
        "enable_auto_draft": True,
        "enable_multi_collection_search": True,
        "enable_ranked_collections": True,
        "enable_batch_processing": True,
        "enable_team_sharing": True,
        "enable_advanced_analytics": True,
        
        # Performance limits
        "max_concurrent_queries": 10,
        "query_timeout_seconds": 120,
        
        # API rate limits (per hour)
        "api_query_limit": -1,  # Unlimited
    }
    
    EDITION_LIMITS = {
        Edition.DEVELOPER: DEFAULT_LIMITS,
        Edition.TEAM: TEAM_LIMITS,
        Edition.ENTERPRISE: ENTERPRISE_LIMITS,
    }
    
    @classmethod
    def get_limits(cls, edition: Edition = None) -> Dict[str, Any]:
        """
        Get feature limits for the specified edition.
        
        Args:
            edition: Edition to get limits for. If None, uses environment variable.
            
        Returns:
            Dictionary of feature limits
        """
        if edition is None:
            edition_str = os.getenv("EDITION", "developer").lower()
            try:
                edition = Edition(edition_str)
            except ValueError:
                edition = Edition.DEVELOPER  # Default to developer edition
        
        return cls.EDITION_LIMITS.get(edition, cls.DEFAULT_LIMITS)
    
    @classmethod
    def is_feature_enabled(cls, feature: str, edition: Edition = None) -> bool:
        """
        Check if a specific feature is enabled for the edition.
        
        Args:
            feature: Feature name to check
            edition: Edition to check against. If None, uses environment variable.
            
        Returns:
            True if feature is enabled, False otherwise
        """
        limits = cls.get_limits(edition)
        return limits.get(f"enable_{feature.lower()}", False)
    
    @classmethod
    def get_limit_value(cls, limit_name: str, edition: Edition = None) -> Any:
        """
        Get the value of a specific limit for the edition.
        
        Args:
            limit_name: Name of the limit to check
            edition: Edition to check against. If None, uses environment variable.
            
        Returns:
            Value of the limit
        """
        limits = cls.get_limits(edition)
        return limits.get(limit_name, None)
    
    @classmethod
    def check_document_limit(cls, current_count: int, edition: Edition = None) -> bool:
        """
        Check if adding a document would exceed the limit.
        
        Args:
            current_count: Current number of documents
            edition: Edition to check against. If None, uses environment variable.
            
        Returns:
            True if within limit, False if limit would be exceeded
        """
        max_docs = cls.get_limit_value("max_documents_per_collection", edition)
        if max_docs == -1:  # Unlimited
            return True
        return current_count < max_docs
    
    @classmethod
    def check_collection_limit(cls, current_count: int, edition: Edition = None) -> bool:
        """
        Check if creating a collection would exceed the limit.
        
        Args:
            current_count: Current number of collections
            edition: Edition to check against. If None, uses environment variable.
            
        Returns:
            True if within limit, False if limit would be exceeded
        """
        max_collections = cls.get_limit_value("max_collections", edition)
        if max_collections == -1:  # Unlimited
            return True
        return current_count < max_collections