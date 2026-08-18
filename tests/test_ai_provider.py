"""
ResumeIQ — Stage 10A AI Provider Abstraction Unit Tests

Covers:
  - Provider routing (local vs gemini)
  - is_ai_available() dependency detection
  - Local provider unavailability (missing torch/transformers)
  - Gemini provider availability check
  - Model load failure: graceful error, no crash
  - call_ai() failure: graceful error propagation
  - Malformed AI output: feature modules return error dicts
  - Deterministic ATS scoring independence from AI provider
  - AI failure does not crash /api/ai/improve endpoint
  - AI failure does not crash /match (dashboard) route
  - is_model_loaded() state tracking
  - reset_model_cache() test isolation helper
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from matcher import final_match_score


class TestProviderRouting(unittest.TestCase):
    """Test that get_active_provider() and call_ai() route to the correct backend."""

    def test_01_default_provider_is_local(self):
        """Without AI_PROVIDER set, get_active_provider() returns 'local'."""
        with patch.dict(os.environ, {}, clear=True):
            from ai.provider import get_active_provider
            provider = get_active_provider()
        self.assertEqual(provider, "local")

    def test_02_local_provider_explicit(self):
        """AI_PROVIDER=local returns 'local'."""
        with patch.dict(os.environ, {"AI_PROVIDER": "local"}):
            from ai.provider import get_active_provider
            provider = get_active_provider()
        self.assertEqual(provider, "local")

    def test_03_gemini_provider_explicit(self):
        """AI_PROVIDER=gemini returns 'gemini'."""
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini"}):
            from ai.provider import get_active_provider
            provider = get_active_provider()
        self.assertEqual(provider, "gemini")

    @patch("ai.local_provider.call_local_model", return_value='{"test": true}')
    @patch("ai.local_provider.is_local_available", return_value=True)
    def test_04_call_ai_routes_to_local(self, mock_avail, mock_call):
        """call_ai() with AI_PROVIDER=local delegates to local_provider."""
        with patch.dict(os.environ, {"AI_PROVIDER": "local"}):
            from ai.provider import call_ai
            result = call_ai("test prompt")
        mock_call.assert_called_once()
        self.assertEqual(result, '{"test": true}')

    @patch("ai.gemini_provider.call_gemini_api", return_value='{"test": true}')
    def test_05_call_ai_routes_to_gemini(self, mock_gemini):
        """call_ai() with AI_PROVIDER=gemini delegates to gemini_provider."""
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "fake-key"}):
            from ai.provider import call_ai
            result = call_ai("test prompt")
        mock_gemini.assert_called_once()
        self.assertEqual(result, '{"test": true}')


class TestIsAiAvailable(unittest.TestCase):
    """Test is_ai_available() correctly reflects provider dependency state."""

    @patch("ai.local_provider.is_local_available", return_value=True)
    def test_06_local_available_when_deps_present(self, mock_avail):
        """is_ai_available() returns True for local when torch+transformers importable."""
        with patch.dict(os.environ, {"AI_PROVIDER": "local"}):
            from ai.provider import is_ai_available
            result = is_ai_available()
        self.assertTrue(result)

    @patch("ai.local_provider.is_local_available", return_value=False)
    def test_07_local_unavailable_when_deps_missing(self, mock_avail):
        """is_ai_available() returns False for local when torch/transformers not importable."""
        with patch.dict(os.environ, {"AI_PROVIDER": "local"}):
            from ai.provider import is_ai_available
            result = is_ai_available()
        self.assertFalse(result)

    def test_08_gemini_available_with_api_key(self):
        """is_ai_available() returns True for gemini when GEMINI_API_KEY is set."""
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "sk-test"}):
            from ai.provider import is_ai_available
            result = is_ai_available()
        self.assertTrue(result)

    def test_09_gemini_unavailable_without_api_key(self):
        """is_ai_available() returns False for gemini when GEMINI_API_KEY is absent."""
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini"}, clear=True):
            # Ensure key is not present
            env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
            env["AI_PROVIDER"] = "gemini"
            with patch.dict(os.environ, env, clear=True):
                from ai.provider import is_ai_available
                result = is_ai_available()
        self.assertFalse(result)


class TestLocalProviderDependencyCheck(unittest.TestCase):
    """Test is_local_available() import-check behavior."""

    def test_10_is_local_available_true_when_torch_importable(self):
        """is_local_available() returns True when torch and transformers are importable."""
        # torch and transformers ARE installed in this environment
        from ai.local_provider import is_local_available
        result = is_local_available()
        self.assertTrue(result)

    def test_11_is_local_available_false_when_import_fails(self):
        """is_local_available() returns False when all local engines fail to import."""
        with patch("ai.local_provider.is_llama_cpp_available", return_value=False), \
             patch("ai.local_provider.is_transformers_available", return_value=False):
            from ai import local_provider
            result = local_provider.is_local_available()
        self.assertFalse(result)


class TestModelLoadFailure(unittest.TestCase):
    """Test graceful handling of model load failures."""

    def setUp(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def tearDown(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def test_12_model_load_failure_raises_runtime_error(self):
        """load_model() raises RuntimeError (not crash) when model download/load fails."""
        with patch("ai.local_provider._load_llama_cpp_model", side_effect=Exception("llama load error")), \
             patch("ai.local_provider._load_transformers_model", side_effect=Exception("transformers load error")):
            from ai.local_provider import load_model
            with self.assertRaises(RuntimeError) as ctx:
                load_model()
            self.assertTrue(
                "Failed to load" in str(ctx.exception) or "No supported" in str(ctx.exception)
            )

    def test_13_call_local_model_propagates_load_error(self):
        """call_local_model() raises RuntimeError if model load fails."""
        with patch("ai.local_provider.load_model",
                   side_effect=RuntimeError("Model unavailable")):
            from ai.local_provider import call_local_model
            with self.assertRaises(RuntimeError) as ctx:
                call_local_model("test prompt")
            self.assertIn("Model unavailable", str(ctx.exception))


class TestFeatureModuleFallback(unittest.TestCase):
    """Test resume_improver and jd_semantic_parser handle provider failures gracefully."""

    def test_14_improve_bullets_returns_error_dict_when_unavailable(self):
        """improve_resume_bullets returns {'available': False, ...} when AI unavailable."""
        with patch("ai.resume_improver.is_ai_available", return_value=False):
            from ai.resume_improver import improve_resume_bullets
            result = improve_resume_bullets("Resume text here.", "Python developer needed.")
        self.assertFalse(result["available"])
        self.assertIsInstance(result["error"], str)
        self.assertEqual(result["improvements"], [])

    def test_15_improve_bullets_returns_error_dict_on_call_failure(self):
        """improve_resume_bullets returns error dict when call_ai raises RuntimeError."""
        with patch("ai.resume_improver.is_ai_available", return_value=True), \
             patch("ai.resume_improver.call_ai",
                   side_effect=RuntimeError("Model load failed")):
            from ai.resume_improver import improve_resume_bullets
            result = improve_resume_bullets(
                "- Built REST APIs using Python and Flask. Delivered 3 microservices.",
                "Senior Python Developer required."
            )
        self.assertTrue(result["available"])
        self.assertIn("Model load failed", result["error"])
        self.assertEqual(result["improvements"], [])

    def test_16_improve_bullets_returns_error_dict_on_malformed_json(self):
        """improve_resume_bullets returns error dict when model returns non-JSON."""
        with patch("ai.resume_improver.is_ai_available", return_value=True), \
             patch("ai.resume_improver.call_ai",
                   return_value="Sorry, I cannot help with that right now."):
            from ai.resume_improver import improve_resume_bullets
            result = improve_resume_bullets(
                "- Built REST APIs using Python and Flask. Delivered 3 microservices.",
                "Senior Python Developer required."
            )
        self.assertTrue(result["available"])
        self.assertIsNotNone(result["error"])
        self.assertIn("JSON", result["error"])
        self.assertEqual(result["improvements"], [])

    def test_17_parse_jd_returns_error_dict_when_unavailable(self):
        """parse_job_description returns {'available': False, ...} when AI unavailable."""
        with patch("ai.jd_semantic_parser.is_ai_available", return_value=False):
            from ai.jd_semantic_parser import parse_job_description
            result = parse_job_description("Senior Python Developer required.")
        self.assertFalse(result["available"])
        self.assertIsInstance(result["error"], str)
        self.assertIsInstance(result["analysis"], dict)

    def test_18_parse_jd_returns_empty_schema_on_call_failure(self):
        """parse_job_description returns empty schema when call_ai raises RuntimeError."""
        with patch("ai.jd_semantic_parser.is_ai_available", return_value=True), \
             patch("ai.jd_semantic_parser.call_ai",
                   side_effect=RuntimeError("Connection timeout")):
            from ai.jd_semantic_parser import parse_job_description
            result = parse_job_description("Senior Python Developer required.")
        self.assertTrue(result["available"])
        self.assertIsNotNone(result["error"])
        self.assertIn("Connection timeout", result["error"])
        self.assertEqual(result["analysis"]["required_skills"], [])

    def test_19_parse_jd_returns_empty_schema_on_malformed_json(self):
        """parse_job_description returns empty schema when model returns non-JSON."""
        with patch("ai.jd_semantic_parser.is_ai_available", return_value=True), \
             patch("ai.jd_semantic_parser.call_ai",
                   return_value="Here is a summary of the job..."):
            from ai.jd_semantic_parser import parse_job_description
            result = parse_job_description("Senior Python Developer required.")
        self.assertTrue(result["available"])
        self.assertIsNotNone(result["error"])
        self.assertIn("JSON", result["error"])


class TestEndpointIsolation(unittest.TestCase):
    """Test Flask endpoints behave correctly across provider states."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("app.is_ai_available", return_value=False)
    def test_20_improve_endpoint_503_when_unavailable(self, mock_avail):
        """POST /api/ai/improve returns 503 when AI provider is unavailable."""
        response = self.client.post(
            "/api/ai/improve",
            json={"resume_text": "Built REST APIs.", "job_description": "Python job."}
        )
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertFalse(data["available"])

    @patch("app.is_ai_available", return_value=False)
    def test_21_parse_jd_endpoint_503_when_unavailable(self, mock_avail):
        """POST /api/ai/parse-jd returns 503 when AI provider is unavailable."""
        response = self.client.post(
            "/api/ai/parse-jd",
            json={"job_description": "Senior Python Developer."}
        )
        self.assertEqual(response.status_code, 503)

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai", side_effect=RuntimeError("Model crashed"))
    def test_22_improve_endpoint_500_on_provider_crash(self, mock_call, mock_avail):
        """POST /api/ai/improve returns 500 when AI call throws RuntimeError."""
        response = self.client.post(
            "/api/ai/improve",
            json={
                "resume_text": "- Built REST APIs with Python and Flask for web services.",
                "job_description": "Senior Python Developer required."
            }
        )
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("Model crashed", data.get("error", ""))

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai", return_value="not valid json at all")
    def test_23_improve_endpoint_500_on_malformed_output(self, mock_call, mock_avail):
        """POST /api/ai/improve returns 500 when model returns malformed JSON."""
        response = self.client.post(
            "/api/ai/improve",
            json={
                "resume_text": "- Built REST APIs with Python and Flask for web services.",
                "job_description": "Senior Python Developer required."
            }
        )
        self.assertEqual(response.status_code, 500)


