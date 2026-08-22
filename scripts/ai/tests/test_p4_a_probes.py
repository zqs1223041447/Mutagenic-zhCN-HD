"""P4-A lane A contract tests: probes exist, evidence parses and passes.

Static + artifact-level checks only; the heavy lifting runs headless via
scripts/validate/p4_a_*.py CLIs (see migration/conversion/p4_a_*.json).
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]


def _evidence(name: str) -> dict:
    path = REPO / "migration" / "conversion" / name
    if not path.exists():
        pytest.skip(f"evidence not generated yet: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def test_p4a_probe_files_exist():
    for rel in [
        "product/scenes/GUI/Feedback/FeedbackConfig.gd",
        "product/scenes/GUI/Feedback/VignetteOverlay.gd",
        "product/scenes/GUI/Feedback/EnemyFeedbackController.gd",
        "product/scenes/Player/PlayerCamera.gd",
        "product/Shaders/hit_flash.gdshader",
        "product/scenes/Levels/_validate/p4_a_feedback_driver.gd",
        "product/scenes/Levels/_validate/p4_a_position_driver.gd",
        "scripts/validate/p4_a_readability_probe.py",
        "scripts/validate/p4_a_position_probe.py",
    ]:
        assert (REPO / rel).exists(), f"missing {rel}"


def test_feedback_config_is_single_source_of_truth():
    src = (REPO / "product/scenes/GUI/Feedback/FeedbackConfig.gd").read_text(encoding="utf-8")
    for token in ["shake_amplitude", "hitstop_duration", "kill_zoom_amount",
                  "vignette_peak_alpha", "hit_flash_duration"]:
        assert token in src, f"config missing {token}"


def test_c2_consumes_position_readonly():
    base = (REPO / "product/scenes/Levels/BaseLevel.gd").read_text(encoding="utf-8")
    assert "apply_saved_player_position" in base
    # read-only consumption: no writes into the saved position field here
    assert '["position"] =' not in base and '["position"]=' not in base


def test_readability_evidence_pass():
    data = _evidence("p4_a_readability_feedback.json")
    result = data.get("result") or {}
    assert data.get("verdict") == "PASS"
    assert result.get("pass") is True
    r1 = result.get("r1") or {}
    r2 = result.get("r2") or {}
    for key in ["enemy_flash_fired", "enemy_flash_restored", "elite_marker_attached",
                "vignette_fired", "vignette_restored"]:
        assert r1.get(key) is True, key
    for key in ["camera_present", "kill_zoom_fired", "kill_zoom_restored",
                "shake_fired", "shake_restored", "hitstop_engaged", "time_scale_restored"]:
        assert r2.get(key) is True, key


def test_position_apply_evidence_pass():
    data = _evidence("p4_a_position_apply.json")
    result = data.get("result") or {}
    assert data.get("verdict") == "PASS"
    assert result.get("pass") is True
    apply = result.get("apply") or {}
    absence = result.get("absence") or {}
    assert apply.get("save_records_position") is True
    assert apply.get("position_applied") is True
    assert absence.get("default_spawn_kept") is True
