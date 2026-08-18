"""
ResumeIQ — AI Provider Abstraction Layer
Routes AI inference calls to the configured backend provider.

Primary provider: 'local' (open-source, Apache-2.0, no API key required)
Secondary provider: 'gemini' (requires GEMINI_API_KEY, optional)

Configuration:
    AI_PROVIDER=local   (default) — uses Qwen3-0.6B via local transformers
    AI_PROVIDER=gemini            — uses Gemini 1.5 Flash REST API

This module is the ONLY entry point that feature modules (resume_improver,
jd_semantic_parser, gap_analyzer) should import from. Never import
gemini_provider or local_provider directly in feature code.
"""

import os


def get_active_provider() -> str:
    """
    Return the configured AI provider name ('local' or 'gemini').
    Defaults to 'local' if AI_PROVIDER is not set.
    """
    return os.environ.get("AI_PROVIDER", "local").strip().lower()


def is_ai_available() -> bool:
    """
    Return True if the configured AI provider's prerequisites are satisfied.

    For 'local': returns True if torch and transformers are importable.
    For 'gemini': returns True if GEMINI_API_KEY environment variable is set.

    This check does NOT load the model or make any network calls.
    It only confirms that the provider's dependencies are present.

    Note: A True return from this function means the provider *can be attempted*,
    not that inference will necessarily succeed. Model-load failures are surfaced
    gracefully at inference time, not here.
    """
    provider = get_active_provider()

    if provider == "gemini":
        from ai.gemini_provider import is_gemini_available
        return is_gemini_available()

    # Default: local provider
    from ai.local_provider import is_local_available
    return is_local_available()


from typing import Optional


def call_ai(prompt: str, timeout: int = 60, max_tokens: Optional[int] = None) -> str:
    """
    Call the configured AI provider with the given prompt string.

    Returns the raw string response from the model.
    Raises RuntimeError if the provider is unavailable or the call fails.

    The 'timeout' parameter is advisory for network providers (Gemini).
    For local providers it is ignored.
    """
    provider = get_active_provider()

    if provider == "gemini":
        from ai.gemini_provider import call_gemini_api
        return call_gemini_api(prompt, timeout=timeout)

    # Default: local provider
    from ai.local_provider import call_local_model
    if max_tokens is None:
        max_tokens = int(os.environ.get("AI_MAX_NEW_TOKENS", "384"))
    temperature = float(os.environ.get("AI_TEMPERATURE", "0.1"))
    return call_local_model(prompt, max_new_tokens=max_tokens, temperature=temperature)
