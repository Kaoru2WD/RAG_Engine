from pathlib import Path

from rag_engine.redaction import apply_placeholders, load_placeholder_rules


def test_apply_placeholders_replaces_sensitive_values() -> None:
    rules = load_placeholder_rules(Path("placeholder_rules.example.json"))

    text, keys = apply_placeholders("EVCU-A を HILS-BENCH-01 へ接続する。", rules)

    assert "{{ECU_NAME}}" in text
    assert "{{BENCH_NAME}}" in text
    assert keys == ["ecu_name", "bench_name"]
