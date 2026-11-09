"""Посчитать тексты и найти примеры инъекций в корпусах курса на home."""

import hashlib
import json
from collections import Counter

from shared.config import DATA_DIR, RAW_DIR
from shared.loaders import iter_source
from shared.security import detect_injection


def main():
    report = {}
    for source in ("habr", "science", "news", "injected"):
        count, seen, attacks = 0, set(), Counter()
        examples = []
        for record in iter_source(RAW_DIR / source, source):
            count += 1
            seen.add(hashlib.sha256(record.text.encode()).hexdigest())
            reasons = detect_injection(record.text)
            attacks.update(reasons)
            if reasons and len(examples) < 3:
                examples.append({"title": record.title, "reasons": reasons})
        report[source] = {
            "nonempty": count,
            "unique_texts": len(seen),
            "rules": dict(attacks),
            "examples": examples,
        }
        print(source, json.dumps(report[source], ensure_ascii=False), flush=True)
    (DATA_DIR / "inspection.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