class TestDeterministicIndependence(unittest.TestCase):
    """Verify deterministic ATS scoring is completely independent of AI provider state."""

    def test_24_ats_score_unchanged_local_provider(self):
        """ATS score is identical regardless of AI_PROVIDER setting."""
        resume = "Python software engineer. Flask, Docker, PostgreSQL, REST API."
        jd = "Senior Python Developer with Flask, Docker, PostgreSQL, REST API experience."

        with patch.dict(os.environ, {"AI_PROVIDER": "local"}):
            result_local = final_match_score(resume, jd)

        with patch.dict(os.environ, {"AI_PROVIDER": "gemini"}):
            result_gemini = final_match_score(resume, jd)

        self.assertAlmostEqual(result_local["ats_score"], result_gemini["ats_score"], places=2)
        self.assertAlmostEqual(result_local["skill_score"], result_gemini["skill_score"], places=2)

    def test_25_ats_score_unchanged_ai_completely_disabled(self):
        """ATS score works correctly with no AI provider at all."""
        resume = "Python engineer, 5 years. Flask, PostgreSQL, Docker."
        jd = "Python developer needed. Flask, PostgreSQL, Docker required."
        result = final_match_score(resume, jd)
        self.assertIn("ats_score", result)
        self.assertGreater(result["ats_score"], 70.0)
        self.assertEqual(result["skill_score"], 100.0)

    def test_26_gap_analysis_works_without_ai(self):
        """analyze_resume_job_gap completes fully without AI (deterministic only)."""
        from gap_analyzer import analyze_resume_job_gap
        resume = "Python engineer. Flask, PostgreSQL, Docker."
        jd = "Python developer needed. Flask, Docker, Redis required. PostgreSQL a plus."
        result = analyze_resume_job_gap(resume, jd)
        self.assertIn("skill_coverage", result)
        self.assertIn("roadmap", result)
        self.assertIsNone(result.get("ai_roadmap"))  # AI roadmap is None without AI

    @patch("gap_analyzer.is_ai_available", return_value=False)
    def test_27_enhance_gap_analysis_noop_when_ai_unavailable(self, mock_avail):
        """enhance_gap_analysis_with_ai returns original gap_analysis unchanged when unavailable."""
        from gap_analyzer import analyze_resume_job_gap, enhance_gap_analysis_with_ai
        resume = "Python engineer. Flask, PostgreSQL."
        jd = "Python developer. Flask, PostgreSQL, Redis required."
        original_gap = analyze_resume_job_gap(resume, jd)
        original_score = original_gap["skill_coverage"]["coverage_percentage"]

        enhanced_gap = enhance_gap_analysis_with_ai(original_gap, jd)
        self.assertEqual(
            enhanced_gap["skill_coverage"]["coverage_percentage"],
            original_score
        )
        # AI roadmap stays None when provider unavailable
        self.assertIsNone(enhanced_gap.get("ai_roadmap"))

    def test_28_health_endpoint_does_not_load_ai_model(self):
        """GET /health returns 200 without loading the AI model."""
        app.config["TESTING"] = True
        client = app.test_client()

        with patch("ai.local_provider.load_model") as mock_load:
            response = client.get("/health")
            # load_model must NOT be called during health check
            mock_load.assert_not_called()

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")


