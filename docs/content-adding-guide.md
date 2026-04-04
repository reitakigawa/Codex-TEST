# コンテンツ追加手順書

このプロジェクトでは、カテゴリごとに `project/content/` 配下のファイルを追加するだけで公開できます。

## 1. 追加先フォルダ

- 小説（Markdown）: `project/content/novels/`
- ブログ（Markdown）: `project/content/blog/`
- ギャラリー（JSON）: `project/content/gallery/`
- ゲーム（JSON）: `project/content/games/`

## 2. Markdownコンテンツ（novels / blog）

### ファイル名
- 例: `my-first-story.md`
- URLの slug はファイル名（拡張子なし）になります。

### 形式

```md
---
title: タイトル
date: 2026-04-04
---

本文をここに書きます。
```

### 公開URL
- novels: `/novels/<slug>`
- blog: `/blog/<slug>`

## 3. JSONコンテンツ（gallery / games）

### ファイル名
- 例: `sample-item.json`
- URLの slug はファイル名（拡張子なし）になります。

### gallery の例

```json
{
  "title": "作品タイトル",
  "date": "2026-04-04",
  "description": "説明"
}
```

### games の例

```json
{
  "title": "ゲーム名",
  "date": "2026-04-04",
  "description": "ゲーム説明",
  "asset": "sample.zip"
}
```

`asset` を設定した場合、詳細ページで `/static/games/<asset>` へのリンクが表示されます。
実ファイルは `project/static/games/` に配置してください。

### 公開URL
- gallery: `/gallery/<slug>`
- games: `/games/<slug>`

## 4. トップページへの反映

トップページでは以下カテゴリの**最新3件**を表示します。
- novels
- blog
- gallery
- games

`date` を新しい順に並べるため、`YYYY-MM-DD` 形式で記入することを推奨します。

## 5. 追加後の反映手順

```bash
git add project/content project/static/games
git commit -m "Add new content"
git push
```

Render を利用している場合、`autoDeploy: true` なら push 後に自動反映されます。
