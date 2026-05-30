from rag_engine.text_processing import extract_search_terms, parse_search_query


def test_extract_search_terms_ignores_japanese_particles() -> None:
    terms = extract_search_terms("CAN通信の確認をする")

    assert "の" not in terms
    assert "を" not in terms
    assert "can" in terms
    assert "確認" in terms


def test_parse_search_query_supports_basic_operators() -> None:
    parsed = parse_search_query('+CAN通信 -旧版 "確認項目" source:can')

    assert "can" in parsed.include_terms
    assert "通信" in parsed.include_terms
    assert "旧版" in parsed.exclude_terms
    assert parsed.phrases == ["確認項目"]
    assert parsed.filters["source"] == ["can"]
