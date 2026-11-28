"""Build the local theme gallery for the Wilson–Cowan book.

Reads rendered-anims/wilson-cowan/book/wc-book.html, extracts Chapter 5 and the side nav,
and writes one preview page per theme into rendered-anims/wilson-cowan/themes/,
plus screenshots (headless Chrome) and an index.html gallery.
Theme CSS files are expected in themes/css/ (downloaded from jsDelivr, pinned versions).

Usage: .venv/bin/python scripts/wilson-cowan/build_theme_gallery.py [--no-shots]
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "rendered-anims/wilson-cowan/book/wc-book.html"
OUT = ROOT / "rendered-anims/wilson-cowan/themes"
CHAPTER = "ch05"

# key, name, repo, licence, package@version/file, look, mode ("light"/"dark"/"auto"), extra
THEMES = [
    ("current", "Classic", "", "(this project)", "inline <style> of wc-book.html",
     "The present look: warm off-white paper, serif headings, coloured note boxes.", "light"),
    ("tufte", "Tufte", "https://github.com/edwardtufte/tufte-css", "MIT", "tufte-css@1.9.0/tufte.min.css",
     "Edward Tufte's book style: cream paper, ET Book serif, narrow text column with wide margin.", "auto"),
    ("latex", "LaTeX", "https://github.com/vincentdoerig/latex-css", "MIT", "latex.css@1.14.0/style.min.css",
     "Looks like a LaTeX article: Latin Modern font, white page, justified text (opt-in dark class latex-dark / latex-dark-auto).", "light"),
    ("pico", "Pico", "https://github.com/picocss/pico", "MIT", "@picocss/pico@2.1.1/css/pico.classless.min.css",
     "Modern UI framework look: system sans, generous spacing, blue accents.", "auto"),
    ("water-light", "Water", "https://github.com/kognise/water.css", "MIT", "water.css@2.1.1/out/light.min.css",
     "Clean system-sans page, soft grey code/blocks, blue links.", "light"),
    ("water-dark", "Ink", "https://github.com/kognise/water.css", "MIT", "water.css@2.1.1/out/dark.min.css",
     "Same as Water light on a dark slate background.", "dark"),
    ("simple", "Simple", "https://github.com/kevquirk/simple.css", "MIT", "simpledotcss@2.3.7/simple.min.css",
     "Minimal centred column, system sans, light-grey header band, follows OS dark mode.", "auto"),
    ("sakura", "Sakura", "https://github.com/oxalorg/sakura", "MIT", "sakura.css@1.5.1/css/sakura.css",
     "Small minimal theme: off-white page, Helvetica-style sans, teal links, large headings.", "light"),
    ("sakura-dark", "Dusk", "https://github.com/oxalorg/sakura", "MIT", "sakura.css@1.5.1/css/sakura-dark.css",
     "Sakura on near-black with soft accents.", "dark"),
    ("sakura-earthly", "Moss", "https://github.com/oxalorg/sakura", "MIT", "sakura.css@1.5.1/css/sakura-earthly.css",
     "Sakura variant with muted green/earth accents.", "light"),
    ("newcss", "Fresh", "https://github.com/xz/new.css", "MIT", "@exampledev/new.css@1.1.3/new.css",
     "Bold dark header-style headings, system sans, blue links, auto dark.", "auto"),
    ("mvp", "Bold", "https://github.com/andybrewer/mvp", "MIT", "mvp.css@1.18.0/mvp.css",
     "Landing-page style: large type, rounded cards, blue accents, auto dark.", "auto"),
    ("awsm", "Essay", "https://github.com/igoradamenko/awsm.css", "MIT", "awsm.css@3.0.7/dist/awsm.min.css",
     "Blog-article look: narrow centred column, system sans, grey-filled tables/blocks, small caps-like headings.", "light"),
    ("github-light", "GitHub", "https://github.com/sindresorhus/github-markdown-css", "MIT",
     "github-markdown-css@5.9.0/github-markdown-light.css",
     "Exactly how a README looks on GitHub: system sans, ruled h1/h2, grey tables.", "light"),
    ("github-dark", "GitHub Night", "https://github.com/sindresorhus/github-markdown-css", "MIT",
     "github-markdown-css@5.9.0/github-markdown-dark.css",
     "GitHub's dark README look.", "dark"),
    ("bamboo", "Nord", "https://github.com/rilwis/bamboo", "MIT", "bamboo.css@1.4.0/dist/light.min.css",
     "Nord-inspired light theme: cool greys, blue links, system sans.", "light"),
    ("bamboo-dark", "Nord Night", "https://github.com/rilwis/bamboo", "MIT", "bamboo.css@1.4.0/dist/dark.min.css",
     "Nord dark palette: blue-grey background, pale text.", "dark"),
    ("marx", "Plain", "https://github.com/mblode/marx", "MIT", "marx-css@5.3.2/css/marx.min.css",
     "Classless reset+style: plain white, system sans, neutral, very utilitarian.", "light"),
]

EXTRA_HEAD = {
    # Pico's container has zero side padding at >=576px; with the side nav taking space, give it a gutter
    "pico": "<style>@media (min-width:1000px){body>main{max-width:900px;padding-left:2rem;padding-right:2rem}}</style>",
    "github-light": "<style>body.markdown-body{margin:0}body.markdown-body>main{box-sizing:border-box;max-width:980px;margin:0 auto;padding:45px}</style>",
    "github-dark": "<style>body.markdown-body{margin:0}body.markdown-body>main{box-sizing:border-box;max-width:980px;margin:0 auto;padding:45px}</style>",
}


def extract(src: str):
    head_style = re.search(r"<style(?: id=\"book-style\")?>(.*?)</style>", src, re.S).group(1)
    nav = re.search(r'<nav id="side">.*?</nav>', src, re.S).group(0)
    start = src.index(f'<section class="chapter" id="{CHAPTER}">')
    end = src.index("</section>", start)
    # the chapter may contain nested sections? check: take up to the next chapter/part section
    nxt = re.search(r'<section class="(chapter|part)"', src[start + 10:])
    end = start + 10 + nxt.start() if nxt else end
    chap = src[start:end].rstrip()
    if not chap.endswith("</section>"):
        chap += "</section>"
    return head_style, nav, chap


def fix_links(fragment: str, local_ids: set) -> str:
    def repl(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("#"):
            if url[1:] in local_ids:
                return m.group(0)
            return f'{attr}="../book/wc-book.html{url}"'
        if re.match(r"(https?:|mailto:|data:|\.\./)", url):
            return m.group(0)
        return f'{attr}="../book/{url}"'
    return re.sub(r'\b(href|src)="([^"]*)"', repl, fragment)


def page(key, name, mode, head_style, nav, chap, nthemes_note):
    local_ids = set(re.findall(r'\bid="([^"]+)"', chap))
    chap = fix_links(chap, local_ids)
    nav = fix_links(nav, local_ids)
    nav = nav.replace(f'href="#{CHAPTER}"', f'class="current" href="#{CHAPTER}"')
    note = (f'<div class="preview-note">Theme preview: <b>{html.escape(name)}</b><br>'
            f'<a href="index.html">&larr; back to the gallery</a></div>')
    nav = nav.replace('<div class="side-title">Wilson–Cowan</div>',
                      '<div class="side-title">Wilson–Cowan</div>' + note, 1)
    if key == "current":
        css = f"<style>{head_style}</style>\n<style>img.print{{display:none}}</style>"
    else:
        css = (f'<link rel="stylesheet" href="css/{key}.css">\n'
               f'<link rel="stylesheet" href="compat.css">')
        css += EXTRA_HEAD.get(key, "")
    body_cls = ' class="markdown-body"' if key.startswith("github") else ""
    html_cls = ' class="cx-dark"' if mode == "dark" else ""
    return f"""<!doctype html>
