import os
from dotenv import dotenv_values, set_key, unset_key
from typing import Dict, Any
from loguru import logger

class ConfigService:
    """Manages loading and saving of .env file configurations.
    
    In Docker environments, prioritizes environment variables over .env file.
    """

    def __init__(self, dotenv_path: str = ".env"):
        # In Docker, .env is mounted at /app/.env
        # For local dev, it's at project root
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..", dotenv_path),  # Local: backend/src/services/../../../.env
            "/app/.env",  # Docker mount
            os.path.join(os.getcwd(), dotenv_path),  # Fallback to current working dir
        ]
        
        self.dotenv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.dotenv_path = path
                break
        
        if self.dotenv_path is None:
            # Use Docker path as default
            self.dotenv_path = "/app/.env"
            logger.warning(f".env file not found, creating at {self.dotenv_path}")
            os.makedirs(os.path.dirname(self.dotenv_path), exist_ok=True)
            open(self.dotenv_path, 'a').close()
        else:
            logger.debug(f"ConfigService initialized. Using .env at: {self.dotenv_path}")

    def load_configuration(self) -> Dict[str, Any]:
        """
        Loads configuration from environment variables (Docker) or .env file (local).
        
        Priority:
        1. Environment variables (for Docker)
        2. .env file values (for local development)
        
        In Docker mode, constructs proper URLs from HOST/PORT variables.

        Returns:
            A dictionary containing the current configuration.
        """
        # Check if running in Docker (environment variables are set)
        if os.getenv("CHROMA_HOST") or os.getenv("REDIS_HOST"):
            logger.info("Running in Docker mode - using environment variables")
            # Return environment variables as config
            config = dict(os.environ)
            
            # Construct proper URLs for Docker networking
            # CHROMA_HOST=chromadb + CHROMA_PORT=8000 → http://chromadb:8000
            chroma_host = os.getenv("CHROMA_HOST", "chromadb")
            chroma_port = os.getenv("CHROMA_PORT", "8000")
            if not chroma_host.startswith("http"):
                config["CHROMA_HOST"] = f"http://{chroma_host}:{chroma_port}"
            
            # OLLAMA_HOST should already be full URL from docker-compose
            ollama_host = os.getenv("OLLAMA_HOST")
            if ollama_host and not ollama_host.startswith("http"):
                config["OLLAMA_HOST"] = f"http://{ollama_host}:11434"
            
            logger.info(f"Docker config: CHROMA_HOST={config.get('CHROMA_HOST')}, OLLAMA_HOST={config.get('OLLAMA_HOST')}")
            return config
        
        # Fallback to .env file for local development
        logger.info(f"Running in local mode - loading configuration from {self.dotenv_path}")
        config = dotenv_values(self.dotenv_path)
        logger.debug(f"Loaded configuration: {config}")
        return config

    def save_configuration(self, config_data: Dict[str, Any]) -> bool:
        """
        Saves the given configuration data to the .env file.

        Args:
            config_data: The configuration dictionary to save.

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Saving configuration to {self.dotenv_path}")
        try:
            # Migration: DATABASE_URL -> lea_database_url
            if 'DATABASE_URL' in config_data and not config_data.get('lea_database_url'):
                config_data['lea_database_url'] = config_data['DATABASE_URL']

            # Ensure old key is removed from .env
            if 'DATABASE_URL' in config_data:
                try:
                    unset_key(self.dotenv_path, 'DATABASE_URL')
                except Exception as e:
                    logger.warning(f"Unable to unset DATABASE_URL: {e}")

            for key, value in config_data.items():
                # set_key handles creating the file if it doesn't exist
                # and updates the key if exists, or adds it if it doesn't.
                set_key(self.dotenv_path, key, str(value))
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

config_service = ConfigService()
