# Daily Report スキル

リポジトリの日次サマリーを生成するスキルです。

## 概要

直近24時間のリポジトリ活動を分析し、以下の情報をまとめた Markdown レポートを生成します：

- **コミットサマリー**: 直近24時間のコミット一覧と主な変更点
- **変更ファイル**: 変更されたファイルの一覧
- **オープン Issue / PR**: 現在オープンな Issue と Pull Request の状況
- **推奨アクション**: 対応が必要そうな項目のピックアップ

## 使い方

このスキルは `agent.py` から自動的に呼び出されます。
手動で実行する場合は以下のコマンドを使用してください：

```bash
export ANTHROPIC_API_KEY="your-api-key"
python agent.py
```

## 出力

`reports/daily-report-YYYY-MM-DD.md` にレポートが出力されます。

## カスタマイズ

- `agent.py` の `get_git_log()` の `since_hours` パラメータで集計期間を変更可能
- プロンプト (`build_prompt()`) を編集してレポートの形式やフォーカスを調整可能
