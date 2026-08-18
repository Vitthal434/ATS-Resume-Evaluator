"""
ResumeIQ — Gemini LLM Provider Service
Encapsulates Gemini API communication and handles environment authentication safely.
"""

import json
import os
import urllib.error
import urllib.request


def is_gemini_available() -> bool:
    """Return True if GEMINI_API_KEY environment variable is set."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    return bool(key)


def call_gemini_api(prompt: str, timeout: int = 15) -> str:
    """
    Call Gemini API endpoint with prompt text.
    Returns the raw response text from the model.
    Raises RuntimeError if key is missing or API call fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

    # Using Gemini 1.5 Flash REST endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidates = result.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            raise RuntimeError("Gemini API returned empty content candidates.")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini API HTTP Error {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Gemini API Network Error: {e.reason}") from e
    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {str(e)}") from e
