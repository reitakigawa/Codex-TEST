from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
SECTIONS = ("novels", "blog", "gallery", "games", "sandbox")
NON_NOVEL_SECTIONS = ("blog", "gallery", "games", "sandbox")


def _safe_section(section: str) -> str:
    if section not in NON_NOVEL_SECTIONS:
        abort(404)
    return section


def _parse_yaml_header(markdown_text: str) -> tuple[dict[str, str], str]:
    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown_text

    metadata: dict[str, str] = {}
    header_lines: list[str] = []

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            header_lines = lines[1:index]
            body = "\n".join(lines[index + 1 :])
            break
    else:
        return {}, markdown_text

    for line in header_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, body


def _load_novels() -> list[dict[str, Any]]:
    novels_dir = CONTENT_DIR / "novels"
    items: list[dict[str, Any]] = []

    for md_path in sorted(novels_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        meta, body = _parse_yaml_header(text)
        items.append(
            {
                "slug": md_path.stem,
                "title": meta.get("title", md_path.stem),
                "date": meta.get("date", ""),
                "body": body,
                "source": str(md_path.relative_to(BASE_DIR)),
            }
        )

    return items


def _load_novel(slug: str) -> dict[str, Any]:
    novel_path = CONTENT_DIR / "novels" / f"{slug}.md"
    if not novel_path.exists():
        abort(404)

    text = novel_path.read_text(encoding="utf-8")
    meta, body = _parse_yaml_header(text)

    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "date": meta.get("date", ""),
        "body": body,
        "source": str(novel_path.relative_to(BASE_DIR)),
    }


def _load_markdown_items(section: str) -> list[dict[str, Any]]:
    section_dir = CONTENT_DIR / section
    items: list[dict[str, Any]] = []

    for md_path in sorted(section_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0] if text.splitlines() else md_path.stem
        title = first_line.lstrip("# ").strip() or md_path.stem
        items.append(
            {
                "slug": md_path.stem,
                "title": title,
                "body": text,
                "source": str(md_path.relative_to(BASE_DIR)),
            }
        )
    return items


def _load_json_items(section: str) -> list[dict[str, Any]]:
    section_dir = CONTENT_DIR / section
    items: list[dict[str, Any]] = []

    for json_path in sorted(section_dir.glob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        items.append(
            {
                "slug": json_path.stem,
                "data": data,
                "source": str(json_path.relative_to(BASE_DIR)),
            }
        )
    return items


@app.get("/")
def top() -> str:
    return render_template("top.html", sections=SECTIONS)


@app.get("/novels")
@app.get("/novels/")
def novels_index() -> str:
    novels = _load_novels()
    return render_template("novels/list.html", novels=novels)


@app.get("/novels/<slug>")
def novels_detail(slug: str) -> str:
    novel = _load_novel(slug)
    return render_template("novels/detail.html", novel=novel)


@app.get("/<section>/")
def section_index(section: str) -> str:
    section_name = _safe_section(section)
    markdown_items = _load_markdown_items(section_name)
    json_items = _load_json_items(section_name)

    return render_template(
        f"{section_name}/index.html",
        section=section_name,
        markdown_items=markdown_items,
        json_items=json_items,
    )


if __name__ == "__main__":
    app.run(debug=True)
