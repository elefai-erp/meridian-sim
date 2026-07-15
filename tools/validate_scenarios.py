#!/usr/bin/env python3
"""Validate every scenario YAML against scenarios/schema.json plus world-consistency rules.

This is the same validator the CA contribution pipeline runs before auto-creating a PR,
and the one CI runs on every push. Exit code 0 = all valid.

Usage: python3 tools/validate_scenarios.py [scenario.yaml ...]
       (no args = validate all of scenarios/**/*.yaml)
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit("Missing deps: pip install pyyaml jsonschema")

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "scenarios" / "schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.yaml$")


def world_checks(data: dict, path: Path) -> list[str]:
    """Consistency rules the JSON Schema can't express."""
    errors = []
    # Filename and directory conventions
    if not SLUG_RE.match(path.name):
        errors.append(f"filename '{path.name}' is not kebab-case .yaml")
    if path.parent.name != data.get("domain"):
        errors.append(f"file lives in '{path.parent.name}/' but domain is '{data.get('domain')}'")
    # A consequence can only surface after the scenario fires
    cons = data.get("consequence")
    if cons and cons["surfaces_week"] < data["week"]:
        errors.append(
            f"consequence surfaces in week {cons['surfaces_week']} "
            f"before the scenario fires in week {data['week']}"
        )
    # Live/approved scenarios must carry full attribution and dates
    if data.get("status") in ("approved", "live"):
        for role in ("authored_by", "reviewed_by"):
            if not data[role]["name"] or not data[role]["membership_no"]:
                errors.append(f"status '{data['status']}' requires {role} name + membership_no")
        if not data.get("approved_date"):
            errors.append(f"status '{data['status']}' requires approved_date")
    # Reviewer must not be the author (schema can't compare fields)
    a, r = data.get("authored_by", {}), data.get("reviewed_by", {})
    if a.get("membership_no") and a.get("membership_no") == r.get("membership_no"):
        errors.append("author and reviewer have the same membership number")
    return errors


def validate(path: Path) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]
    if not isinstance(data, dict):
        return ["file is not a YAML mapping"]
    errors = [
        f"{'.'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in VALIDATOR.iter_errors(data)
    ]
    errors += world_checks(data, path)
    return errors


def main() -> int:
    if len(sys.argv) > 1:
        files = [Path(a) for a in sys.argv[1:]]
    else:
        files = sorted((ROOT / "scenarios").rglob("*.yaml"))
    if not files:
        print("No scenario files found.")
        return 1
    failed = 0
    for f in files:
        errs = validate(f)
        rel = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
        if errs:
            failed += 1
            print(f"FAIL {rel}")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"ok   {rel}")
    print(f"\n{len(files) - failed}/{len(files)} scenarios valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
