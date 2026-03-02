"""
API Documentation Configuration for Mail Modul Alpha

This module provides extended configuration for FastAPI's built-in documentation
and additional tools for documenting the API endpoints.

The configuration includes:
1. Custom metadata for the API
2. Extended OpenAPI schema definition
3. Documentation generation utilities
4. API specification export functions
"""

from fastapi import FastAPI
from typing import Dict, Any
import json
import yaml
from pathlib import Path

# Extended API metadata
API_METADATA = {
    "title": "PantheonMail API",
    "description": """
    # PantheonMail API Documentation

    Welcome to the API documentation for PantheonMail - an AI-powered email assistant
    that combines Retrieval-Augmented Generation (RAG) with multi-provider LLM support to
    automatically generate intelligent email draft responses.

    ## 🚀 Features
    - **Multi-Provider Email Support**: Gmail (OAuth2) or IMAP/SMTP
    - **Multi-Provider LLM**: OpenAI, Gemini, Ollama, Anthropic
    - **RAG System**: ChromaDB Vector Store for contextual responses
    - **Smart Draft Generation**: Automatic response suggestions with LLM
    - **Learning System**: Learns from your corrections (Supervised Learning)
    - **Privacy First**: Everything runs locally, no data leaves your computer

    ## 🔐 Authentication
    All endpoints require authentication via JWT tokens. Include the token in the
    Authorization header as "Bearer {token}".

    ## 📨 Rate Limiting
    API endpoints are subject to rate limiting to ensure fair usage and system stability.

    ## 🛡️ Security
    All data processing happens locally. Only LLM providers receive prompts (if used).
    """,
    "version": "1.0.0",
    "terms_of_service": "http://example.com/terms/",
    "contact": {
        "name": "API Support",
        "email": "support@yourcompany.com",
        "url": "http://www.yourcompany.com/support"
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
}

def export_openapi_spec(app: FastAPI, output_dir: str = "./docs/api") -> Dict[str, str]:
    """
    Export the OpenAPI specification in both JSON and YAML formats.
    
    Args:
        app: The FastAPI application instance
        output_dir: Directory to save the API specification files
        
    Returns:
        Dictionary with paths to the generated files
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Export as JSON
    json_path = Path(output_dir) / "openapi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    # Export as YAML
    yaml_path = Path(output_dir) / "openapi.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(openapi_schema, f, default_flow_style=False, allow_unicode=True)
    
    return {
        "json": str(json_path),
        "yaml": str(yaml_path)
    }

def generate_api_documentation_summary(app: FastAPI) -> Dict[str, Any]:
    """
    Generate a summary of the API documentation.
    
    Args:
        app: The FastAPI application instance
        
    Returns:
        Summary dictionary containing API information
    """
    openapi_schema = app.openapi()
    
    # Count endpoints by method
    endpoint_counts = {}
    total_endpoints = 0
    
    for path, methods in openapi_schema.get("paths", {}).items():
        for method in methods.keys():
            method_upper = method.upper()
            endpoint_counts[method_upper] = endpoint_counts.get(method_upper, 0) + 1
            total_endpoints += 1
    
    return {
        "api_info": openapi_schema.get("info", {}),
        "total_endpoints": total_endpoints,
        "endpoints_by_method": endpoint_counts,
        "available_paths": list(openapi_schema.get("paths", {}).keys()),
        "schemas_count": len(openapi_schema.get("components", {}).get("schemas", {})),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "openapi_yaml": "/openapi.yaml"
        }
    }

# Example usage function
def setup_documentation_hooks(app: FastAPI):
    """
    Setup documentation hooks for the FastAPI application.
    
    This function should be called during the application initialization
    to enable extended documentation features.
    """
    # Add custom API routes for documentation
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi():
        return app.openapi()
    
    @app.get("/documentation-summary", include_in_schema=False)
    async def get_documentation_summary():
        return generate_api_documentation_summary(app)
    
    # Export documentation on startup (optional)
    # export_openapi_spec(app)

if __name__ == "__main__":
    # This section demonstrates how to use the documentation tools
    print("API Documentation Configuration")
    print("=" * 40)
    print("This module provides utilities for API documentation generation.")
    print("Use the functions in your main application to enhance API docs.")