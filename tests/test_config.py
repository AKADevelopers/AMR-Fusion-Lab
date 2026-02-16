from amr_fusion_lab.config import load_config, ConfigError
import pytest


def test_load_config_success(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("sample_id: S1\noutdir: outputs/S1\n", encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg["sample_id"] == "S1"


def test_load_config_missing_keys(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("sample_id: S1\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(str(p))