<html lang="en"{html_cls}><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} – Wilson–Cowan theme preview</title>
<link rel="stylesheet" href="../book/assets/katex/katex.min.css">
{css}
</head><body{body_cls}>
{nav}
<main>
{chap}
</main>
</body></html>
"""


def index_page():
    cards = []
    for key, name, repo, lic, pkg, look, mode in THEMES:
        modes = {"light": "Light only", "dark": "Dark only",
                 "auto": "Light; switches to dark with the OS setting"}[mode]
        repo_html = (f'<a href="{repo}">{html.escape(repo.replace("https://github.com/", ""))}</a>'
                     if repo else "—")
        cards.append(f"""<article class="card">
  <a class="shot" href="{key}.html"><img src="shots/{key}.png" alt="Screenshot of the {html.escape(name)} preview" loading="lazy"></a>
  <h2><a href="{key}.html">{html.escape(name)}</a></h2>
  <p class="look">{html.escape(look)}</p>
  <dl><dt>Repo</dt><dd>{repo_html}</dd><dt>Licence</dt><dd>{html.escape(lic)}</dd>
  <dt>Mode</dt><dd>{modes}</dd><dt>CSS</dt><dd><code>{html.escape(pkg)}</code></dd></dl>
  <a class="open" href="{key}.html">Open full preview &rarr;</a>
