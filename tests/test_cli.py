from pathlib import Path

import pytest

from scoper.cli import main

REPO = Path(__file__).resolve().parents[1]


def test_cli_generate_and_check_template(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    code = main(
        [
            "generate",
            "--provider",
            "template",
            "--input",
            str(REPO / "examples/northbridge-ops-request.md"),
            "--out",
            str(tmp_path),
        ]
    )
    assert code == 0
    md = tmp_path / "scope-package.md"
    js = tmp_path / "scope-package.json"
    assert md.is_file()
    assert js.is_file()
    assert "Pilot plan" in md.read_text(encoding="utf-8")
    assert main(["check", str(md)]) == 0


def test_cli_rejects_empty_request(tmp_path):
    empty = tmp_path / "empty.md"
    empty.write_text("   \n", encoding="utf-8")
    try:
        main(["generate", "--provider", "template", "--input", str(empty), "--out", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code not in (0, None)
    else:
        raise AssertionError("expected SystemExit for an empty request")


@pytest.mark.parametrize(
    "name",
    ["northbridge-ops-output.md", "harborline-erp-output.md"],
)
def test_committed_example_outputs_pass_rubric(name):
    assert main(["check", str(REPO / "examples" / name)]) == 0
