"""Agent SDK サンプル: リポジトリ日次レポート生成エージェント

Claude Agent SDK を使って、リポジトリの直近のコミット、Issue、PR を分析し、
日次レポートを生成するサンプルスクリプト。

認証:
- ANTHROPIC_API_KEY 環境変数があれば API キーで認証
- なければ Claude Code CLI 経由で認証（Max/Pro プラン対応）
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


REPORT_PROMPT = """\
このリポジトリの日次レポートを生成してください。

以下の手順で情報を収集し、Markdown 形式のレポートを作成してください：

1. `git log --since="24 hours ago" --oneline --no-merges` で直近24時間のコミットを確認
2. `git log --since="24 hours ago" --name-only --pretty=format:` で変更ファイルを確認
3. `gh issue list --state open --limit 10` でオープンな Issue を確認（gh が使えない場合はスキップ）
4. `gh pr list --state open --limit 10` でオープンな PR を確認（gh が使えない場合はスキップ）

レポートには以下を含めてください：
- 本日のハイライト（主な変更点を2-3行で要約）
- コミット一覧
- 変更ファイル一覧
- オープンな Issue / PR の状況
- 推奨アクション（対応が必要そうな項目があれば）

レポートを reports/daily-report-{today}.md に保存してください。
""".format(today=datetime.now(timezone.utc).strftime("%Y-%m-%d"))


async def run_agent() -> str:
    """Agent SDK を使ってレポートを生成する。"""
    report_text = ""

    async for message in query(
        prompt=REPORT_PROMPT,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
            permission_mode="bypassPermissions",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                    report_text += block.text + "\n"
                elif hasattr(block, "name"):
                    print(f"[Tool] {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"[Done] {message.subtype}")

    return report_text


def main():
    print("日次レポートを生成中...")
    report = asyncio.run(run_agent())

    # レポートファイルの確認
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = Path(__file__).parent / "reports" / f"daily-report-{today}.md"
    if report_path.exists():
        print(f"レポートを保存しました: {report_path}")
    else:
        # エージェントがファイルを作成しなかった場合のフォールバック
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"レポートを保存しました (fallback): {report_path}")


if __name__ == "__main__":
    main()
