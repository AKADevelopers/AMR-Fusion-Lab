import pandas as pd

from amr_fusion_lab.ontology import harmonize_drug_classes


def test_harmonize_drug_classes_maps_synonyms():
    df = pd.DataFrame(
        [
            {"drug_class": "beta lactam"},
            {"drug_class": "Fluoroquinolones"},
            {"drug_class": "colistin"},
            {"drug_class": "unknown class"},
        ]
    )

    out = harmonize_drug_classes(df)

    assert out.loc[0, "drug_class_normalized"] == "beta-lactam"
    assert out.loc[1, "drug_class_normalized"] == "fluoroquinolone"
    assert out.loc[2, "drug_class_normalized"] == "polymyxin"
    assert out.loc[3, "drug_class_normalized"] == "unknown class"
