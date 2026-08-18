"""
ResumeIQ — Local Open-Source AI Provider
Runs optimized inference against open-source instruction-tuned models.

Primary engine : llama-cpp-python with quantized GGUF (fastest CPU execution)
Default model  : Qwen/Qwen2.5-0.5B-Instruct-GGUF (qwen2.5-0.5b-instruct-q5_k_m.gguf) — Apache-2.0
Alternative    : Qwen/Qwen3-0.6B-GGUF (Qwen3-0.6B-Q8_0.gguf)
Fallback engine: HuggingFace Transformers (explicit opt-in via LOCAL_BACKEND=transformers)

Configuration via Environment Variables:
  - LOCAL_BACKEND      : 'auto' (default: llama_cpp), 'llama_cpp', or 'transformers'
  - GGUF_REPO_ID       : HuggingFace repo for GGUF model (default: 'Qwen/Qwen2.5-0.5B-Instruct-GGUF')
  - GGUF_FILENAME      : GGUF filename (default: 'qwen2.5-0.5b-instruct-q5_k_m.gguf')
  - GGUF_MODEL_PATH    : Direct local filepath to a .gguf file (optional override)
  - MODEL_NAME         : Transformers model ID (default: 'Qwen/Qwen3-0.6B')
  - AI_BULLET_MAX_TOKENS: Max tokens for resume bullet optimization (default: 256)
  - AI_JD_MAX_TOKENS   : Max tokens for JD semantic parsing (default: 384)
  - AI_TEMPERATURE     : Sampling temperature (default: 0.1)

Key behaviors:
  - Model is lazily loaded on first inference call.
  - Singleton cache: model loads once per process lifetime.
  - Thread-safe: uses a module-level lock during initial load.
  - CPU-friendly: lightweight quantized GGUF weights, no GPU requirement.
  - Strict fallback: does NOT silently fall back to slow Transformers unless explicitly configured.
  - Thinking tokens stripped automatically for reasoning models.
"""

import os
import re
import threading
from typing import Optional, Tuple, Any

DEFAULT_GGUF_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
DEFAULT_GGUF_FILE = "qwen2.5-0.5b-instruct-q5_k_m.gguf"
DEFAULT_TRANSFORMERS_MODEL = "Qwen/Qwen3-0.6B"

_engine_type: Optional[str] = None  # 'llama_cpp' or 'transformers'
_llama_model: Optional[Any] = None
_tokenizer: Optional[Any] = None
_transformers_model: Optional[Any] = None
_model: Optional[Any] = None
_model_load_error: Optional[str] = None
_model_lock = threading.Lock()


def is_llama_cpp_available() -> bool:
    """Return True if llama_cpp is importable."""
    try:
        import llama_cpp  # noqa: F401
        return True
    except ImportError:
        return False


def is_transformers_available() -> bool:
    """Return True if torch and transformers are importable."""
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False


def is_local_available() -> bool:
    """
    Return True if the configured local inference engine is importable.
    By default, requires llama_cpp for fast CPU inference.
    If LOCAL_BACKEND=transformers, checks for torch and transformers.
    """
    backend = os.environ.get("LOCAL_BACKEND", "auto").strip().lower()
    if backend == "transformers":
        return is_transformers_available()
    if backend == "llama_cpp":
        return is_llama_cpp_available()
    return is_llama_cpp_available() or (backend == "auto" and is_transformers_available())


def is_model_loaded() -> bool:
    """Return True if a local model singleton has been successfully loaded."""
    return (
        (_model is not None)
        or (_llama_model is not None)
        or (_transformers_model is not None and _tokenizer is not None)
    )


def _get_cpu_threads() -> int:
    """Determine optimal CPU thread count for llama.cpp."""
    try:
        count = os.cpu_count() or 4
        return max(1, min(count, 6))
    except Exception:
        return 4


def _load_llama_cpp_model() -> Any:
    """Load and return llama_cpp.Llama instance."""
    from huggingface_hub import hf_hub_download
    import llama_cpp

    local_path = os.environ.get("GGUF_MODEL_PATH", "").strip()
    if not local_path or not os.path.isfile(local_path):
        repo_id = os.environ.get("GGUF_REPO_ID", DEFAULT_GGUF_REPO).strip()
        filename = os.environ.get("GGUF_FILENAME", DEFAULT_GGUF_FILE).strip()
        local_path = hf_hub_download(repo_id=repo_id, filename=filename)

    threads = int(os.environ.get("LLAMA_THREADS", str(_get_cpu_threads())))
    llm = llama_cpp.Llama(
        model_path=local_path,
        n_ctx=2048,
        n_threads=threads,
        verbose=False,
    )
    return llm


