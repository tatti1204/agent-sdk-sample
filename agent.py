"""Agent SDK サンプル: リポジトリ日次レポート生成エージェント

GitHub リポジトリの直近のコミット、Issue、PR を分析し、
日次レポートを生成する Agent SDK のサンプルスクリプト。
"""

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic


def get_git_log(since_hours: int = 24) -> str:
    """直近のコミットログを取得する。"""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since_hours} hours ago", "--oneline", "--no-merges"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip() or "直近24時間のコミットはありません。"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Git ログの取得に失敗しました。"


def get_changed_files(since_hours: int = 24) -> str:
    """直近に変更されたファイル一覧を取得する。"""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since_hours} hours ago", "--name-only", "--pretty=format:"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        files = sorted(set(line for line in result.stdout.strip().splitlines() if line))
        return "\n".join(files) if files else "直近24時間の変更ファイルはありません。"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "変更ファイルの取得に失敗しました。"


def get_open_issues_and_prs() -> str:
    """gh CLI でオープンな Issue と PR を取得する。"""
    output_parts = []

    # Issues
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "10", "--json", "number,title,createdAt"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output_parts.append(f"## Open Issues\n{result.stdout.strip() or 'なし'}")
    except (subprocess.SubprocessError, FileNotFoundError):
        output_parts.append("## Open Issues\ngh CLI が利用できません。")

    # Pull Requests
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--limit", "10", "--json", "number,title,createdAt"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output_parts.append(f"## Open PRs\n{result.stdout.strip() or 'なし'}")
    except (subprocess.SubprocessError, FileNotFoundError):
        output_parts.append("## Open PRs\ngh CLI が利用できません。")

    return "\n\n".join(output_parts)


def build_prompt(git_log: str, changed_files: str, issues_and_prs: str) -> str:
    """エージェントに渡すプロンプトを構築する。"""
    return f"""あなたはリポジトリの日次レポートを生成するアシスタントです。
以下の情報をもとに、Markdown 形式で簡潔な日次サマリーレポートを作成してください。

# 直近24時間のコミット
{git_log}

# 変更されたファイル
{changed_files}

# オープンな Issue / PR
{issues_and_prs}

レポートには以下を含めてください：
1. 本日のハイライト（主な変更点を2-3行で要約）
2. コミット一覧
3. 変更ファイル一覧
4. オープンな Issue / PR の状況
5. 推奨アクション（対応が必要そうな項目があれば）

日付: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""


def run_agent() -> str:
    """Agent SDK を使ってレポートを生成する。"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY が設定されていません。", file=sys.stderr)
        sys.exit(1)

    git_log = get_git_log()
    changed_files = get_changed_files()
    issues_and_prs = get_open_issues_and_prs()

    prompt = build_prompt(git_log, changed_files, issues_and_prs)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def save_report(content: str) -> Path:
    """レポートをファイルに保存する。"""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = reports_dir / f"daily-report-{today}.md"
    report_path.write_text(content, encoding="utf-8")
    return report_path


def main():
    print("日次レポートを生成中...")
    report = run_agent()
    path = save_report(report)
    print(f"レポートを保存しました: {path}")
    print("---")
    print(report)


if __name__ == "__main__":
    main()
