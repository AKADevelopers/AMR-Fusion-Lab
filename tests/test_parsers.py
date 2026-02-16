from amr_fusion_lab.parsers import parse_rgi


def test_parse_rgi_smoke(tmp_path):
    p = tmp_path / "rgi.tsv"
    p.write_text(
        "Best_Hit_ARO\tDrug Class\t% Identity\t% Length of Reference Sequence\n"
        "ARO:1|blaTEM-1\tbeta-lactam\t99.0\t95.0\n",
        encoding="utf-8",
    )

    df = parse_rgi(str(p), sample_id="S1")
    assert len(df) == 1
    assert df.iloc[0]["tool"] == "rgi"
    assert df.iloc[0]["gene"] == "blaTEM-1"
