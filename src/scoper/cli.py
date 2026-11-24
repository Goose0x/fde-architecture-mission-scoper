from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from scoper.providers import get_provider
from scoper.providers.base import resolve_provider_name
from scoper.render import render_markdown
from scoper.rubric import check_file, check_markdown, check_package


def _read_request(args: argparse.Namespace) -> str:
    if args.request and args.input:
        raise SystemExit("use either --request or --input, not both")
    if args.request:
        return args.request
    if args.input:
        path = Path(args.input)
        if not path.is_file():
            raise SystemExit(f"input file not found: {path}")
        return path.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("provide --request, --input, or pipe the intake on stdin")


def _cmd_generate(args: argparse.Namespace) -> int:
    request = _read_request(args)
    if not request.strip():
        raise SystemExit("request is empty")
    provider = get_provider(args.provider)
    package = provider.generate(request)
    markdown = render_markdown(package)
    issues = check_package(package)
    issues.extend(check_markdown(markdown))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "scope-package.md"
    json_path = out_dir / "scope-package.json"
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(package.model_dump_json(indent=2), encoding="utf-8")
    if issues and not args.allow_failing_rubric:
        for issue in issues:
            print(f"rubric: {issue}", file=sys.stderr)
        return 2
    print(f"Wrote {md_path} and {json_path} (provider={provider.name})")
    if issues:
        for issue in issues:
            print(f"rubric warning: {issue}", file=sys.stderr)
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        raise SystemExit(f"file not found: {path}")
    issues = check_file(path)
    if issues:
        for issue in issues:
            print(f"rubric: {issue}", file=sys.stderr)
        return 2
    print(f"rubric ok: {path}")
    return 0


def _cmd_ui(args: argparse.Namespace) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        raise SystemExit("Streamlit is not installed. Run: pip install -e '.[ui]'") from None
    app = Path(__file__).with_name("app.py")
    os.environ["SCOPER_PROVIDER"] = args.provider
    print(f"Starting Streamlit UI (provider={resolve_provider_name(args.provider)})")
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app)],
        check=False,
    )
    return int(result.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scoper",
        description=(
            "Turn a vague executive request into a four-week SOW, pilot plan, "
            "STRIDE threat model, mermaid architecture, and success metrics."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a scope package")
    gen.add_argument("-i", "--input", help="path to an intake text or markdown file")
    gen.add_argument("-r", "--request", help="intake text passed on the command line")
    gen.add_argument("-o", "--out", default="out", help="output directory (default: out/)")
    gen.add_argument(
        "--provider",
        choices=["auto", "template", "anthropic", "vertex"],
        default="auto",
        help="template is offline and deterministic; auto picks anthropic, then vertex, then template",
    )
    gen.add_argument(
        "--allow-failing-rubric",
        action="store_true",
        help="write outputs even if the rubric finds issues",
    )
    gen.set_defaults(func=_cmd_generate)

    check = sub.add_parser("check", help="run the output rubric on a generated markdown file")
    check.add_argument("path")
    check.set_defaults(func=_cmd_check)

    ui = sub.add_parser("ui", help="open the optional Streamlit UI")
    ui.add_argument(
        "--provider",
        choices=["auto", "template", "anthropic", "vertex"],
        default="auto",
    )
    ui.set_defaults(func=_cmd_ui)
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