def _load_transformers_model() -> Tuple[Any, Any]:
    """Load and return (tokenizer, model) for Transformers fallback."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name = os.environ.get("MODEL_NAME", DEFAULT_TRANSFORMERS_MODEL).strip()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
    )
    model.eval()
    return tokenizer, model


def load_model() -> Any:
    """
    Lazy-load and cache the local model singleton.
    Prioritizes llama_cpp (GGUF). Does not silently fall back to slow Transformers
    unless LOCAL_BACKEND=transformers is explicitly configured.
    Thread-safe via module lock.
    """
    global _engine_type, _llama_model, _tokenizer, _transformers_model, _model, _model_load_error

    if is_model_loaded():
        if _engine_type == "llama_cpp":
            return _llama_model
        return _tokenizer, _transformers_model

    if _model_load_error is not None:
        raise RuntimeError(f"Local AI model load previously failed: {_model_load_error}")

    with _model_lock:
        if is_model_loaded():
            if _engine_type == "llama_cpp":
                return _llama_model
            return _tokenizer, _transformers_model

        backend = os.environ.get("LOCAL_BACKEND", "auto").strip().lower()

        # Explicit opt-in for Transformers
        if backend == "transformers":
            if is_transformers_available():
                try:
                    _tokenizer, _transformers_model = _load_transformers_model()
                    _engine_type = "transformers"
                    _model = _transformers_model
                    return _tokenizer, _transformers_model
                except Exception as exc:
                    _model_load_error = str(exc)
                    raise RuntimeError(f"Failed to load local AI model via transformers: {exc}") from exc
            else:
                _model_load_error = "LOCAL_BACKEND=transformers requested but torch/transformers is not installed."
                raise RuntimeError(_model_load_error)

        # Default ('auto' or 'llama_cpp'): strictly use llama_cpp for fast CPU inference
        if is_llama_cpp_available():
            try:
                _llama_model = _load_llama_cpp_model()
                _engine_type = "llama_cpp"
                _model = _llama_model
                return _llama_model
            except Exception as exc:
                _model_load_error = str(exc)
                raise RuntimeError(f"Failed to load GGUF model via llama_cpp: {exc}") from exc

        _model_load_error = (
            "llama-cpp-python is required for local AI inference. "
            "Please install llama-cpp-python or configure AI_PROVIDER=gemini."
        )
        raise RuntimeError(_model_load_error)


def _extract_json_block(text: str) -> str:
    """Extract valid JSON from raw text, removing think tags and markdown fences."""
    clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()

    try:
        import json
        json.loads(clean)
        return clean
    except Exception:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", clean, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            import json
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    return clean


def call_local_model(
    prompt: str,
    max_new_tokens: int = 384,
    temperature: float = 0.1,
) -> str:
    """
    Run inference against the loaded local model with the given prompt.
    Returns decoded clean text stripped of thinking tags and markdown code blocks.
    """
    load_res = load_model()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise AI assistant. "
                "Respond ONLY with valid JSON. "
                "Do not include markdown code fences, explanations, "
                "or any text outside the JSON object."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    if _engine_type == "llama_cpp":
        llm = _llama_model
        try:
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
            )
            raw_output = response["choices"][0]["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"llama_cpp inference failed: {exc}") from exc

    else:
        # Transformers path
        import torch

        tokenizer, model = _tokenizer, _transformers_model
        try:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        inputs = tokenizer(text, return_tensors="pt")
        gen_kwargs: dict = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": tokenizer.eos_token_id,
        }
        if temperature > 0:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = temperature
        else:
            gen_kwargs["do_sample"] = False

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_kwargs)

        new_ids = outputs[0][inputs.input_ids.shape[1]:]
        raw_output = tokenizer.decode(new_ids, skip_special_tokens=True)

    return _extract_json_block(raw_output)


def reset_model_cache() -> None:
    """
    Clear the model singleton. Intended for testing only.
    """
    global _engine_type, _llama_model, _tokenizer, _transformers_model, _model, _model_load_error
    with _model_lock:
        _engine_type = None
        _llama_model = None
        _tokenizer = None
        _transformers_model = None
        _model = None
        _model_load_error = None
