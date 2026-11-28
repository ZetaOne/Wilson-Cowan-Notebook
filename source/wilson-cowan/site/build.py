#!/usr/bin/env python3
"""build.py -- the local website of the Wilson–Cowan book (adapted from the notebook-site builder)

    python3 build.py              copy the book from REMOTE, then build site/
    python3 build.py --no-sync    build site/ from the copy already in src-book/
    cd site && git add -A && git commit -m "..." && git push

What goes in site/:
  index.html            the library: book, PDF, the paper, every chapter with its deck, code
                        and study material, and "my highlights" (read from this browser)
  wilson-cowan.html    the book, with the Display panel of pyauto-xpp (theme, text size,
                        font) and highlights/notes (reader.js); figs/, assets/, the PDF
  decks/chNN/           the slide decks; deck.js remembers the last slide of each
  code/                 every script behind the book's figures, as themed pages + raw files
  study/                the other material for studying Osinga & Moehlis (2010): the
                        explainer, the recipe, the course scripts and notebooks, the XPPAUT
                        shell and 8.4 scripts, each next to the chapters it belongs to
Display choices are shared with the pyauto-xpp site (same localStorage keys, same origin).
"""
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC, OUT, WEB = ROOT / "rendered-anims" / "wilson-cowan" / "book", ROOT / "rendered-anims" / "wilson-cowan" / "site", HERE / "web"
REMOTE = "user@host:path/to/your/book/"   # where the book is made (an rsync source); change this, or use --no-sync
DOCS = ROOT / "rendered-anims" / "wilson-cowan" / "study"
sys.path.insert(0, str(HERE / "vendor"))
import make_site as M  # noqa: E402  (the pyauto-xpp site: themes, Display panel, Prism)

TITLE = "Wilson-Cowan-Notebook"
SITE = "https://zetaone.github.io/Wilson-Cowan-Notebook/"
PAPER = "https://doi.org/10.1152/jn.00404.2019"
PAPER_REF = ("C. C. Chow and Y. Karimipanah, <i>Before and beyond the Wilson&ndash;Cowan equations</i>, "
             "J. Neurophysiol. 123 (2020) 1645&ndash;1656")
PYX, XWEB, GH = "https://zetaone.github.io/pyauto-xpp/", "https://zetaone.github.io/XPPAUT-Web/", \
    "https://github.com/ZetaOne/Wilson-Cowan-Notebook"
ISO = "https://zetaone.github.io/Isochrons-Notebook/"     # the sister book
EDITOR = PYX + "editor/"                                   # pyauto-xpp's editor (runs on the reader's computer)


def editor_href(s):
    """an 'Open in editor' link for XPP files, scripts and notebooks of the study kit, or None"""
    name = Path(s[3]).name
    if Path(name).suffix not in (".ode", ".py", ".ipynb"):
        return None
    return f"{EDITOR}?open={SITE}study/files/{name}"
KATEX = "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/"
esc = html.escape

# ---- the other study material: (id, title, kind, source, chapters, group, description, extra)
# kind: page (an HTML page shown as it is), md (markdown -> themed page), pdf, image,
#       code (a script -> themed page), notebook (.ipynb -> themed page)
GROUPS = [
    ("xpp", "XPP files", "Open these in XPPAUT (or load them with pyauto-xpp). Each one is a model from the book, ready to run."),
    ("nb", "Notebooks", "Five executed notebooks, geometry first, each with a 'Try' exercise. Every simulation runs XPPAUT through pyauto-xpp."),
]
O = "ode/"
STUDY = [
    ("ode-pop1", "one_population.ode", "code", O + "one_population.ode", ["ch02"], "xpp",
     "One excitatory population: bistable for inputs between &minus;1.8 and 1.8.", {}),
    ("ode-osc", "wc_oscillator.ode", "code", O + "wc_oscillator.ode", ["ch05", "ch06"], "xpp",
     "The Wilson&ndash;Cowan pair with the parameters of their Figure 11: a limit cycle.", {}),
    ("ode-hys", "wc_hysteresis.ode", "code", O + "wc_hysteresis.ode", ["ch05", "ch07"], "xpp",
     "Their Figure 4/5 parameters: three steady states and hysteresis in <code>p</code>.", {}),
    ("ode-stm", "stm_form.ode", "code", O + "stm_form.ode", ["ch04", "ch11"], "xpp",
     "The same network written for the inputs (the STM form).", {}),
    ("ode-field", "amari_bump.ode", "code", O + "amari_bump.ode", ["ch08"], "xpp",
     "Amari's field on a ring of 240 points with a Mexican-hat kernel (XPP's <code>conv</code>): a bump that outlives its stimulus.", {}),
    ("ode-theta", "theta_network.ode", "code", O + "theta_network.ode", ["ch01", "ch12"], "xpp",
     "200 &theta;-neurons with Lorentzian excitabilities and shared synapses.", {}),
    ("ode-mpr", "mpr_mean_field.ode", "code", O + "mpr_mean_field.ode", ["ch13"], "xpp",
     "The exact Montbri&oacute;&ndash;Paz&oacute;&ndash;Roxin mean field.", {}),
    ("ode-lang", "langevin_population.ode", "code", O + "langevin_population.ode", ["ch14"], "xpp",
     "Langevin approximation of a finite stochastic population: noise-driven switching.", {}),
    ("nb1", "Notebook 1: one population", "notebook", "01_one_population.ipynb", ["ch01", "ch02"], "nb",
     "Crossings with the diagonal, the S-curve, hysteresis by ramping, folds with AUTO.", {"also": ["01_one_population.py"]}),
    ("nb2", "Notebook 2: the E&ndash;I phase plane", "notebook", "02_wc_phase_plane.ipynb", ["ch05", "ch06", "ch07"], "nb",
     "Nullclines, three steady states, the limit cycle, the Hopf point and frequency against input with AUTO.", {"also": ["02_wc_phase_plane.py"]}),
    ("nb3", "Notebook 3: neural fields", "notebook", "03_neural_fields.ipynb", ["ch08", "ch09"], "nb",
     "Amari's bump condition and a bump that remembers where the stimulus was.", {"also": ["03_neural_fields.py"]}),
    ("nb4", "Notebook 4: spiking networks and their mean field", "notebook", "04_spiking_mean_field.ipynb", ["ch12", "ch13"], "nb",
     "A &theta;-neuron raster and rate, and the exact MPR mean field: volleys versus smooth responses.", {"also": ["04_spiking_mean_field.py"]}),
    ("nb5", "Notebook 5: finite size", "notebook", "05_finite_size.ipynb", ["ch14", "ch15"], "nb",
     "Gillespie simulations, 1/N fluctuations and noise-driven switching.", {"also": ["05_finite_size.py"]}),
]
LANG = {".py": ("python", "Python"), ".sh": ("bash", "Shell"), ".ode": ("ode", "XPP .ode"),
        ".xps": ("ode", "XPP script"), ".md": ("none", "Markdown"), ".ipynb": ("none", "Notebook")}


