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
