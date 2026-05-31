from pathlib import Path


DOMAIN_RULES = [
    ("charging", ["charge", "charging", "charger", "obc", "plug", "pilot", "dc charging"]),
    ("diagnostics", ["diag", "diagnostic", "session", "tester", "uds", "security access"]),
    ("power_mode", ["power mode", "precharge", "ready", "ign", "boot sequence", "startup", "起動", "立ち上げ"]),
    ("thermal", ["thermal", "coolant", "derate", "statortemp", "temperature"]),
    ("brake_regen", ["regen", "regenerative", "brake", "torque cap"]),
    ("fault_injection", ["fault injection", "bus off", "injection"]),
    ("io_mapping", ["io mapping", "signal map", "register", "matrix", "signal"]),
    ("bench_ops", ["bench", "topology", "scalexio", "dspace", "rack"]),
]

CONTENT_KIND_RULES = [
    ("checklist", ["checklist", "確認項目", "確認", "preconditions"]),
    ("procedure", ["procedure", "steps", "startup steps", "手順", "立ち上げ"]),
    ("playbook", ["playbook", "recovery pattern", "rollback", "復旧"]),
    ("signal_map", ["signal map", "signal matrix", "mapping", "register"]),
    ("report", ["report", "result summary", "observed", "test report"]),
    ("notes", ["notes", "review", "context", "appendix"]),
    ("matrix", ["matrix", "coverage", "execution"]),
    ("guide", ["guide", "quick guide"]),
]


def infer_document_categories(relative_path: Path, title: str, file_type: str, content: str) -> dict:
    basis = " ".join(
        [
            relative_path.as_posix().lower(),
            title.lower(),
            file_type.lower(),
            content[:2000].lower(),
        ]
    )
    domain, domain_matches = _pick_category(DOMAIN_RULES, basis, fallback="general")
    content_kind, kind_matches = _pick_category(CONTENT_KIND_RULES, basis, fallback="reference")

    tags = sorted(set(_collect_tags(domain_matches + kind_matches)))
    return {
        "source_area": relative_path.parts[0] if relative_path.parts else file_type,
        "domain": domain,
        "content_kind": content_kind,
        "tags": tags,
        "inference_source": "path_and_naming_rules",
        "matched_keywords": sorted(set(domain_matches + kind_matches)),
    }


def summarize_categories(documents: list[dict]) -> dict:
    summary: dict[str, dict[str, int]] = {
        "source_area": {},
        "domain": {},
        "content_kind": {},
    }
    for document in documents:
        categories = document.get("categories", {})
        for key in summary:
            value = categories.get(key, "unknown")
            summary[key][value] = summary[key].get(value, 0) + 1
    return summary


def _pick_category(rules: list[tuple[str, list[str]]], basis: str, fallback: str) -> tuple[str, list[str]]:
    best_name = fallback
    best_matches: list[str] = []
    for name, patterns in rules:
        matches = [pattern for pattern in patterns if pattern in basis]
        if len(matches) > len(best_matches):
            best_name = name
            best_matches = matches
    return best_name, best_matches


def _collect_tags(matches: list[str]) -> list[str]:
    normalized: list[str] = []
    for match in matches:
        token = match.strip().replace(" ", "_")
        if token:
            normalized.append(token)
    return normalized
