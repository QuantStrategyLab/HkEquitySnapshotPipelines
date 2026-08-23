from pathlib import Path
import re


WORKFLOWS = (
    Path(".github/workflows/monthly_snapshot_audit.yml"),
    Path(".github/workflows/hide-codex-limit-comments.yml"),
)
FULL_SHA_ACTION = re.compile(r"uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+v\d+)?$")


def test_privileged_workflows_pin_remote_actions_to_full_commit_shas():
    for path in WORKFLOWS:
        workflow = path.read_text(encoding="utf-8")
        action_lines = [line.strip() for line in workflow.splitlines() if "uses:" in line]

        assert action_lines
        assert all(FULL_SHA_ACTION.fullmatch(line) for line in action_lines)