# =============================================================================
def sync():
    subprocess.run(["rsync", "-a", "--delete", REMOTE, str(SRC) + "/"], check=True)


def copy_book():
    OUT.mkdir(exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude=.git", "--exclude=README.md", "--exclude=source", "--exclude=study", "--exclude=thumbs", "--exclude=wilson-cowan.html", "--exclude=wilson-cowan.pdf",
                    str(SRC) + "/", str(OUT) + "/"], check=True)
    # the book's files take the site's name
    for a, b in (("wc-book.html", "wilson-cowan.html"), ("wc-book.pdf", "wilson-cowan.pdf")):
        if (OUT / a).exists():
            (OUT / a).replace(OUT / b)


# ---- the book's chapters, from its own table of contents ---------------------------
def source():
    """site/source/wilson-cowan/: the scripts that make the book, decks, figures, study kit and this site."""
    d = OUT / "source" / "wilson-cowan"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(HERE.parent, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "HANDOVER.md"))


def chapters(book):
    out, part = [], None
    side = book[book.index('<nav id="side">'):book.index("</nav>")]
    for m in re.finditer(r'<li class="toc-part"><a href="#(\w+)">([^<]+)</a>|<li><a href="#(\w+)">'
                         r'<span class="tocnum">(\w+)</span> ([^<]+)</a>', side):
        if m.group(1):
            i = book.index(f'id="{m.group(1)}"')
            blurb = re.search(r'<p class="part-blurb">(.*?)</p>', book[i:i + 3000])
            kick = re.search(r'<div class="part-kicker">(.*?)</div>', book[i:i + 400])
            part = {"id": m.group(1), "title": html.unescape(m.group(2)), "chapters": [],
                    "blurb": blurb.group(1) if blurb else "", "kicker": kick.group(1) if kick else ""}
            out.append(part)
        else:
            cid = m.group(3)
            i = book.index(f'<section class="chapter" id="{cid}"')
            j = book.find('<section class="', i + 10)
            sec = book[i:j if j > 0 else len(book)]
            sub = re.search(r'<p class="chap-sub">(.*?)</p>', sec)
            img = re.search(r'<img src="(figs/[^"]+)"', sec)
            part["chapters"].append({
                "id": cid, "num": m.group(4), "title": html.unescape(m.group(5)), "sub": sub.group(1) if sub else "",
                "img": img.group(1) if img else None,
                "deck": f"decks/{cid}/wc-{cid}_deck.html" if (SRC / "decks" / cid).is_dir() else None,
                "code": f"code/{cid}_figs.html" if (SRC / "code" / f"{cid}_figs.html").exists() else
                        (f"code/{cid}.html" if (SRC / "code" / f"{cid}.html").exists() else None),
                "slides": len(re.findall(r"<section ", (SRC / "decks" / cid / f"wc-{cid}_deck.html").read_text()))
                          if (SRC / "decks" / cid).is_dir() else 0})
    return out


def thumbs(parts):
    (OUT / "thumbs").mkdir(exist_ok=True)
    man = json.loads((SRC / "figs" / "manifest.json").read_text())
    by_file = {}
    for v in man.values():
        for k in ("file", "gif", "png", "still"):
            if v.get(k):
                by_file[v[k]] = v
    for p in parts:
        for c in p["chapters"]:
            if not c["img"]:
                continue
            name = Path(c["img"]).name
            v = by_file.get(name, {})
            png = v.get("png") or v.get("still") or (name if name.endswith(".png") else None)
            if not png or not (SRC / "figs" / png).exists():
                c["thumb"] = None
                continue
            im = Image.open(SRC / "figs" / png).convert("RGB")
            im.thumbnail((560, 360))
            im.save(OUT / "thumbs" / f"{c['id']}.webp", quality=82)
            c["thumb"] = f"thumbs/{c['id']}.webp"


