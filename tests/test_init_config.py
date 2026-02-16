from amr_fusion_lab.config import write_default_config, load_config


def test_write_default_config_roundtrip(tmp_path):
    p = tmp_path / "starter.yaml"
    write_default_config(str(p), force=False)
    cfg = load_config(str(p))
    assert cfg["sample_id"] == "SAMPLE_001"
    assert "outdir" in cfg