class TestModelCacheManagement(unittest.TestCase):
    """Test is_model_loaded() and reset_model_cache() utilities."""

    def setUp(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def tearDown(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def test_29_is_model_loaded_false_initially(self):
        """is_model_loaded() returns False before any load attempt."""
        from ai.local_provider import is_model_loaded
        self.assertFalse(is_model_loaded())

    def test_30_is_model_loaded_true_after_mock_load(self):
        """is_model_loaded() returns True after model singleton is populated."""
        import ai.local_provider as lp
        lp._model = MagicMock()
        lp._tokenizer = MagicMock()
        self.assertTrue(lp.is_model_loaded())

    def test_31_reset_cache_clears_model_state(self):
        """reset_model_cache() clears model, tokenizer, and error state."""
        import ai.local_provider as lp
        lp._model = MagicMock()
        lp._tokenizer = MagicMock()
        lp._model_load_error = "previous error"

        lp.reset_model_cache()

        self.assertIsNone(lp._model)
class TestJsonExtractor(unittest.TestCase):
    """Test _extract_json_block helper function in local_provider."""

    def test_32_extract_json_block_pure_json(self):
        """Pure JSON text is returned untouched."""
        from ai.local_provider import _extract_json_block
        raw = '{"key": "value", "count": 1}'
        self.assertEqual(_extract_json_block(raw), raw)

    def test_33_extract_json_block_strips_thinking_tags(self):
        """Thinking tags <think>...</think> are stripped."""
        from ai.local_provider import _extract_json_block
        raw = '<think>Internal reasoning here.</think>\n{"key": "value"}'
        self.assertEqual(_extract_json_block(raw), '{"key": "value"}')

    def test_34_extract_json_block_strips_markdown_fences(self):
        """Markdown ```json ... ``` codeblocks are stripped."""
        from ai.local_provider import _extract_json_block
        raw = '```json\n{"key": "value"}\n```'
        self.assertEqual(_extract_json_block(raw), '{"key": "value"}')

    def test_35_extract_json_block_with_surrounding_text(self):
        """Extracts JSON object when surrounded by conversational text."""
        from ai.local_provider import _extract_json_block
        raw = 'Here is your requested output:\n{"key": "value"}\nHope this helps!'
        self.assertEqual(_extract_json_block(raw), '{"key": "value"}')


class TestTokenLimitsAndStrictFallback(unittest.TestCase):
    """Test token limit configuration and strict fallback safety."""

    def setUp(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def tearDown(self):
        from ai.local_provider import reset_model_cache
        reset_model_cache()

    def test_36_strict_fallback_fails_fast_when_llama_cpp_missing(self):
        """Default backend fails fast when llama_cpp is unavailable without silent Transformers fallback."""
        with patch("ai.local_provider.is_llama_cpp_available", return_value=False):
            from ai.local_provider import load_model
            with self.assertRaises(RuntimeError) as ctx:
                load_model()
            self.assertIn("llama-cpp-python is required", str(ctx.exception))

    def test_37_explicit_transformers_backend_loads_transformers(self):
        """LOCAL_BACKEND=transformers triggers transformers loader explicitly."""
        with patch.dict(os.environ, {"LOCAL_BACKEND": "transformers"}), \
             patch("ai.local_provider.is_transformers_available", return_value=True), \
             patch("ai.local_provider._load_transformers_model", return_value=(MagicMock(), MagicMock())):
            from ai.local_provider import load_model, _engine_type
            res = load_model()
            from ai import local_provider
            self.assertEqual(local_provider._engine_type, "transformers")

    def test_38_call_ai_passes_custom_max_tokens(self):
        """call_ai passes custom max_tokens parameter to local provider."""
        with patch.dict(os.environ, {"AI_PROVIDER": "local"}), \
             patch("ai.local_provider.call_local_model", return_value='{"test": 1}') as mock_call:
            from ai.provider import call_ai
            call_ai("prompt", max_tokens=192)
            mock_call.assert_called_once_with("prompt", max_new_tokens=192, temperature=0.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
