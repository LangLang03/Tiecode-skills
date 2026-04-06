#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        key = str(path.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(path.resolve())
    return result


def find_skill_root(script_file: Path) -> Path:
    # .../tiecode-tlang/scrpits/list_doc_absolute_paths.py -> .../tiecode-tlang
    return script_file.parent.parent.resolve()


def collect_reference_files(references_root: Path) -> list[Path]:
    if not references_root.exists():
        return []
    files = [p.resolve() for p in references_root.rglob("*") if p.is_file()]
    return sorted(files, key=lambda p: str(p).lower())


def collect_reference_dirs(files: list[Path]) -> list[Path]:
    dirs = [f.parent.resolve() for f in files]
    return sorted(unique_paths(dirs), key=lambda p: str(p).lower())


def build_workspace_roots(skill_root: Path, workspace_root: str | None) -> list[Path]:
    roots: list[Path] = []
    if workspace_root:
        roots.append(Path(workspace_root).resolve())
    roots.append(Path.cwd().resolve())

    # Project skill typical layout: <workspace>/skills/<skill-name>
    try:
        project_root = skill_root.parent.parent.resolve()
        roots.append(project_root)
    except Exception:
        pass
    return unique_paths(roots)


def first_existing(relative_path: str, roots: list[Path]) -> str:
    rel = Path(relative_path)
    for root in roots:
        candidate = (root / rel).resolve()
        if candidate.exists():
            return str(candidate)
    return ""


def first_glob(pattern: str, roots: list[Path]) -> str:
    for root in roots:
        try:
            matches = sorted(root.glob(pattern), key=lambda p: str(p).lower())
        except Exception:
            matches = []
        for match in matches:
            if match.is_file():
                return str(match.resolve())
    return ""


def to_payload(skill_root: Path, workspace_roots: list[Path]) -> dict:
    references_root = (skill_root / "references").resolve()
    reference_files = collect_reference_files(references_root)
    reference_dirs = collect_reference_dirs(reference_files)

    rope_component_file = first_existing("绳包/安卓基本库/源代码/安卓_可视化组件.t", workspace_roots)
    if not rope_component_file:
        rope_component_file = first_glob("**/绳包/安卓基本库/源代码/安卓_可视化组件.t", workspace_roots)

    return {
        "skill_root": str(skill_root),
        "references_root": str(references_root),
        "reference_directories": [str(p) for p in reference_dirs],
        "reference_files": [str(p) for p in reference_files],
        "resolved_project_paths": {
            "source_dir": first_existing("源代码", workspace_roots),
            "rope_component_file": rope_component_file,
        },
        "workspace_roots_checked": [str(p) for p in workspace_roots],
        "fallback_note": (
            "If Python is unavailable, use the original relative paths from "
            "SKILL.md -> Mandatory Read Set."
        ),
    }


def print_text(payload: dict) -> None:
    print("[ABSOLUTE_DOC_ROOTS]")
    print(f"skill_root={payload['skill_root']}")
    print(f"references_root={payload['references_root']}")

    print("\n[ABSOLUTE_DOC_DIRECTORIES]")
    for directory in payload["reference_directories"]:
        print(directory)

    print("\n[ABSOLUTE_DOC_FILES]")
    for file_path in payload["reference_files"]:
        print(file_path)

    print("\n[RESOLVED_PROJECT_PATHS]")
    resolved = payload["resolved_project_paths"]
    print(f"source_dir={resolved['source_dir'] or '(not found)'}")
    print(f"rope_component_file={resolved['rope_component_file'] or '(not found)'}")

    print("\n[WORKSPACE_ROOTS_CHECKED]")
    for root in payload["workspace_roots_checked"]:
        print(root)

    print("\n[FALLBACK]")
    print(payload["fallback_note"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List absolute documentation paths for the active tiecode-tlang skill."
    )
    parser.add_argument(
        "--workspace-root",
        help="Optional workspace root used to resolve project paths (e.g. 源代码, 绳包).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of plain text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = find_skill_root(Path(__file__).resolve())
    workspace_roots = build_workspace_roots(skill_root, args.workspace_root)
    payload = to_payload(skill_root, workspace_roots)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
