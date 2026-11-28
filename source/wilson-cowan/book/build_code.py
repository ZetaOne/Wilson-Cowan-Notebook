"""Write a browser page (syntax-highlighted, with a download link) for every
script behind the book: rendered-anims/wilson-cowan/book/code/<name>.html"""
import html
import shutil
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, TextLexer

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
OUT = SRC.parents[1] / "rendered-anims" / "wilson-cowan" / "book" / "code"
OUT.mkdir(parents=True, exist_ok=True)

files = [SRC / "wc_lib.py", SRC / "figkit.py"] + sorted((SRC / "figs").glob("*.py")) + sorted((SRC / "decks").glob("*.py"))
DESC = {
    "wc_lib.py": "Shared numerics: the Wilson–Cowan models as XPP .ode text, run through pyauto-xpp, plus helpers.",
    "figkit.py": "Figure helpers: style, colours, saving PNGs and GIFs, the figure manifest.",
}
fmt = HtmlFormatter(linenos="table", style="friendly", anchorlinenos=True, lineanchors="L")
css = fmt.get_style_defs(".highlight")
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{name}</title>
<style>
body {{ margin: 0; font: 15px/1.5 system-ui, sans-serif; background: #fdfcf9; color: #1d232b; }}
header {{ padding: 14px 20px; border-bottom: 1px solid #dfe3e8; background: #f3f1ec; position: sticky; top: 0; }}
header h1 {{ font-size: 17px; margin: 0 0 4px; font-family: ui-monospace, monospace; }}
header p {{ margin: 0; color: #5b6672; font-size: 13px; }}
header a {{ color: #0b6b8a; margin-right: 14px; }}
main {{ padding: 10px 20px 60px; overflow-x: auto; }}
.highlight pre {{ font: 13px/1.5 ui-monospace, "JetBrains Mono", Menlo, monospace; margin: 0; }}
td.linenos {{ color: #9aa3ad; padding-right: 12px; user-select: none; }}
{css}
</style></head><body>
<header><h1>{name}</h1><p>{desc}</p>
<p><a href="{raw}" download>download {name}</a><a href="index.html">all code</a><a href="../wc-book.html">back to the book</a></p></header>
<main>{body}</main></body></html>"""

rows = []
for f in files:
    raw = f"raw/{f.name}"
    (OUT / "raw").mkdir(exist_ok=True)
    shutil.copy(f, OUT / raw)
    src = f.read_text()
    doc = DESC.get(f.name)
    if not doc:
        first = src.split('"""')[1].strip().splitlines()[0] if src.startswith('"""') else ""
        doc = first
    body = highlight(src, PythonLexer(), fmt)
    (OUT / f"{f.stem}.html").write_text(PAGE.format(name=f.name, desc=html.escape(doc), raw=raw, body=body, css=css))
    rows.append((f.name, f.stem, doc))

idx = "".join(f'<li><a href="{s}.html"><code>{n}</code></a> — {html.escape(d)}</li>' for n, s, d in rows)
(OUT / "index.html").write_text(PAGE.format(name="Code behind the Wilson–Cowan book", desc="Every figure links to the script that made it. Simulations use XPPAUT through pyauto-xpp.", raw="raw/iso_lib.py", body=f"<ul>{idx}</ul>", css=css))
print(f"wrote {len(rows)} code pages to {OUT}")
