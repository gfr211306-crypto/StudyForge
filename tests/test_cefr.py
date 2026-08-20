import csv
import json

from scripts.build_cefr_data import build_cefr_mapping
from studyforge.cefr import CEFRProfile, CEFR_UNKNOWN, default_cefr_profile


def test_default_cefr_profile_uses_reliable_partial_mapping():
    profile = default_cefr_profile()
    assert profile.known_word_count >= 7_000
    assert profile.level_for("achieve") == "A2"
    assert profile.level_for("analyze") == "B1"
    assert profile.level_for("alleviate") == "C1"
    assert profile.level_for("access") == CEFR_UNKNOWN
    assert profile.level_for("definitely-not-a-real-word") == CEFR_UNKNOWN


def test_cefr_profile_rejects_invalid_levels():
    profile = CEFRProfile.from_mapping({"valid": "B2", "guessed": "B9"})
    assert profile.level_for("valid") == "B2"
    assert profile.level_for("guessed") == CEFR_UNKNOWN


def test_cefr_builder_omits_ambiguous_headwords_and_expands_variants(tmp_path):
    cefr_j = tmp_path / "cefrj.csv"
    c1_c2 = tmp_path / "c1c2.csv"
    output = tmp_path / "levels.json"

    for path, rows in (
        (
            cefr_j,
            [
                ["analyze/analyse", "verb", "B1"],
                ["access", "noun", "B1"],
                ["access", "verb", "B2"],
            ],
        ),
        (c1_c2, [["alleviate", "verb", "C1"]]),
    ):
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["headword", "pos", "CEFR"])
            writer.writerows(rows)

    known, ambiguous = build_cefr_mapping(cefr_j, c1_c2, output)
    data = json.loads(output.read_text(encoding="utf-8"))
    assert known == 3
    assert ambiguous == 1
    assert data["levels"]["analyze"] == "B1"
    assert data["levels"]["analyse"] == "B1"
    assert data["levels"]["alleviate"] == "C1"
    assert "access" not in data["levels"]
