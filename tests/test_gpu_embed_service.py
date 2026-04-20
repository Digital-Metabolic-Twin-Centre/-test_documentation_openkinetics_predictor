#!/usr/bin/env python3
"""Unit tests for GPU embedding precompute orchestration helpers."""

from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


class _FakeRedis:
    def set(self, *args, **kwargs):
        return None

    def get(self, *args, **kwargs):
        return None

    def delete(self, *args, **kwargs):
        return None


fake_progress_service = types.ModuleType("api.services.progress_service")
fake_progress_service.redis_conn = _FakeRedis()
sys.modules["api.services.progress_service"] = fake_progress_service

from api.services import gpu_embed_service as ges  # noqa: E402


class GpuEmbedServiceTests(unittest.TestCase):
    def test_gpu_submit_sparse_steps_and_tracker_order(self):
        plan = SimpleNamespace(
            need_computation=2,
            gpu_supported=True,
            gpu_reason=None,
            profile="kinform_full",
            seq_id_to_seq={"sid_1": "AAAA", "sid_2": "BBBB"},
        )

        events: list[str] = []

        def _http_side_effect(method, url, payload=None, timeout=5.0):
            events.append(f"http:{method}:{url}")
            if method == "POST":
                self.assertIn("step_work", payload)
                self.assertEqual(
                    payload["step_work"],
                    {
                        "kinform_esm2_layers": ["sid_1"],
                        "kinform_prott5_layers": ["sid_2"],
                    },
                )
                self.assertEqual(payload["seq_id_to_seq"], {"sid_1": "AAAA", "sid_2": "BBBB"})
                return {"job_id": "job_1"}
            return {"status": "done"}

        with patch.object(ges, "build_embedding_plan", return_value=plan):
            with patch.object(
                ges,
                "gpu_step_work",
                return_value={"kinform_esm2_layers": ["sid_1"], "kinform_prott5_layers": ["sid_2"]},
            ):
                with patch.object(ges, "_base_url", return_value="http://gpu"):
                    with patch.object(ges, "get_gpu_status", return_value={"online": True}):
                        with patch.object(
                            ges,
                            "start_embedding_tracking",
                            side_effect=lambda **_: events.append("start_tracking"),
                        ):
                            with patch.object(ges, "_http_json", side_effect=_http_side_effect):
                                result = ges.run_gpu_precompute_if_available(
                                    job_public_id="job_x",
                                    method_key="KinForm-H",
                                    target="kcat",
                                    valid_sequences=["AAAA", "BBBB"],
                                    env={},
                                )

        self.assertTrue(result.used_gpu)
        self.assertTrue(result.completed)
        self.assertFalse(result.failed)
        self.assertEqual(events[0], "start_tracking")
        self.assertTrue(events[1].startswith("http:POST:"))

    def test_gpu_timeout_is_fail_open(self):
        plan = SimpleNamespace(
            need_computation=1,
            gpu_supported=True,
            gpu_reason=None,
            profile="turnup_esm1b",
            seq_id_to_seq={"sid_1": "AAAA"},
        )

        with patch.object(ges, "build_embedding_plan", return_value=plan):
            with patch.object(ges, "gpu_step_work", return_value={"turnup_esm1b": ["sid_1"]}):
                with patch.object(ges, "_base_url", return_value="http://gpu"):
                    with patch.object(ges, "get_gpu_status", return_value={"online": True}):
                        with patch.object(ges, "start_embedding_tracking", return_value=True):
                            with patch.object(ges, "_http_json", return_value={"job_id": "job_1"}):
                                with patch.object(ges, "_poll_job", return_value={"status": "timeout"}):
                                    result = ges.run_gpu_precompute_if_available(
                                        job_public_id="job_y",
                                        method_key="TurNup",
                                        target="kcat",
                                        valid_sequences=["AAAA"],
                                        env={},
                                    )

        self.assertTrue(result.used_gpu)
        self.assertFalse(result.completed)
        self.assertTrue(result.failed)
        self.assertEqual(result.reason, "timeout")

    def test_gpu_status_cache_and_unconfigured(self):
        with patch.object(ges, "_base_url", return_value=""):
            status = ges.get_gpu_status(force_refresh=True)
        self.assertFalse(status["configured"])

        mock_http = Mock(return_value={"online": True, "gpu_name": "RTX A4500", "free_vram_gb": 8.0})
        with patch.object(ges, "_base_url", return_value="http://gpu"):
            with patch.object(ges, "_http_json", mock_http):
                status1 = ges.get_gpu_status(force_refresh=True)
                status2 = ges.get_gpu_status(force_refresh=False)

        self.assertEqual(mock_http.call_count, 1)
        self.assertTrue(status1["online"])
        self.assertEqual(status2["gpu_name"], "RTX A4500")


if __name__ == "__main__":
    unittest.main()
