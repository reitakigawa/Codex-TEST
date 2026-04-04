# Codex-TEST

## GitHubリポジトリに接続する手順

> まだGitHub上にリポジトリを作っていない場合は、先にGitHubで空リポジトリを作成してください。

1. 接続先のリモートを確認

```bash
git remote -v
```

2. `origin` を追加（HTTPS）

```bash
git remote add origin https://github.com/<your-account>/<your-repo>.git
```

3. すでに `origin` がある場合はURLを更新

```bash
git remote set-url origin https://github.com/<your-account>/<your-repo>.git
```

4. 現在のブランチを初回push

```bash
git push -u origin $(git branch --show-current)
```

## 認証のポイント

- HTTPSの場合: GitHub Personal Access Token（PAT）を利用
- SSHの場合: `git@github.com:<your-account>/<your-repo>.git` を `origin` に設定し、公開鍵をGitHubに登録

## 接続確認

```bash
git remote -v
git ls-remote --heads origin
```

## Render へのデプロイ手順（Flask）

このリポジトリには `render.yaml` を追加済みです。Render 側で Blueprint デプロイを使うと設定を自動で読み込めます。

### 1. GitHub連携
1. Render にログイン
2. **New +** → **Blueprint** を選択
3. このGitHubリポジトリを選択
4. `render.yaml` を読み込んで作成

### 2. デプロイ設定（本リポジトリの内容）
- `rootDir`: `project`
- `buildCommand`: `pip install -r requirements.txt`
- `startCommand`: `gunicorn app:app`
- `env`: `python`

### 3. 初回デプロイ後の確認
- Render の Logs で `gunicorn` 起動を確認
- 発行されたURLにアクセスしてトップページが表示されるか確認

### 4. 以降の更新
- `main` ブランチ（または接続ブランチ）に push
- `autoDeploy: true` のため自動再デプロイ

## ローカル起動（確認用）

```bash
cd project
pip install -r requirements.txt
python app.py
```
