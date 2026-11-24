"""Optional Streamlit UI. Launch with `scoper ui` or `streamlit run src/scoper/app.py`."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from scoper.providers import get_provider
from scoper.render import render_markdown
from scoper.rubric import check_markdown, check_package

PROVIDERS = ["auto", "template", "anthropic", "vertex"]


def main() -> None:
    load_dotenv()
    import streamlit as st

    st.set_page_config(page_title="Architecture Scoper", layout="wide")
    st.title("Architecture Scoper")
    st.caption(
        "Turn a vague executive request into a four-week SOW, pilot plan, "
        "STRIDE threat model, architecture diagram, and success metrics. "
        "Use fictional, unclassified intake only."
    )

    default_provider = os.environ.get("SCOPER_PROVIDER", "auto")
    if default_provider not in PROVIDERS:
        default_provider = "auto"
    provider_name = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(default_provider),
        help=(
            "template runs offline with no API key. "
            "anthropic and vertex require credentials in the environment."
        ),
    )
    request = st.text_area(
        "Intake request",
        height=220,
        placeholder="Paste a vague, fictional request…",
    )

    if st.button("Generate scope package", type="primary"):
        if not request.strip():
            st.error("Request is empty.")
            return
        try:
            package = get_provider(provider_name).generate(request)
        except Exception as exc:
            st.error(str(exc))
            return
        markdown = render_markdown(package)
        issues = check_package(package) + check_markdown(markdown)
        if issues:
            st.warning("\n".join(str(issue) for issue in issues))
        st.markdown(markdown)
        st.download_button(
            "Download markdown",
            data=markdown,
            file_name="scope-package.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download JSON",
            data=package.model_dump_json(indent=2),
            file_name="scope-package.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
