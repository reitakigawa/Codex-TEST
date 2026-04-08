from __future__ import annotations

import json
import os
from functools import wraps
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, redirect, render_template, session, url_for

try:
    from authlib.integrations.flask_client import OAuth
except ImportError:  # pragma: no cover - optional dependency for auth feature
    OAuth = None

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
SECTIONS = ("novels", "blog", "gallery", "games", "sandbox")
GENERIC_SECTIONS = ("sandbox",)

twitter = None
if OAuth is not None:
    oauth = OAuth(app)
    twitter = oauth.register(
        name="twitter",
        client_id=os.environ.get("TWITTER_CLIENT_ID"),
        client_secret=os.environ.get("TWITTER_CLIENT_SECRET"),
        authorize_url="https://twitter.com/i/oauth2/authorize",
        access_token_url="https://api.twitter.com/2/oauth2/token",
        api_base_url="https://api.twitter.com/2/",
        client_kwargs={
            "scope": "tweet.read users.read offline.access",
        },
    )


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




def _date_sort_key(date_str: str) -> datetime:
    if not date_str:
        return datetime.min

    normalized = date_str.strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return datetime.min


def _latest_items(section: str, content_type: str, limit: int = 3) -> list[dict[str, Any]]:
    if content_type == "markdown":
        raw_items = _load_markdown_collection(section)
    else:
        raw_items = _load_json_collection(section)

    sorted_items = sorted(raw_items, key=lambda item: _date_sort_key(item.get("date", "")), reverse=True)
    latest = sorted_items[:limit]

    return [
        {
            "title": item.get("title", item["slug"]),
            "slug": item["slug"],
            "date": item.get("date", ""),
            "url": f"/{section}/{item['slug']}",
        }
        for item in latest
    ]


def _build_top_latest_content() -> dict[str, list[dict[str, Any]]]:
    return {
        "novels": _latest_items("novels", "markdown", 3),
        "blog": _latest_items("blog", "markdown", 3),
        "gallery": _latest_items("gallery", "json", 3),
        "games": _latest_items("games", "json", 3),
    }

def _safe_generic_section(section: str) -> str:
    if section not in GENERIC_SECTIONS:
        abort(404)
    return section


def _is_twitter_auth_enabled() -> bool:
    return (
        twitter is not None
        and bool(os.environ.get("TWITTER_CLIENT_ID"))
        and bool(os.environ.get("TWITTER_CLIENT_SECRET"))
    )


def login_required(view_func: Any) -> Any:
    @wraps(view_func)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if not session.get("user"):
            return redirect(url_for("twitter_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


@app.context_processor
def inject_auth_user() -> dict[str, Any]:
    return {
        "current_user": session.get("user"),
        "twitter_auth_enabled": _is_twitter_auth_enabled(),
    }


@app.get("/auth/twitter/available")
def twitter_auth_available() -> Any:
    return jsonify({"available": _is_twitter_auth_enabled()})


@app.get("/auth/twitter/login")
def twitter_login() -> Any:
    if twitter is None:
        return "Twitter login is unavailable because Authlib is not installed.", 503
    if not os.environ.get("TWITTER_CLIENT_ID") or not os.environ.get("TWITTER_CLIENT_SECRET"):
        return "Twitter login is unavailable because OAuth credentials are not configured.", 503
    redirect_uri = url_for("twitter_callback", _external=True)
    return twitter.authorize_redirect(redirect_uri)


@app.get("/auth/twitter/callback")
def twitter_callback() -> Any:
    if twitter is None:
        return "Twitter login is unavailable because Authlib is not installed.", 503
    token = twitter.authorize_access_token()
    response = twitter.get("users/me?user.fields=name,username,profile_image_url", token=token)
    profile = response.json().get("data", {})
    session["user"] = {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "username": profile.get("username"),
        "profile_image_url": profile.get("profile_image_url"),
    }
    return redirect(url_for("top"))


@app.post("/auth/logout")
def logout() -> Any:
    session.pop("user", None)
    return redirect(url_for("top"))


@app.get("/me")
@login_required
def me() -> Any:
    return render_template("profile.html", user=session["user"])


@app.get("/")
def top() -> str:
    latest_content = _build_top_latest_content()
    return render_template("top.html", sections=SECTIONS, latest_content=latest_content)


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
