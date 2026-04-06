#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INDEX_FILES = {
    "annotation": "t_lang_annotation_index_v2.json",
    "api": "t_lang_api_index.json",
    "structured": "t_lang_structured_members.json",
    "manifest": "t_lang_manifest.json",
    "manifest_v2": "t_lang_manifest_v2.json",
}


def find_skill_root(script_file: Path) -> Path:
    # .../tiecode-tlang/scrpits/index_json_ops.py -> .../tiecode-tlang
    return script_file.parent.parent.resolve()


def indexes_root(skill_root: Path) -> Path:
    return (skill_root / "references" / "indexes").resolve()


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


@dataclass
class LoadedIndex:
    name: str
    path: Path
    data: Any


def load_index(skill_root: Path, name: str) -> LoadedIndex:
    if name not in INDEX_FILES:
        raise ValueError(f"unknown index: {name}")
    path = indexes_root(skill_root) / INDEX_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"index file not found: {path}")
    return LoadedIndex(name=name, path=path, data=read_json_file(path))


def load_many(skill_root: Path, names: list[str]) -> list[LoadedIndex]:
    return [load_index(skill_root, n) for n in names]


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(stringify(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k}:{stringify(v)}" for k, v in value.items())
    return str(value)


def make_jsonable(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, list):
        return [make_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: make_jsonable(v) for k, v in obj.items()}
    return obj


def cmd_list(args: argparse.Namespace, skill_root: Path) -> int:
    root = indexes_root(skill_root)
    result: list[dict[str, Any]] = []
    for name, filename in INDEX_FILES.items():
        path = root / filename
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        result.append(
            {
                "name": name,
                "file": filename,
                "path": str(path),
                "exists": exists,
                "size_bytes": size,
            }
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("[INDEX_FILES]")
    for item in result:
        mark = "OK" if item["exists"] else "MISSING"
        print(f"{mark:8} {item['name']:11} {item['file']} ({item['size_bytes']} bytes)")
        print(f"         {item['path']}")
    return 0


def collect_stats(indexes: list[LoadedIndex]) -> dict[str, Any]:
    stats: dict[str, Any] = {}

    for idx in indexes:
        data = idx.data
        if idx.name == "annotation" and isinstance(data, dict):
            stats[idx.name] = {
                "annotation_count": data.get("annotation_count"),
                "entries": len(data.get("annotations", [])),
            }
        elif idx.name == "api" and isinstance(data, dict):
            stats[idx.name] = {
                "counts": data.get("counts", {}),
                "classes": len(data.get("classes", [])),
                "methods": len(data.get("methods", [])),
                "prop_reads": len(data.get("prop_reads", [])),
                "prop_writes": len(data.get("prop_writes", [])),
                "constants": len(data.get("constants", [])),
                "events": len(data.get("events", [])),
                "operators": len(data.get("operators", [])),
                "files": len(data.get("files", [])),
            }
        elif idx.name == "structured" and isinstance(data, dict):
            stats[idx.name] = {
                "file_count": data.get("file_count"),
                "class_count": data.get("class_count"),
                "member_count": data.get("member_count"),
                "count_by_kind": data.get("count_by_kind", {}),
                "members": len(data.get("members", [])),
            }
        elif idx.name == "manifest" and isinstance(data, dict):
            coverage = data.get("coverage", {})
            stats[idx.name] = {
                "spec": data.get("spec"),
                "counts": data.get("counts", {}),
                "coverage_file_count": coverage.get("file_count"),
                "coverage_files_entries": len(coverage.get("files", [])) if isinstance(coverage, dict) else None,
            }
        elif idx.name == "manifest_v2" and isinstance(data, dict):
            stats[idx.name] = {
                "file_count": data.get("file_count"),
                "summary": data.get("summary", {}),
                "files_entries": len(data.get("files", [])),
            }
        else:
            stats[idx.name] = {"type": type(data).__name__}

    return stats


def cmd_stats(args: argparse.Namespace, skill_root: Path) -> int:
    names = args.indexes if args.indexes else list(INDEX_FILES.keys())
    indexes = load_many(skill_root, names)
    payload = collect_stats(indexes)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("[INDEX_STATS]")
    for name in names:
        print(f"- {name}")
        block = payload.get(name, {})
        for k, v in block.items():
            print(f"  {k}: {v}")
    return 0


def gather_search_records(index: LoadedIndex, section_filter: set[str] | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    data = index.data

    if index.name == "annotation" and isinstance(data, dict):
        section = "annotations"
        if section_filter and section not in section_filter:
            return records
        for item in data.get("annotations", []):
            if not isinstance(item, dict):
                continue
            records.append(
                {
                    "index": index.name,
                    "section": section,
                    "file": item.get("first_ref", ""),
                    "line": None,
                    "name": item.get("name", ""),
                    "raw": stringify(item),
                    "payload": item,
                }
            )
        return records

    if not isinstance(data, dict):
        return records

    default_sections = [
        "classes",
        "methods",
        "prop_reads",
        "prop_writes",
        "constants",
        "events",
        "operators",
        "files",
        "members",
    ]
    for section in default_sections:
        if section not in data:
            continue
        if section_filter and section not in section_filter:
            continue
        section_data = data.get(section, [])
        if not isinstance(section_data, list):
            continue
        for item in section_data:
            if not isinstance(item, dict):
                continue
            records.append(
                {
                    "index": index.name,
                    "section": section,
                    "file": item.get("file", item.get("path", "")),
                    "line": item.get("line"),
                    "name": item.get("name", item.get("class", "")),
                    "raw": item.get("raw", stringify(item)),
                    "payload": item,
                }
            )
    return records


def match_text(text: str, keyword: str, ignore_case: bool, regex: bool) -> bool:
    if regex:
        flags = re.IGNORECASE if ignore_case else 0
        return re.search(keyword, text, flags=flags) is not None
    if ignore_case:
        return keyword.lower() in text.lower()
    return keyword in text


def cmd_search(args: argparse.Namespace, skill_root: Path) -> int:
    names = args.indexes if args.indexes else ["annotation", "api", "structured"]
    section_filter = set(args.sections) if args.sections else None
    indexes = load_many(skill_root, names)

    all_results: list[dict[str, Any]] = []
    for idx in indexes:
        for record in gather_search_records(idx, section_filter):
            haystack = " ".join(
                [
                    stringify(record.get("name")),
                    stringify(record.get("file")),
                    stringify(record.get("raw")),
                    stringify(record.get("payload")),
                ]
            )
            if match_text(haystack, args.keyword, args.ignore_case, args.regex):
                all_results.append(record)
                if len(all_results) >= args.limit:
                    break
        if len(all_results) >= args.limit:
            break

    if args.json:
        print(json.dumps(make_jsonable(all_results), ensure_ascii=False, indent=2))
        return 0

    print(f"[SEARCH_RESULTS] keyword={args.keyword!r} total={len(all_results)}")
    for r in all_results:
        line_part = f":{r['line']}" if r.get("line") not in (None, "") else ""
        print(f"- {r['index']}/{r['section']}  {r.get('file','')}{line_part}  {r.get('name','')}")
        if args.show_raw:
            print(f"  raw: {r.get('raw','')}")
    return 0


def validate_index_shapes(indexes: list[LoadedIndex]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    by_name = {i.name: i for i in indexes}

    # Basic shape checks.
    required_top = {
        "annotation": {"generated_at", "annotation_count", "annotations"},
        "api": {"counts", "classes", "methods", "prop_reads", "prop_writes", "constants", "events", "operators", "files"},
        "structured": {"file_count", "class_count", "member_count", "count_by_kind", "classes", "members"},
        "manifest": {"spec", "generated_at", "coverage", "counts"},
        "manifest_v2": {"generated_at", "file_count", "summary", "files"},
    }

    for idx in indexes:
        if not isinstance(idx.data, dict):
            errors.append(f"{idx.name}: root is not object/dict")
            continue
        missing = sorted(required_top.get(idx.name, set()) - set(idx.data.keys()))
        if missing:
            errors.append(f"{idx.name}: missing keys {missing}")

    # Cross checks.
    if "annotation" in by_name and isinstance(by_name["annotation"].data, dict):
        d = by_name["annotation"].data
        count = d.get("annotation_count")
        length = len(d.get("annotations", [])) if isinstance(d.get("annotations"), list) else None
        if isinstance(count, int) and isinstance(length, int) and count != length:
            warnings.append(f"annotation: annotation_count={count} but annotations.len={length}")

    if "manifest_v2" in by_name and isinstance(by_name["manifest_v2"].data, dict):
        d = by_name["manifest_v2"].data
        count = d.get("file_count")
        length = len(d.get("files", [])) if isinstance(d.get("files"), list) else None
        if isinstance(count, int) and isinstance(length, int) and count != length:
            warnings.append(f"manifest_v2: file_count={count} but files.len={length}")

    if "api" in by_name and "structured" in by_name:
        a = by_name["api"].data
        s = by_name["structured"].data
        if isinstance(a, dict) and isinstance(s, dict):
            api_class_count = len(a.get("classes", [])) if isinstance(a.get("classes"), list) else None
            structured_class_count = s.get("class_count")
            if isinstance(api_class_count, int) and isinstance(structured_class_count, int) and api_class_count != structured_class_count:
                warnings.append(
                    f"cross-check: api.classes.len={api_class_count} != structured.class_count={structured_class_count}"
                )

            api_method_count = len(a.get("methods", [])) if isinstance(a.get("methods"), list) else None
            structured_member_count = s.get("member_count")
            if isinstance(api_method_count, int) and isinstance(structured_member_count, int) and api_method_count > structured_member_count:
                warnings.append(
                    f"cross-check: api.methods.len={api_method_count} > structured.member_count={structured_member_count}"
                )

    return errors, warnings


def cmd_validate(args: argparse.Namespace, skill_root: Path) -> int:
    names = args.indexes if args.indexes else list(INDEX_FILES.keys())
    indexes = load_many(skill_root, names)
    errors, warnings = validate_index_shapes(indexes)

    payload = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("[VALIDATE]")
        print(f"ok={payload['ok']}")
        for e in errors:
            print(f"ERROR: {e}")
        for w in warnings:
            print(f"WARN: {w}")

    if errors:
        return 2
    if warnings and args.fail_on_warning:
        return 3
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Operate on tiecode-tlang index JSON files (list/stats/search/validate)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List index files and paths.")
    p_list.add_argument("--json", action="store_true", help="Emit JSON.")

    p_stats = sub.add_parser("stats", help="Show index statistics.")
    p_stats.add_argument(
        "--indexes",
        nargs="+",
        choices=list(INDEX_FILES.keys()),
        help="Indexes to include. Default: all.",
    )
    p_stats.add_argument("--json", action="store_true", help="Emit JSON.")

    p_search = sub.add_parser("search", help="Search records in index JSON.")
    p_search.add_argument("keyword", help="Keyword or regex pattern.")
    p_search.add_argument(
        "--indexes",
        nargs="+",
        choices=list(INDEX_FILES.keys()),
        help="Indexes to search. Default: annotation api structured.",
    )
    p_search.add_argument(
        "--sections",
        nargs="+",
        help="Optional section filter (for example: classes methods members annotations).",
    )
    p_search.add_argument("--limit", type=int, default=50, help="Max results. Default: 50.")
    p_search.add_argument("--ignore-case", action="store_true", help="Case-insensitive search.")
    p_search.add_argument("--regex", action="store_true", help="Interpret keyword as regex.")
    p_search.add_argument("--show-raw", action="store_true", help="Show raw field in text output.")
    p_search.add_argument("--json", action="store_true", help="Emit JSON.")

    p_validate = sub.add_parser("validate", help="Validate index JSON shape and cross-check basic counts.")
    p_validate.add_argument(
        "--indexes",
        nargs="+",
        choices=list(INDEX_FILES.keys()),
        help="Indexes to validate. Default: all.",
    )
    p_validate.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings exist.")
    p_validate.add_argument("--json", action="store_true", help="Emit JSON.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = find_skill_root(Path(__file__).resolve())

    if args.command == "list":
        return cmd_list(args, skill_root)
    if args.command == "stats":
        return cmd_stats(args, skill_root)
    if args.command == "search":
        return cmd_search(args, skill_root)
    if args.command == "validate":
        return cmd_validate(args, skill_root)
    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