def logo():
    """a square icon from the Wilson–Cowan limit cycle figure"""
    im = Image.open(SRC / "figs" / "ch09_logpolar.png").convert("RGB")
    w0, h0 = im.size
    im = im.crop((int(0.755 * w0), int(0.52 * h0), w0, h0))
    w, h = im.size
    s = min(w, h)
    box = ((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)
    sq = im.crop(box)
    for n in (32, 192, 512):
        sq.resize((n, n), Image.LANCZOS).save(OUT / f"icon-{n}.png")


# ---- the page shell (pyauto-xpp's toolbar, themes and Display panel) ------------------
def display_head():
    # new visitors start with the Light theme here (the book is a book); a choice made on
    # the pyauto-xpp site is shared, as the two sites share an origin and the keys
    return M.display_head().replace("'funky2'", "'light'")


NAV = [("index.html#book", "Book"), ("index.html#chapters", "Chapters"), ("index.html#study", "Study kit"),
       ("code/index.html", "Code"), ("index.html#highlights", "My highlights")]

SITE_CSS = r"""
html { scroll-behavior: smooth }
body { margin: 0; background: var(--bg); color: var(--fg); line-height: 1.55 }
a { color: var(--accent) }
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 20px }
.nav { display: flex; gap: 2px }
.nav a { padding: 8px 10px; border-radius: 6px; color: var(--fg); text-decoration: none }
.nav a:hover { background: var(--panel-bar-active) }
.menu { display: none }
h1, h2, h3 { line-height: 1.2 }
h2 { font-size: 1.5rem; margin: 2.2rem 0 .4rem }
.lead { color: var(--muted); margin: 0 0 1rem; max-width: 60rem }
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 9px 16px; border-radius: 8px; border: 1px solid var(--accent);
       background: var(--accent); color: var(--accent-fg); font-weight: 600; text-decoration: none; font-size: .9375rem; cursor: pointer }
.btn.ghost { background: transparent; color: var(--fg); border-color: var(--line) }
.btn.ghost:hover { border-color: var(--accent) }
.btn small { font-weight: 400; opacity: .8 }
.tag { display: inline-block; padding: 1px 8px; border-radius: 999px; border: 1px solid var(--line); font-size: .75rem;
       color: var(--muted); text-decoration: none; white-space: nowrap }
a.tag:hover { border-color: var(--accent); color: var(--fg) }
.fig-bg { background: #fff; border-radius: 8px }
footer { margin-top: 48px; padding: 22px 0 30px; border-top: 1px solid var(--line); background: var(--bar);
         font-size: .84375rem; color: var(--muted) }
footer a { color: var(--fg) }
@media (max-width: 760px) {
  .nav { display: none }
  .menu { display: block }
}
"""

CODE_CSS = r"""
:root[data-code='dark'] { --cb-bg: #1e1e1e; --cb-head: #252526; --cb-headfg: #c5c5c5; --cb-line: #3c3c3c; --cb-fg: #d4d4d4; --cb-num: #6e7681 }
:root[data-code='light'] { --cb-bg: #ffffff; --cb-head: #f3f3f3; --cb-headfg: #5c5c5c; --cb-line: #dcdcdc; --cb-fg: #1f1f1f; --cb-num: #9a9a9a }
.cb { margin: 1em 0 1.3em; border: 1px solid var(--cb-line); border-radius: 8px; overflow: hidden; background: var(--cb-bg) }
.cb-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 32px; padding: 0 6px 0 12px;
       background: var(--cb-head); color: var(--cb-headfg); border-bottom: 1px solid var(--cb-line); font-size: .75rem }
.cb-head button, .cb-head a { font: inherit; color: inherit; background: transparent; border: 1px solid var(--cb-line); border-radius: 5px;
       padding: 3px 9px; cursor: pointer; text-decoration: none }
.cb-body { display: grid; grid-template-columns: auto 1fr; overflow-x: auto }
.cb pre { margin: 0; padding: 12px 14px; font: .8125rem/1.55 var(--font-mono); background: transparent !important; color: var(--cb-fg);
       tab-size: 4; overflow: visible }
.cb pre code { font: inherit; background: transparent !important; text-shadow: none }
.cb pre.ln { color: var(--cb-num); text-align: right; user-select: none; padding-right: 10px; border-right: 1px solid var(--cb-line) }
.cb.out { background: color-mix(in srgb, var(--cb-bg) 94%, var(--fg)) }
.cb.out pre { white-space: pre-wrap }
.doc { max-width: 52rem }
.doc img { max-width: 100%; background: #fff; border-radius: 6px }
.doc table { border-collapse: collapse; margin: 1em 0; font-size: .9375rem }
.doc th, .doc td { border: 1px solid var(--line); padding: 4px 10px; text-align: left; vertical-align: top }
.doc code { font-size: .875em; background: color-mix(in srgb, var(--fg) 8%, transparent); padding: 1px 4px; border-radius: 4px }
.doc pre code { background: transparent; padding: 0 }
.doc blockquote { margin: 1em 0; padding: .2em 1em; border-left: 3px solid var(--accent); color: var(--muted) }
.crumbs { font-size: .875rem; color: var(--muted); margin: 18px 0 0 }
.crumbs a { color: var(--muted) }
.pagehead h1 { font-size: 1.75rem; margin: .3rem 0 .4rem; font-family: var(--font-mono) }
.pagehead h1.prose { font-family: inherit }
.pagehead p { margin: .2rem 0 .6rem; color: var(--muted); max-width: 52rem }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: .6rem 0 }
.figs { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; margin: 1rem 0 }
.figs a { display: block; background: #fff; border-radius: 8px; border: 1px solid var(--line); overflow: hidden }
.figs img { width: 100%; display: block }
.cell-md { margin: 1.2rem 0 }
.cell-n { font: .6875rem var(--font-mono); color: var(--muted); margin: 1rem 0 -.6rem }
.cell-img { max-width: 100%; background: #fff; border-radius: 6px; display: block; margin: .4rem 0 1rem }
.flist { list-style: none; padding: 0; display: grid; gap: 8px }
.flist li { display: grid; grid-template-columns: minmax(12rem, auto) 1fr; gap: 4px 14px; padding: 10px 12px; background: var(--bar);
            border: 1px solid var(--line); border-radius: 8px }
.flist li a { font-family: var(--font-mono); font-weight: 600 }
.flist li span { color: var(--muted) }
@media (max-width: 760px) { .flist li { grid-template-columns: 1fr } }
"""

ODE_GRAMMAR = r"""
if (window.Prism && Prism.languages) {
  Prism.languages.ode = {
    'after-done': { pattern: /(^done[ \t]*\n)[\s\S]*/m, lookbehind: true, alias: 'comment' },
    comment: [{ pattern: /(^|\s)#.*/m, lookbehind: true }, { pattern: /^\s*".*/m }],
    keyword: { pattern: /^(\s*)(?:par(?:am)?|p|init|i|aux|number|num|done|set|global|table|wiener|markov|bdry|volt|special|only|export|options|load|keys|autokeys|ans|auto|try|else|end|for|shot|quit|msg|speed)\b|^\s*@/m, lookbehind: true },
    property: { pattern: /^(\s*)(?:\w+'|d\w+\/dt|\w+\(t\+dt\))(?=\s*=)/m, lookbehind: true },
    function: /\b\w+(?=\()/,
    number: /(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?\b/i,
    operator: /[-+*\/^=<>!]/,
    punctuation: /[(){},;\[\]]/,
  };
  try { Prism.highlightAll() } catch (e) {}
}
for (const b of document.querySelectorAll('.cb-copy')) b.addEventListener('click', async () => {
  const t = b.closest('.cb').querySelector('pre:not(.ln) code').textContent;
  try { await navigator.clipboard.writeText(t); b.textContent = 'Copied' } catch (e) { b.textContent = 'Select and copy' }
  setTimeout(() => b.textContent = 'Copy', 1500);
});
"""


def page(title, body, rel="", desc="", code=False, math=False, extra_head="", extra_js=""):
    prism_css = "".join(f'<link rel="stylesheet" data-code="{k}" href="{M.CDN}{f}" integrity="{sri}" '
                        f'crossorigin="anonymous" referrerpolicy="no-referrer">' for k, (f, sri) in M.PRISM_CSS.items())
    prism_js = "".join(f'<script src="{M.CDN}{f}" integrity="{sri}" crossorigin="anonymous" '
                       f'referrerpolicy="no-referrer"></script>' for f, sri in M.PRISM_JS)
    katex_head = (f'<link rel="stylesheet" href="{KATEX}katex.min.css">' if math else "")
    katex_js = (f'<script src="{KATEX}katex.min.js"></script><script src="{KATEX}contrib/auto-render.min.js"></script>'
                '<script>renderMathInElement(document.querySelector("main"),{delimiters:[{left:"$$",right:"$$",display:true},'
                '{left:"\\\\[",right:"\\\\]",display:true},{left:"\\\\(",right:"\\\\)",display:false},'
                '{left:"$",right:"$",display:false}],ignoredTags:["script","noscript","style","textarea","pre","code"],'
                'throwOnError:false})</script>' if math else "")
    nav = "".join(f'<a href="{rel}{h}">{t}</a>' for h, t in NAV)
    navmenu = "".join(f'<a role="menuitem" href="{rel}{h}">{t}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc or TITLE)}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{rel}icon-32.png"><link rel="apple-touch-icon" href="{rel}icon-192.png">
{display_head()}
{prism_css if code else ""}{katex_head}
<style>{M.theme_css()}
{M.TOOLBAR_CSS}
{M.DISPLAY_CSS}
{SITE_CSS}
{CODE_CSS if (code or math) else ""}</style>
{extra_head}
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <a class="brand" href="{rel}index.html"><img src="{rel}icon-192.png" alt="" width="22" height="22">{TITLE}</a>
  <nav class="nav" aria-label="Sections">{nav}</nav>
  <div class="right">
    {M.DISPLAY_BUTTON}
    <details class="menu"><summary class="round" aria-label="Menu" title="Menu">{M.ICON_MENU}</summary>
      <div class="panel" role="menu">{navmenu}<a role="menuitem" href="{PAPER}" target="_blank" rel="noopener">The paper (PDF)</a></div></details>
  </div>
</header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
  <p><b style="color:var(--fg)">{TITLE}</b>, a guided reading of {PAPER_REF}
     (<a href="{PAPER}" target="_blank" rel="noopener">the paper</a>).
     Every simulation is computed by Bard Ermentrout's
     <a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a>
     through <a href="{PYX}">pyauto-xpp</a>.</p>
  <p><a href="{PYX}">pyauto-xpp</a> &middot; <a href="{XWEB}">XPPAUT-Web</a> &middot; <a href="{ISO}">Isochrons-Notebook</a></p>
  <p>Made by Jeevan Kumar Gochhayat (<a href="https://github.com/ZetaOne">github.com/ZetaOne</a>) &middot; <a href="{GH}">Source of this site</a></p>
</div></footer>
{prism_js if code else ""}
<script>{M.display_js()}</script>
{"<script>" + ODE_GRAMMAR + "</script>" if code else ""}
{katex_js}
{extra_js}
</body></html>
"""


def codeblock(text, lang, label, raw_href=None, name=""):
    n = text.count("\n") + (0 if text.endswith("\n") else 1)
    ln = "\n".join(str(i) for i in range(1, n + 1))
    dl = f'<a href="{raw_href}" download>Download</a>' if raw_href else ""
    cls = f' class="language-{lang}"' if lang != "none" else ""
    return (f'<div class="cb"><div class="cb-head"><span>{esc(name or label)} &middot; {n} lines</span>'
            f'<span class="row" style="margin:0"><button type="button" class="cb-copy">Copy</button>{dl}</span></div>'
            f'<div class="cb-body"><pre class="ln" aria-hidden="true">{ln}</pre>'
            f'<pre><code{cls}>{esc(text)}</code></pre></div></div>')


# ---- the book's own code pages, themed (code/*.html from code/raw/*) -----------------
def book_code():
    idx = (SRC / "code" / "index.html").read_text()
    descs = dict(re.findall(r'<a href="([\w.]+)\.html">[^<]*</a>\s*(?:</?\w+[^>]*>\s*)*(?:—|&mdash;|-)?\s*([^<]+)', idx))
    rows = []
    order = ["wc_lib", "figkit", "deckkit"]
    raws = sorted((SRC / "code" / "raw").glob("*.py"), key=lambda p: (p.stem not in order,
                  order.index(p.stem) if p.stem in order else 0, p.stem))
    for p in raws:
        d = descs.get(p.stem, "").strip()
        ch = re.match(r"(ch\d+b?)", p.stem)
        body = f"""<div class="wrap">
<p class="crumbs"><a href="../index.html">Library</a> / <a href="index.html">Code</a> / {esc(p.name)}</p>
<div class="pagehead"><h1>{esc(p.name)}</h1><p>{esc(d)}</p>
<div class="row">{f'<a class="btn ghost" href="../wilson-cowan.html#{ch.group(1)}">Read chapter</a>' if ch else ''}
<a class="btn ghost" href="raw/{p.name}" download>Download</a></div></div>
{codeblock(p.read_text(), "python", "Python", f"raw/{p.name}", p.name)}
</div>"""
        (OUT / "code" / f"{p.stem}.html").write_text(page(f"{p.name} · {TITLE}", body, "../", d, code=True))
        rows.append(f'<li><a href="{p.stem}.html">{esc(p.name)}</a><span>{esc(d)}</span></li>')
    study = "".join(f'<li><a href="../study/{s[0]}.html">{esc(Path(s[3]).name)}</a><span>{s[6]}</span></li>'
                    for s in STUDY if s[2] in ("code", "notebook"))
    body = f"""<div class="wrap">
<p class="crumbs"><a href="../index.html">Library</a> / Code</p>
<div class="pagehead"><h1 class="prose">The code</h1>
<p>Every number and figure in the book was computed by these scripts, with XPPAUT 8.4 through pyauto-xpp.
<code>iso_lib.py</code> holds the numerics; each <code>chNN_figs.py</code> draws one chapter's figures.</p></div>
<h2>Behind the book</h2><ul class="flist">{''.join(rows)}</ul>
<h2>Study kit</h2><p class="lead">Scripts, XPP files and notebooks for working through the paper yourself.</p>
<ul class="flist">{study}</ul></div>"""
    (OUT / "code" / "index.html").write_text(page(f"Code · {TITLE}", body, "../", "The code behind the Wilson–Cowan book"))


# ---- study material ----------------------------------------------------------------------
def md_html(path):
    r = subprocess.run([shutil.which("pandoc") or str(Path.home() / "anaconda3/envs/nrnbase/bin/pandoc"), "-f", "markdown", "-t", "html", "--mathjax", str(path)],
                       capture_output=True, text=True, check=True)
    return r.stdout


def chap_tags(chs, names, rel):
    return " ".join(f'<a class="tag" href="{rel}wilson-cowan.html#{c}">Ch. {names[c][0]} &middot; {esc(names[c][1])}</a>'
                    for c in chs if c in names)


def notebook_html(path, sid):
    nb = json.loads(path.read_text())
    out, k = [], 0
    (OUT / "study" / "nb").mkdir(parents=True, exist_ok=True)
    for cell in nb["cells"]:
        src = "".join(cell.get("source", ""))
        if not src.strip() and cell["cell_type"] != "code":
            continue
        if cell["cell_type"] == "markdown":
            r = subprocess.run([shutil.which("pandoc") or str(Path.home() / "anaconda3/envs/nrnbase/bin/pandoc"), "-f", "markdown", "-t", "html", "--mathjax"], input=src,
                               capture_output=True, text=True, check=True)
            out.append(f'<div class="cell-md doc">{r.stdout}</div>')
        elif cell["cell_type"] == "code":
            out.append(codeblock(src, "python", "Python", None, f"In [{cell.get('execution_count') or ' '}]"))
            for o in cell.get("outputs", []):
                if o.get("output_type") == "stream":
                    t = "".join(o.get("text", ""))
                    out.append(f'<div class="cb out"><pre>{esc(t)}</pre></div>')
                elif o.get("output_type") in ("execute_result", "display_data"):
                    d = o.get("data", {})
                    if "image/png" in d:
                        import base64
                        k += 1
                        f = OUT / "study" / "nb" / f"{sid}_{k}.png"
                        f.write_bytes(base64.b64decode("".join(d["image/png"])))
                        out.append(f'<img class="cell-img" loading="lazy" src="nb/{f.name}" alt="output figure">')
                    elif "text/plain" in d:
                        out.append(f'<div class="cb out"><pre>{esc("".join(d["text/plain"]))}</pre></div>')
                elif o.get("output_type") == "error":
                    out.append(f'<div class="cb out"><pre>{esc(o.get("ename", ""))}: {esc(o.get("evalue", ""))}</pre></div>')
    return "\n".join(out)


def study(names):
    d = OUT / "study"
    if d.exists():
        shutil.rmtree(d)
    (d / "files").mkdir(parents=True)
    for s_full in STUDY:
        sid, title, kind, src, chs, group, desc, extra = s_full
        src = DOCS / src
        if kind == "page":
            shutil.copy2(src, d / src.name)
            continue
        if kind == "image":
            shutil.copy2(src, d / "files" / src.name)
            continue
        shutil.copy2(src, d / "files" / src.name)
        for a in extra.get("also", []) + ([extra["pdf"]] if "pdf" in extra else []) + extra.get("assets", []):
            shutil.copy2(DOCS / a, d / "files" / Path(a).name)
        figs = ""
        if extra.get("figs"):
            (d / "figs").mkdir(exist_ok=True)
            items = []
            for f in extra["figs"]:
                f = DOCS / f
                tgt = f"{sid}_{f.name}"
                shutil.copy2(f, d / "figs" / tgt)
                items.append(f'<a href="figs/{tgt}"><img loading="lazy" src="figs/{tgt}" alt="{esc(f.stem)}"></a>')
            figs = f'<h2>What it draws</h2><div class="figs">{"".join(items)}</div>'
        also = "".join(f'<a class="btn ghost" href="files/{Path(a).name}" download>{esc(Path(a).name)}</a>'
                       for a in extra.get("also", []))
        if "pdf" in extra:
            also += f'<a class="btn ghost" href="files/{Path(extra["pdf"]).name}">PDF version</a>'
        lang, label = LANG[src.suffix]
        math = False
        if kind == "code":
            content = figs + "<h2>The code</h2>" + codeblock(src.read_text(), lang, label, f"files/{src.name}", src.name)
            h1 = f"<h1>{esc(src.name)}</h1>" if title == src.name else f'<h1 class="prose">{title}</h1>'
        elif kind == "md":
            body_html = md_html(src).replace('src="algorithm-isochron-flow.png"', 'src="files/algorithm-isochron-flow.png"')
            # the title block of the markdown file, if any, is in its YAML header
            content = f'<div class="doc">{body_html}</div>'
            h1 = f'<h1 class="prose">{title}</h1>'
            math = True
        elif kind == "notebook":
            content = notebook_html(src, sid)
            h1 = f'<h1 class="prose">{title}</h1>'
            math = True
        dl = f'<a class="btn ghost" href="files/{src.name}" download>Download {esc(src.name)}</a>'
        if editor_href(s_full):
            dl = f'<a class="btn" href="{editor_href(s_full)}" target="_blank" rel="noopener" title="Runs on your computer through pyauto-xpp">Open in editor</a>' + dl
        body = f"""<div class="wrap">
<p class="crumbs"><a href="../index.html">Library</a> / <a href="../index.html#study">Study kit</a> / {esc(src.name)}</p>
<div class="pagehead">{h1}<p>{desc}</p>
<div class="row">{chap_tags(chs, names, "../")}</div>
<div class="row">{dl}{also}</div></div>
{content}
</div>"""
        (d / f"{sid}.html").write_text(page(f"{html.unescape(re.sub('<[^>]+>', '', title))} · {TITLE}", body, "../",
                                            html.unescape(re.sub("<[^>]+>", "", desc)), code=(kind != "md"), math=math))


def study_href(s):
    sid, title, kind, src = s[:4]
    if kind == "page":
        return f"study/{Path(src).name}"
    if kind == "image":
        return f"study/files/{Path(src).name}"
    return f"study/{sid}.html"


# ---- the book page: Display panel + highlights ------------------------------------------
BOOK_CSS = r"""
/* the book follows the site's theme: its colours become the theme's */
:root { --ink: var(--fg); --paper: var(--bg); --rule: var(--line); --side: var(--bar); --link: var(--accent);
  --accent2: color-mix(in srgb, #c0407a 75%, var(--fg));
  --def: color-mix(in srgb, #0e9aa6 13%, var(--bg)); --thm: color-mix(in srgb, #7b4fc0 12%, var(--bg));
  --idea: color-mix(in srgb, #e0a800 15%, var(--bg)); --ex: color-mix(in srgb, #4f9a3a 12%, var(--bg));
  --warn: color-mix(in srgb, #d0453a 12%, var(--bg)); --paper-box: color-mix(in srgb, #3a6fd0 11%, var(--bg));
  --key: color-mix(in srgb, #d04a8a 11%, var(--bg)); --try: color-mix(in srgb, var(--fg) 6%, var(--bg));
  --recap: color-mix(in srgb, #4f9a3a 8%, var(--bg)) }
body { font-size: 1.0625rem }
:root[data-font='system'] body, :root:not([data-font]) body { font-family: Charter, 'Bitstream Charter', 'Iowan Old Style', 'Palatino Linotype', Georgia, serif }
#side { font-size: .875rem }
main img { background: #fff; border-radius: 4px }
main table { display: block; max-width: 100%; overflow-x: auto }
"""


def book_page():
    p = OUT / "wilson-cowan.html"
    s = (SRC / "wc-book.html").read_text()
    head = (f'{display_head()}\n<meta name="theme-color" content="#ffffff">'
            f'<link rel="icon" href="icon-32.png">\n<style>{M.theme_css()}\n{M.TOOLBAR_CSS}\n{M.DISPLAY_CSS}\n{BOOK_CSS}</style>\n'
            f'<link rel="stylesheet" href="reader.css">\n')
    tools = f"""<header class="rtools hl-ui" aria-label="Reading tools">
  <a class="rt" href="index.html" title="Book, slides, code and study kit">&larr; Library</a>
  <a class="rt" href="{PAPER}" target="_blank" rel="noopener" title="Chow &amp; Karimipanah (2020), the review">Review</a>
  <button type="button" class="rt" id="hl-open" title="My highlights and notes">Highlights <span class="hl-fab-n"></span></button>
  {M.DISPLAY_BUTTON}
</header>
<script>{M.display_js()}</script>
<script src="reader.js"></script>
"""
    s = re.sub(r"<title>[^<]*</title>", f"<title>{TITLE}</title>", s, count=1)
    s = re.sub(r'(<h1 class="cover-title">)[^<]*(</h1>)', rf"\g<1>{TITLE}\g<2>", s, count=1)
    s = re.sub(r'<div class="side-title">[^<]*</div>', f'<div class="side-title">{TITLE}</div>', s, count=1)
    s = s.replace("</head>", head + "</head>", 1)
    i = s.rindex("</body>")
    s = s[:i] + tools + s[i:]
    p.write_text(s)


def decks(parts):
    for pt in parts:
        for c in pt["chapters"]:
            if not c["deck"]:
                continue
            f = OUT / c["deck"]
            s = f.read_text()
            t = f"Chapter {c['num']}: {c['title']} (slides)"
            s = s.replace("<title>Manim Slides</title>", f'<title>{esc(t)}</title><link rel="icon" href="../../icon-32.png">', 1)
            i = s.rindex("</body>")
            s = (s[:i] + f'<script src="../../deck.js" data-deck="{c["id"]}" data-title="{esc(t)}"></script>\n' + s[i:])
            f.write_text(s)


# ---- the library (index.html) ----------------------------------------------------------
def index(parts, names):
    by_ch = {}
    for s in STUDY:
        for c in s[4]:
            by_ch.setdefault(c, []).append(s)
    cards = []
    for p in parts:
        items = []
        for c in p["chapters"]:
            th = (f'<img class="fig-bg" loading="lazy" src="{c["thumb"]}" alt="">' if c.get("thumb") else
                  '<div class="fig-bg ph"></div>')
            acts = [f'<a class="act" href="wilson-cowan.html#{c["id"]}">Read</a>']
            if c["deck"]:
                acts.append(f'<a class="act" href="{c["deck"]}">Slides <small>{c["slides"]}</small></a>')
            if c["code"]:
                acts.append(f'<a class="act" href="{c["code"]}">Code</a>')
            kit = by_ch.get(c["id"], [])
            kit_html = ("".join(f'<a class="tag" href="{study_href(s)}">{s[1]}</a>' for s in kit[:6])
                        + (f'<a class="tag" href="#study">+{len(kit) - 6} more</a>' if len(kit) > 6 else ""))
            items.append(f"""<article class="chap" id="c-{c['id']}">
  <a class="thumb" href="wilson-cowan.html#{c['id']}" tabindex="-1" aria-hidden="true">{th}</a>
  <div class="ctext">
    <div class="ckick">Chapter {c['num']} <span class="cstat" data-hlc="{c['id']}"></span><span class="cstat" data-deck="{c['id']}" data-n="{c['slides']}"></span></div>
    <h3><a href="wilson-cowan.html#{c['id']}">{esc(c['title'])}</a></h3>
    <p>{c['sub']}</p>
    <div class="acts">{''.join(acts)}</div>
    {f'<div class="kit"><span>Study:</span> {kit_html}</div>' if kit else ''}
  </div>
</article>""")
        cards.append(f"""<section class="part" id="p-{p['id']}">
  <div class="pkick">{p['kicker']}</div><h3 class="ptitle">{esc(p['title'])}</h3><p class="lead">{p['blurb']}</p>
  <div class="chaps">{''.join(items)}</div>
</section>""")
    groups = []
    for g, gt, gd in GROUPS:
        its = [s for s in STUDY if s[5] == g]
        lis = []
        for s in its:
            kindlabel = {"page": "page", "md": "page + PDF" if "pdf" in s[7] else "page", "pdf": "PDF",
                         "image": "figure", "code": LANG.get(Path(s[3]).suffix, ("", ""))[1], "notebook": "notebook"}[s[2]]
            tags = " ".join(f'<a class="tag" href="wilson-cowan.html#{c}">{names[c][0]}</a>' for c in s[4] if c in names)
            lis.append(f"""<li><a class="kt" href="{study_href(s)}">{s[1]}</a> <span class="kk">{kindlabel}</span>
  <p>{s[6]}</p><div class="ktags"><span>Chapters</span> {tags}{(f'<a class="kopen" href="{editor_href(s)}" target="_blank" rel="noopener" title="Open it in the pyauto-xpp editor, which runs it on your computer">Open in editor</a>') if editor_href(s) else ""}</div></li>""")
        groups.append(f'<div class="kgroup"><h3>{gt}</h3><p class="lead">{gd}</p><ul class="klist">{"".join(lis)}</ul></div>')
    nch = sum(len(p["chapters"]) for p in parts)
    ndeck = sum(1 for p in parts for c in p["chapters"] if c["deck"])
    pdf_mb = (OUT / "wilson-cowan.pdf").stat().st_size / 1e6
    body = f"""
<section class="hero" id="book"><div class="wrap">
  <div class="htext">
    <div class="kicker">A book in four parts, with slides, code and a study kit</div>
    <h1>{TITLE}</h1>
    <p class="sub">From spiking networks to activity equations and beyond mean field: a guided reading of
      {PAPER_REF}, and of Wilson &amp; Cowan (1972).</p>
    <div class="row">
      <a class="btn" href="wilson-cowan.html">Read the book</a>
      <a class="btn" id="resume" href="wilson-cowan.html#resume" hidden>Continue reading</a>
      <a class="btn ghost" href="wilson-cowan.pdf">PDF <small>{pdf_mb:.0f} MB</small></a>
      <a class="btn ghost" href="{PAPER}" target="_blank" rel="noopener">The review &#8599;</a>
    </div>
    <p class="hstats">{nch} chapters &middot; {ndeck} slide decks &middot; every figure's code &middot; a study kit of
      scripts, XPP files and notebooks. Highlights and notes you make in the book stay in this browser.
      The book has 18 themes: pick one from the Theme button at its bottom right.</p>
  </div>
  <a class="cover" href="wilson-cowan.html"><img class="fig-bg" src="figs/ch06_fig11.png" alt="Cover: the Wilson–Cowan limit cycle"></a>
</div></section>

<div class="wrap">
<h2 id="chapters">Chapters</h2>
<p class="lead">Each chapter has its slide deck (arrow keys or space to step; the deck remembers where you stopped),
  the code behind its figures, and the study material that goes with it.</p>
{''.join(cards)}

<h2 id="study">Study kit</h2>
<p class="lead">XPP files, scripts and notebooks for working through the Wilson&ndash;Cowan equations yourself. The tags show the chapters each
  item goes with.</p>
<div class="kit-grid">{''.join(groups)}</div>

<h2 id="highlights">My highlights</h2>
<p class="lead">Select text in the book and pick a colour; click a highlight to add a note. They are kept in this
  browser only (Export moves them to another device).</p>
<div id="myhl" class="myhl"><p class="muted">No highlights yet.</p></div>
</div>
"""
    head = f'<link rel="stylesheet" href="library.css">'
    js = f'<script>window.ISO_CHAPTERS = {json.dumps({k: v for k, v in names.items()})};</script><script src="library.js"></script>'
    (OUT / "index.html").write_text(page(TITLE, body, "", "A book, slide decks, code and a study kit on the Wilson–Cowan equations", extra_head=head, extra_js=js))


def main():

    copy_book()
    book = (SRC / "wc-book.html").read_text()
    parts = chapters(book)
    names = {c["id"]: (c["num"], c["title"]) for p in parts for c in p["chapters"]}
    thumbs(parts)
    logo()
    for f in WEB.iterdir():
        shutil.copy2(f, OUT / f.name)
    book_page()
    decks(parts)
    book_code()
    study(names)
    index(parts, names)
    source()
    (OUT / ".nojekyll").write_text("")
    (OUT / "README.md").write_text(f"""# {TITLE}

**The website: {SITE}**

A book on the Wilson&ndash;Cowan model of neuronal populations, from the basics up, following
C. C. Chow and Y. Karimipanah, *Before and beyond the Wilson&ndash;Cowan equations*, J. Neurophysiol. 123
(2020) 1645-1656 ([the paper]({PAPER})), together with Wilson & Cowan (1972).

## What is on the site

- **The book**: 16 chapters and 3 appendices, from why populations and the sigmoid, through the E&ndash;I
  phase plane, oscillations, multistability, neural fields and patterns, to spiking mean fields,
  finite-size effects and path integrals; in the browser or as a PDF.
- **Slide decks**, one per chapter, geometry first; each remembers the slide you stopped at.
- **The code** behind every figure, to read or download.
- **A study kit**: XPP `.ode` files and executed notebooks.
- **Your reading**, kept in your own browser only: highlights and notes, where you stopped, your
  progress in each deck. Nothing is sent anywhere.

Every simulation is computed by Bard Ermentrout's
[XPPAUT](https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html) through [pyauto-xpp]({PYX}); the
models can also be explored in the browser with [XPPAUT-Web]({XWEB}). Its sister book:
[Isochrons-Notebook]({ISO}).

## About this repository

The site files here are generated: they are rebuilt from the book's sources, so changes go into
those, not into these files. GitHub Pages publishes the `main` branch.

The sources are in [`source/wilson-cowan/`](source/wilson-cowan/), copied in on every build:

- `book/`: the chapters (Markdown) and the book builder (`build.mjs`, `build_code.py`)
- `figs/`: one script per figure; `wc_lib.py`, `figkit.py`: the shared model code and plot style
- `decks/`: one slide-deck script per chapter (ManimGX through `sciviz`, the animation tools of
  this project, which are not included here) and `render_all.sh`
- `study/`: the XPP `.ode` files of the study kit and `make_notebooks.py`, which writes its notebooks
- `site/`: this website's builder (`build.py`) and its page assets

Made by Jeevan Kumar Gochhayat ([github.com/ZetaOne](https://github.com/ZetaOne)).
""")
    print(f"built {OUT}: {sum(len(p['chapters']) for p in parts)} chapters, {len(STUDY)} study items")


if __name__ == "__main__":
    main()
