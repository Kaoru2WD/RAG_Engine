import re
from dataclasses import dataclass, field


ASCII_PATTERN = re.compile(r"[A-Za-z0-9_]+")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[一-龯]+|[ァ-ヴー]+|[ぁ-ゖ]+")
PHRASE_PATTERN = re.compile(r'"([^"]+)"')
FILTER_PATTERN = re.compile(r"(?P<key>source|title|tag):(?P<value>\S+)")

JAPANESE_STOPWORDS = {
    "は",
    "が",
    "を",
    "に",
    "で",
    "と",
    "へ",
    "も",
    "や",
    "の",
    "か",
    "ね",
    "よ",
    "ぞ",
    "さ",
    "な",
    "わ",
    "だけ",
    "まで",
    "より",
    "ほど",
    "など",
    "について",
    "として",
}


@dataclass(slots=True)
class SearchQuery:
    raw: str
    include_terms: list[str] = field(default_factory=list)
    optional_terms: list[str] = field(default_factory=list)
    exclude_terms: list[str] = field(default_factory=list)
    phrases: list[str] = field(default_factory=list)
    filters: dict[str, list[str]] = field(default_factory=dict)


def extract_search_terms(text: str) -> list[str]:
    tokens: list[str] = []
    for token in TOKEN_PATTERN.findall(text):
        normalized = token.lower()
        if _is_hiragana_only(normalized):
            if normalized in JAPANESE_STOPWORDS or len(normalized) == 1:
                continue
            tokens.append(normalized)
            continue
        tokens.append(normalized)
        if _can_expand_with_bigrams(normalized):
            tokens.extend(_build_bigrams(normalized))
    return tokens


def build_search_text(text: str) -> str:
    return " ".join(extract_search_terms(text))


def build_query_text(question: str) -> str:
    parsed = parse_search_query(question)
    tokens = parsed.include_terms + parsed.optional_terms
    if not tokens and not parsed.phrases:
        return question

    query_parts = [f'"{token}"' for token in tokens]
    for phrase in parsed.phrases:
        query_parts.extend(f'"{token}"' for token in extract_search_terms(phrase))
    return " OR ".join(query_parts) if query_parts else question


def parse_search_query(text: str) -> SearchQuery:
    phrases = [match.group(1) for match in PHRASE_PATTERN.finditer(text)]
    filters: dict[str, list[str]] = {}
    for match in FILTER_PATTERN.finditer(text):
        filters.setdefault(match.group("key"), []).append(match.group("value"))

    working = PHRASE_PATTERN.sub(" ", text)
    working = FILTER_PATTERN.sub(" ", working)

    include_terms: list[str] = []
    optional_terms: list[str] = []
    exclude_terms: list[str] = []

    for raw_part in working.split():
        if not raw_part:
            continue

        bucket = optional_terms
        token_text = raw_part
        if raw_part.startswith("+") and len(raw_part) > 1:
            bucket = include_terms
            token_text = raw_part[1:]
        elif raw_part.startswith("-") and len(raw_part) > 1:
            bucket = exclude_terms
            token_text = raw_part[1:]

        bucket.extend(extract_search_terms(token_text))

    return SearchQuery(
        raw=text,
        include_terms=include_terms,
        optional_terms=optional_terms,
        exclude_terms=exclude_terms,
        phrases=phrases,
        filters=filters,
    )


def _build_bigrams(text: str) -> list[str]:
    if len(text) < 2:
        return []
    return [text[index:index + 2] for index in range(len(text) - 1)]


def _can_expand_with_bigrams(token: str) -> bool:
    return len(token) >= 2 and not ASCII_PATTERN.fullmatch(token)


def _is_hiragana_only(text: str) -> bool:
    return all(0x3040 <= ord(char) <= 0x309F for char in text)
