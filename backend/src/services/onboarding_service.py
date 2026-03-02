"""
Onboarding service for the Developer Edition.
Handles the initial setup and introduction for new users.
"""
from typing import Dict, Any
from src.core.feature_limits import FeatureLimits, Edition
from loguru import logger


class OnboardingService:
    """
    Handles onboarding for new users of the Developer Edition.
    """
    
    def __init__(self, edition: Edition = Edition.DEVELOPER):
        self.edition = edition
    
    def get_welcome_message(self) -> Dict[str, Any]:
        """
        Get the welcome message for the current edition.
        """
        limits = FeatureLimits.get_limits(self.edition)

        welcome_msg = {
            "title": "Welcome to PantheonRAG-Mail v1.0 - Developer Edition",
            "subtitle": "Your Personal Knowledge Base",
            "edition": self.edition.value,
            "features": {
                "collections_limit": limits["max_collections"],
                "documents_per_collection": limits["max_documents_per_collection"],
                "file_formats": limits["allowed_file_formats"],
                "advanced_rag": limits["enable_advanced_rag"],
                "learning_system": limits["enable_learning_system"],
                "team_sharing": limits["enable_team_sharing"],
            },
            "welcome_text": self._get_welcome_text(),
            "next_steps": self._get_next_steps(),
            "limitations": self._get_limitations(),
            "upgrade_cta": self._get_upgrade_cta()
        }

        return welcome_msg

    def _get_welcome_text(self) -> str:
        """
        Get the welcome text based on the edition.
        """
        if self.edition == Edition.DEVELOPER:
            return (
                "Hello! Welcome to PantheonRAG-Mail v1.0 - Developer Edition. "
                "This free version allows you to build a personal knowledge base "
                "on your computer and receive intelligent email responses. "
                "Simply drag a folder with your documents here to get started."
            )
        else:
            return (
                "Welcome to PantheonRAG-Mail! "
                "You are using the {self.edition.value.title()} Edition with advanced features."
            )
    
    def _get_next_steps(self) -> list:
        """
        Get the next steps for the user based on the edition.
        """
        if self.edition == Edition.DEVELOPER:
            return [
                {
                    "step": 1,
                    "title": "Create Your First Knowledge Collection",
                    "description": "Click 'Create New Collection' and give your knowledge collection a name.",
                    "action": "create_collection"
                },
                {
                    "step": 2,
                    "title": "Add Documents",
                    "description": "Drag a folder with PDF documents into the app or upload individual files.",
                    "action": "add_documents"
                },
                {
                    "step": 3,
                    "title": "Ask Your First Question",
                    "description": "Ask a question about your documents in the chat field below.",
                    "action": "ask_question"
                },
                {
                    "step": 4,
                    "title": "Generate Your First Email",
                    "description": "Connect your email account and test automatic response generation.",
                    "action": "connect_email"
                }
            ]
        else:
            return [
                {
                    "step": 1,
                    "title": "Create Your Knowledge Collections",
                    "description": "Create multiple collections for different topics or departments.",
                    "action": "create_collections"
                },
                {
                    "step": 2,
                    "title": "Add Documents",
                    "description": "Add a variety of document formats including PDF, DOCX, TXT and more.",
                    "action": "add_documents"
                },
                {
                    "step": 3,
                    "title": "Invite Team Members",
                    "description": "Invite colleagues and collaborate on your knowledge base together.",
                    "action": "invite_team"
                }
            ]

    def _get_limitations(self) -> Dict[str, Any]:
        """
        Get the limitations for the current edition.
        """
        limits = FeatureLimits.get_limits(self.edition)

        limitations = {
            "collections": f"You can create a maximum of {limits['max_collections']} knowledge collection{'s' if limits['max_collections'] != 1 else ''}.",
            "documents": f"Each collection can contain a maximum of {limits['max_documents_per_collection']} document{'s' if limits['max_documents_per_collection'] != 1 else ''}.",
            "formats": f"You can only process {', '.join(limits['allowed_file_formats'])} files.",
            "advanced_features": {
                "advanced_rag": f"Advanced RAG features: {'Available' if limits['enable_advanced_rag'] else 'Not available (upgrade required)'}",
                "learning_system": f"Learning system: {'Available' if limits['enable_learning_system'] else 'Not available (upgrade required)'}",
                "team_sharing": f"Team sharing: {'Available' if limits['enable_team_sharing'] else 'Not available (upgrade required)'}"
            }
        }

        return limitations

    def _get_upgrade_cta(self) -> Dict[str, str]:
        """
        Get the upgrade call-to-action for the current edition.
        """
        if self.edition == Edition.DEVELOPER:
            return {
                "title": "Want More Features?",
                "description": "Upgrade to Team Edition for unlimited collections, advanced RAG features and team access.",
                "button_text": "Upgrade to Team Edition Now",
                "link": "/upgrade"
            }
        else:
            return {
                "title": "Everything Under Control!",
                "description": "You are already using a powerful edition with advanced features.",
                "button_text": "Back to App",
                "link": "/dashboard"
            }


# Global instance for the onboarding service
onboarding_service = OnboardingService()