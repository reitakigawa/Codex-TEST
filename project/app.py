from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
SECTIONS = ("novels", "blog", "gallery", "games", "sandbox")
GENERIC_SECTIONS = ("sandbox",)


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


def _load_markdown_collection(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    section_dir = CONTENT_DIR / section

    for md_path in sorted(section_dir.glob("*.md")):
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


def _load_markdown_item(section: str, slug: str) -> dict[str, Any]:
    md_path = CONTENT_DIR / section / f"{slug}.md"
    if not md_path.exists():
        abort(404)

    text = md_path.read_text(encoding="utf-8")
    meta, body = _parse_yaml_header(text)
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "date": meta.get("date", ""),
        "body": body,
        "source": str(md_path.relative_to(BASE_DIR)),
    }


def _load_json_collection(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    section_dir = CONTENT_DIR / section

    for json_path in sorted(section_dir.glob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        items.append(
            {
                "slug": json_path.stem,
                "title": data.get("title", json_path.stem),
                "date": data.get("date", ""),
                "data": data,
                "source": str(json_path.relative_to(BASE_DIR)),
            }
        )

    return items


def _load_json_item(section: str, slug: str) -> dict[str, Any]:
    json_path = CONTENT_DIR / section / f"{slug}.json"
    if not json_path.exists():
        abort(404)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    return {
        "slug": slug,
        "title": data.get("title", slug),
        "date": data.get("date", ""),
        "data": data,
        "source": str(json_path.relative_to(BASE_DIR)),
    }


def _safe_generic_section(section: str) -> str:
    if section not in GENERIC_SECTIONS:
        abort(404)
    return section


@app.get("/")
def top() -> str:
    return render_template("top.html", sections=SECTIONS)


@app.get("/novels")
@app.get("/novels/")
def novels_list() -> str:
    novels = _load_markdown_collection("novels")
    return render_template("novels/list.html", novels=novels)


@app.get("/novels/<slug>")
def novels_detail(slug: str) -> str:
    novel = _load_markdown_item("novels", slug)
    return render_template("novels/detail.html", novel=novel)


@app.get("/blog")
@app.get("/blog/")
def blog_list() -> str:
    posts = _load_markdown_collection("blog")
    return render_template("blog/list.html", posts=posts)


@app.get("/blog/<slug>")
def blog_detail(slug: str) -> str:
    post = _load_markdown_item("blog", slug)
    return render_template("blog/detail.html", post=post)


@app.get("/gallery")
@app.get("/gallery/")
def gallery_list() -> str:
    items = _load_json_collection("gallery")
    return render_template("gallery/list.html", items=items)


@app.get("/gallery/<slug>")
def gallery_detail(slug: str) -> str:
    item = _load_json_item("gallery", slug)
    return render_template("gallery/detail.html", item=item)


@app.get("/games")
@app.get("/games/")
def games_list() -> str:
    items = _load_json_collection("games")
    return render_template("games/list.html", items=items)


@app.get("/games/<slug>")
def games_detail(slug: str) -> str:
    item = _load_json_item("games", slug)
    return render_template("games/detail.html", item=item)


@app.get("/<section>/")
def section_index(section: str) -> str:
    section_name = _safe_generic_section(section)
    markdown_items = _load_markdown_collection(section_name)
    json_items = _load_json_collection(section_name)
    return render_template(
        f"{section_name}/index.html",
        section=section_name,
        markdown_items=markdown_items,
        json_items=json_items,
    )


if __name__ == "__main__":
    app.run(debug=True)