</article>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Theme Gallery</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--muted:#5d6670;--line:#d9dde3;--link:#1f5fbf}}
@media (prefers-color-scheme: dark){{:root{{--bg:#111418;--card:#1a1e24;--ink:#e6e9ed;--muted:#9aa3ad;--line:#2c323a;--link:#7fb0ff}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
header{{max-width:1200px;margin:0 auto;padding:28px 16px 8px}}
h1{{margin:0 0 6px;font-size:1.6rem}}
header p{{margin:4px 0;color:var(--muted);max-width:60rem}}
a{{color:var(--link)}}
.grid{{max-width:1200px;margin:0 auto;padding:16px;display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}}
.shot img{{display:block;width:100%;aspect-ratio:1280/900;object-fit:cover;object-position:top left;border-bottom:1px solid var(--line)}}
.card h2{{font-size:1.1rem;margin:12px 14px 4px}}
.card h2 a{{color:inherit;text-decoration:none}}
.look{{margin:0 14px 8px;color:var(--muted)}}
dl{{margin:0 14px 10px;display:grid;grid-template-columns:auto 1fr;gap:2px 10px;font-size:.85rem}}
dt{{color:var(--muted)}} dd{{margin:0;overflow-wrap:anywhere}}
code{{font-size:.8rem}}
.open{{margin:auto 14px 14px;font-weight:600}}
</style></head><body>
<header>
<h1>Theme gallery for the Wilson–Cowan book</h1>
<p>Each card shows Chapter 5 (“The E–I Phase Plane”) rendered with an open-source classless CSS theme from GitHub,
plus a small shared <code>compat.css</code> that only makes figures responsive, styles the note boxes from the theme's own colours,
and keeps the side navigation usable. The first card is the current book style, for comparison.
All files are local; theme CSS was downloaded once from jsDelivr (pinned versions) into <code>css/</code>.</p>
<p>Screenshots are taken in light mode at 1280×900. Themes marked “switches to dark” will turn dark if your OS is in dark mode.</p>
</header>
<main class="grid">
{chr(10).join(cards)}
</main>
</body></html>
"""


def main():
    src = BOOK.read_text(encoding="utf-8")
    head_style, nav, chap = extract(src)
    (OUT / "css").mkdir(parents=True, exist_ok=True)
    (OUT / "shots").mkdir(exist_ok=True)
    for key, name, repo, lic, pkg, look, mode in THEMES:
        (OUT / f"{key}.html").write_text(page(key, name, mode, head_style, nav, chap, ""), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(), encoding="utf-8")
    print(f"wrote {len(THEMES)} previews + index.html in {OUT}")
    if "--no-shots" in sys.argv:
        return
    for key, *_ in THEMES:
        shot = OUT / "shots" / f"{key}.png"
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-color-profile=srgb", "--virtual-time-budget=4000",
                        "--blink-settings=preferredColorScheme=1",
                        f"--screenshot={shot}", "--window-size=1280,900",
                        (OUT / f"{key}.html").as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("shot", shot.name)


if __name__ == "__main__":
    main()
