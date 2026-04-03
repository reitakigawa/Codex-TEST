from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
SECTIONS = ("novels", "blog", "gallery", "games", "sandbox")


def _safe_section(section: str) -> str:
    if section not in SECTIONS:
        abort(404)
    return section


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
