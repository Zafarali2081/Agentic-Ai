"""Configuration and LLM Client initialization.

This module handles:
1. Loading environment variables securely (never hardcoding keys in code).
2. Setting up the LLM client (Groq, GitHub Models, or OpenAI API).
3. Providing fallback awareness so the project works both online and offline.
"""

import os
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


def get_api_credentials() -> Tuple[Optional[str], str, str]:
    """Retrieve API credentials and configuration from environment variables.

    Priority:
    1. GROQ_API_KEY (Groq fast inference endpoint)
    2. GITHUB_TOKEN (GitHub Models free endpoint)
    3. OPENAI_API_KEY (Standard OpenAI endpoint)

    Auto-detects keys:
    - If a key begins with 'gsk_', it routes to Groq automatically.

    Returns:
        tuple: (api_key, base_url, model_name)
    """
    groq_key = os.getenv("GROQ_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")

    # 1. Check GROQ_API_KEY
    if groq_key and groq_key != "your_groq_api_key_here":
        api_key = groq_key
        base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        return api_key, base_url, model

    # 2. Check GITHUB_TOKEN
    if github_token and github_token != "your_github_token_here":
        # Auto-detect if user put a groq key here
        if github_token.startswith("gsk_"):
            base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
            model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
            return github_token, base_url, model

        api_key = github_token
        base_url = os.getenv("LLM_BASE_URL", "https://models.inference.ai.azure.com")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        return api_key, base_url, model

    # 3. Check OPENAI_API_KEY
    if openai_key and openai_key != "your_openai_api_key_here":
        # Auto-detect if user put a groq key here
        if openai_key.startswith("gsk_"):
            base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
            model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
            return openai_key, base_url, model

        api_key = openai_key
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        return api_key, base_url, model

    # No active key detected -> default fallback configuration
    return None, "", "openai/gpt-oss-120b"


def get_llm_client():
    """Create and return an OpenAI-compatible client, or None if no key is found."""
    api_key, base_url, _ = get_api_credentials()

    if not api_key:
        return None

    try:
        from openai import OpenAI
        if base_url:
            return OpenAI(api_key=api_key, base_url=base_url)
        return OpenAI(api_key=api_key)
    except ImportError:
        print("[Warning] 'openai' package not installed. Run: pip install openai")
        return None


def get_model_name() -> str:
    """Return the configured model name."""
    _, _, model = get_api_credentials()
    return model
