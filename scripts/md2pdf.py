#!/usr/bin/env python
"""Convert a Markdown document to a styled PDF.

Renders Markdown -> HTML (python-markdown) and prints it through Playwright's
bundled Chromium, so web fonts and CSS render exactly as a browser would.
Typography matches cultivatedprogression.com (Newsreader / JetBrains Mono,
gold accent) on a light, print-readable page.

Usage:
    python scripts/md2pdf.py input.md [output.pdf]

Setup (one time):
    pip install playwright markdown
    python -m playwright install chromium
"""

import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

CSS = """
@page {
  size: Letter;
  margin: 22mm 20mm 20mm 20mm;
}
:root {
  --serif: "Newsreader", Georgia, serif;
  --mono: "JetBrains Mono", ui-monospace, monospace;
  --ink-0: #1a1714;
  --ink-1: #3c3733;
  --ink-2: #6b635b;
  --gold: #9a6b29;
  --gold-dim: #c9a86a;
  --rule: #e4ddd2;
  --bg-note: #faf6ef;
}
* { box-sizing: border-box; }
body {
  font-family: var(--serif);
  color: var(--ink-1);
  font-size: 11.5pt;
  line-height: 1.6;
  margin: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
h1, h2, h3, h4 {
  font-family: var(--serif);
  color: var(--ink-0);
  font-weight: 500;
  line-height: 1.2;
}
h1 {
  font-size: 26pt;
  font-style: italic;
  font-weight: 400;
  margin: 0 0 4pt;
  letter-spacing: -0.01em;
}
h2 {
  font-size: 15.5pt;
  margin: 26pt 0 9pt;
  padding-bottom: 5pt;
  border-bottom: 1px solid var(--gold-dim);
  page-break-after: avoid;
}
h3 {
  font-size: 12.5pt;
  color: var(--gold);
  margin: 18pt 0 6pt;
  page-break-after: avoid;
}
p { margin: 0 0 10pt; }
strong { color: var(--ink-0); font-weight: 600; }
em { font-style: italic; }
a { color: var(--gold); text-decoration: none; }
ul, ol { margin: 0 0 12pt; padding-left: 20pt; }
li { margin: 0 0 5pt; padding-left: 3pt; }
li::marker { color: var(--gold-dim); }
hr {
  border: 0;
  border-top: 1px solid var(--rule);
  margin: 20pt 0;
}
blockquote {
  margin: 12pt 0;
  padding: 11pt 16pt;
  background: var(--bg-note);
  border-left: 2px solid var(--gold-dim);
  color: var(--ink-2);
  font-size: 10.5pt;
}
blockquote p { margin: 0; }
blockquote p + p { margin-top: 7pt; }
code {
  font-family: var(--mono);
  font-size: 0.9em;
  color: var(--ink-0);
}
table { border-collapse: collapse; width: 100%; margin: 12pt 0; font-size: 10pt; }
th, td { border: 1px solid var(--rule); padding: 6pt 9pt; text-align: left; vertical-align: top; }
th { background: var(--bg-note); font-family: var(--mono); font-size: 8.5pt;
     text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-0); }
/* The lede: first italic paragraph right after the H2 subtitle */
h1 + h2 { border: 0; font-size: 13pt; font-style: italic; font-weight: 400;
          color: var(--ink-2); margin: 0 0 16pt; padding: 0; }
sub, sup { font-size: 0.72em; }
"""

HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>%s</style></head><body>"""

FOOTER = (
    '<div style="font-family:\'JetBrains Mono\',monospace;font-size:7.5pt;'
    'color:#6b635b;width:100%;padding:0 20mm;display:flex;'
    'justify-content:space-between;">'
    '<span>Cultivated Progression</span>'
    '<span class="pageNumber"></span></div>'
)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/md2pdf.py input.md [output.pdf]")
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")

    html_body = markdown.markdown(
        src.read_text(encoding="utf-8"),
        extensions=["extra", "sane_lists", "smarty", "tables"],
    )
    html = HEAD % CSS + html_body + "</body></html>"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.pdf(
            path=str(out),
            format="Letter",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=FOOTER,
            margin={"top": "22mm", "bottom": "18mm", "left": "20mm", "right": "20mm"},
        )
        browser.close()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
