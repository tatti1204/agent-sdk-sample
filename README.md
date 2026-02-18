# Agent SDK + GitHub Actions サンプル

Anthropic の API を使ってリポジトリの日次レポートを自動生成するサンプルプロジェクトです。
GitHub Actions のスケジュール実行で毎日レポートを生成します。

## セットアップ

### 1. リポジトリの準備

```bash
cd ~/agent-sdk-sample
git init
git add .
git commit -m "Initial commit"
```

GitHub にリポジトリを作成してプッシュしてください。

### 2. GitHub Secrets の設定

リポジトリの **Settings > Secrets and variables > Actions** で以下を設定：

| Secret 名 | 説明 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic の API キー |

### 3. GitHub Actions の有効化

リポジトリの **Actions** タブを開き、ワークフローを有効化してください。
`workflow_dispatch` が設定されているので、**Run workflow** ボタンから手動実行も可能です。

## ローカルでのテスト

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# API キーを設定して実行
export ANTHROPIC_API_KEY="your-api-key"
python agent.py
```

`reports/` ディレクトリにレポートが出力されます。

## ファイル構成

```
.github/workflows/scheduled-agent.yml  # GitHub Actions ワークフロー
.claude/skills/daily-report/SKILL.md   # スキル定義
agent.py                               # メインスクリプト
requirements.txt                       # 依存パッケージ
reports/                               # レポート出力先
```

## カスタマイズ

- **実行スケジュールの変更**: `.github/workflows/scheduled-agent.yml` の `cron` を編集
- **レポート内容の変更**: `agent.py` の `build_prompt()` を編集
- **集計期間の変更**: `get_git_log()` / `get_changed_files()` の `since_hours` を変更
- **モデルの変更**: `run_agent()` の `model` パラメータを変更
