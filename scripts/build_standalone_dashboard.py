#!/usr/bin/env python3
"""Build a self-contained dashboard for repository-hosted HTML previews."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"


def main() -> None:
    html = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    styles = (DASHBOARD / "styles.css").read_text(encoding="utf-8")
    data = (DASHBOARD / "data" / "dashboard-data.js").read_text(encoding="utf-8")
    application = (DASHBOARD / "app.js").read_text(encoding="utf-8")

    replacements = {
        '<link rel="stylesheet" href="styles.css" />': f"<style>\n{styles}\n</style>",
        '<script src="data/dashboard-data.js"></script>': f"<script>\n{data}\n</script>",
        '<script src="app.js"></script>': f"<script>\n{application}\n</script>",
    }
    for source, replacement in replacements.items():
        if source not in html:
            raise ValueError(f"Dashboard template marker not found: {source}")
        html = html.replace(source, replacement, 1)

    output = DASHBOARD / "standalone.html"
    output.write_text(html, encoding="utf-8")
    print(f"Built standalone dashboard at {output}")


if __name__ == "__main__":
    main()
