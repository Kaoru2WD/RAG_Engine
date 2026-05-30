import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PlaceholderRule:
    key: str
    placeholder: str
    values: list[str]


def load_placeholder_rules(path: Path | None) -> list[PlaceholderRule]:
    if path is None or not path.exists():
        return []

    payload = json.loads(path.read_text(encoding="utf-8"))
    rules: list[PlaceholderRule] = []
    for row in payload.get("rules", []):
        rules.append(
            PlaceholderRule(
                key=row["key"],
                placeholder=row["placeholder"],
                values=row.get("values", []),
            )
        )
    return rules


def apply_placeholders(text: str, rules: list[PlaceholderRule]) -> tuple[str, list[str]]:
    redacted = text
    matched_keys: list[str] = []
    for rule in rules:
        matched = False
        for value in sorted(rule.values, key=len, reverse=True):
            if value and value in redacted:
                redacted = redacted.replace(value, rule.placeholder)
                matched = True
        if matched:
            matched_keys.append(rule.key)
    return redacted, matched_keys
