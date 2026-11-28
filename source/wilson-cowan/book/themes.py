"""NOT USED since 2026-11-27: the user chose the Isochrons-Notebook look (the book's own style and the
Display panel of the site), without a theme drop-down. Kept for reference.

Add a theme switcher to the built book (wc-book.html).

'Tufte' (light) is the default; the reader can switch to the book's own 'Classic' or any of the open-source
(MIT-licensed) stylesheets from GitHub projects, collected by scripts/wilson-cowan/build_theme_gallery.py
in rendered-anims/wilson-cowan/themes/. The choice is remembered in this browser (localStorage 'wc.theme').
Run after build.mjs:  .venv/bin/python scripts/wilson-cowan/book/themes.py"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "rendered-anims" / "wilson-cowan" / "book"
SRC = ROOT / "rendered-anims" / "wilson-cowan" / "themes"
DST = BOOK / "assets" / "themes"

# key (css file), short name, dark?, source project
DEFAULT = "tufte"
# Six stylesheets follow the computer's dark mode on their own (prefers-color-scheme); each becomes two
# fixed choices, light and dark (install_assets writes <key>.css without, <key>-dark.css with the dark rules)
SPLIT = {"tufte": "Tufte", "latex": "LaTeX", "pico": "Pico", "simple": "Simple", "newcss": "Fresh", "mvp": "Bold"}
THEMES = [
    ("tufte", "Tufte", False, "edwardtufte/tufte-css"),
    ("tufte-dark", "Tufte Dark", True, "edwardtufte/tufte-css"),
    ("classic", "Classic", False, "this book"),
    ("latex", "LaTeX", False, "vincentdoerig/latex-css"),
    ("latex-dark", "LaTeX Dark", True, "vincentdoerig/latex-css"),
    ("pico", "Pico", False, "picocss/pico"),
    ("pico-dark", "Pico Dark", True, "picocss/pico"),
    ("water-light", "Water", False, "kognise/water.css"),
    ("water-dark", "Ink", True, "kognise/water.css"),
    ("simple", "Simple", False, "kevquirk/simple.css"),
    ("simple-dark", "Simple Dark", True, "kevquirk/simple.css"),
    ("sakura", "Sakura", False, "oxalorg/sakura"),
    ("sakura-dark", "Dusk", True, "oxalorg/sakura"),
    ("sakura-earthly", "Moss", False, "oxalorg/sakura"),
    ("newcss", "Fresh", False, "xz/new.css"),
    ("newcss-dark", "Fresh Dark", True, "xz/new.css"),
    ("mvp", "Bold", False, "andybrewer/mvp"),
    ("mvp-dark", "Bold Dark", True, "andybrewer/mvp"),
    ("awsm", "Essay", False, "igoradamenko/awsm.css"),
    ("github-light", "GitHub", False, "sindresorhus/github-markdown-css"),
    ("github-dark", "GitHub Night", True, "sindresorhus/github-markdown-css"),
    ("bamboo", "Nord", False, "rilwis/bamboo"),
    ("bamboo-dark", "Nord Night", True, "rilwis/bamboo"),
    ("marx", "Plain", False, "mblode/marx"),
]
EXTRA = {
    "pico": "@media (min-width:1000px){body>main{max-width:900px;padding-left:2rem;padding-right:2rem}}",
    "pico-dark": "@media (min-width:1000px){body>main{max-width:900px;padding-left:2rem;padding-right:2rem}}",
    "github-light": "body.markdown-body{margin:0}body.markdown-body>main{box-sizing:border-box;max-width:980px;margin:0 auto;padding:45px}",
    "github-dark": "body.markdown-body{margin:0}body.markdown-body>main{box-sizing:border-box;max-width:980px;margin:0 auto;padding:45px}",
}

PICKER_CSS = """
#wc-theme{position:fixed;right:14px;bottom:14px;z-index:9999;font:13px/1.2 system-ui,sans-serif}
#wc-theme select{font:inherit;padding:6px 8px;border-radius:8px;border:1px solid rgba(127,127,127,.5);
  background:rgba(255,255,255,.92);color:#222;box-shadow:0 2px 8px rgba(0,0,0,.15);cursor:pointer}
html.cx-dark #wc-theme select{background:rgba(30,30,30,.92);color:#eee}
@media print{#wc-theme{display:none}}
"""

PICKER_JS = r"""
(function(){
  var T = __THEMES__, EXTRA = __EXTRA__, KEY = "wc.theme";
  var base = (document.currentScript && document.currentScript.getAttribute("data-base")) || "assets/themes/";
  function anchorEl(){            // the element at the top of the window, to keep the reading position
    if (location.hash && window.scrollY < 5) { var h = document.getElementById(location.hash.slice(1)); if (h) return h; }
    var e = document.elementFromPoint(Math.min(600, window.innerWidth - 20), 8);
    return (e && e !== document.body && e !== document.documentElement) ? e : null;
  }
  function restore(el){ if (el && el.scrollIntoView) el.scrollIntoView({block: "start"}); }
  function apply(k, first){
    var el = first ? (location.hash ? document.getElementById(location.hash.slice(1)) : null) : anchorEl();
    var own = document.getElementById("book-style");
    ["wc-ext","wc-compat","wc-extra"].forEach(function(id){var e=document.getElementById(id); if(e) e.remove();});
    document.documentElement.classList.remove("cx-dark");
    document.body.classList.remove("markdown-body"); document.body.classList.remove("latex-dark");
    var t = T.filter(function(x){return x[0]===k;})[0] || T.filter(function(x){return x[0]===__DEFAULT__;})[0];
    if (t[0] === "classic") { if (own) own.disabled = false; restore(el); return t[0]; }
    if (own) own.disabled = true;
    var l = document.createElement("link"); l.rel="stylesheet"; l.id="wc-ext"; l.href=base+t[0]+".css"; l.onload=function(){ setTimeout(function(){ restore(el); }, 30); }; document.head.appendChild(l);
    var c = document.createElement("link"); c.rel="stylesheet"; c.id="wc-compat"; c.href=base+"compat.css"; document.head.appendChild(c);
    if (EXTRA[t[0]]) { var s=document.createElement("style"); s.id="wc-extra"; s.textContent=EXTRA[t[0]]; document.head.appendChild(s); }
    if (t[2]) document.documentElement.classList.add("cx-dark");
    if (t[0].indexOf("github")===0) document.body.classList.add("markdown-body");
    if (t[0] === "latex-dark") document.body.classList.add("latex-dark");      // latex.css's own dark switch
    var R = document.documentElement;
    if (R.dataset.wcOrigTheme === undefined) R.dataset.wcOrigTheme = R.getAttribute("data-theme") || "";
    if (t[0] === "pico-dark") R.setAttribute("data-theme", "dark");               // pico.css's dark switch
    else if (R.dataset.wcOrigTheme) R.setAttribute("data-theme", R.dataset.wcOrigTheme); else R.removeAttribute("data-theme");
    if (t[0] === "mvp-dark") document.documentElement.setAttribute("color-mode", "user"); // mvp.css's dark switch
    else document.documentElement.removeAttribute("color-mode");
    return t[0];
  }
  var cur = __DEFAULT__; try { cur = localStorage.getItem(KEY) || __DEFAULT__; } catch(e) {}
  cur = apply(cur, true);
  var box = document.createElement("div"); box.id = "wc-theme";
  var sel = document.createElement("select"); sel.setAttribute("aria-label","Theme"); sel.title = "Theme (open-source stylesheets)";
  T.forEach(function(t){ var o=document.createElement("option"); o.value=t[0]; o.textContent="Theme: "+t[1]; if(t[0]===cur) o.selected=true; sel.appendChild(o); });
  sel.addEventListener("change", function(){ var k=apply(sel.value); try{localStorage.setItem(KEY,k);}catch(e){} });
  box.appendChild(sel); document.body.appendChild(box);
})();
"""


def dark_blocks(css):
    """the (start, open brace, end) of each @media block whose condition asks for prefers-color-scheme: dark"""
    out, i = [], 0
    while True:
        i = css.find("@media", i)
        if i < 0:
            return out
        b = css.find("{", i)
        cond = css[i:b]
        if "prefers-color-scheme" in cond and "dark" in cond:
            depth, j = 0, b
            while j < len(css):
                depth += css[j] == "{"
                depth -= css[j] == "}"
                if depth == 0:
                    break
                j += 1
            out.append((i, b, j))
            i = j + 1
        else:
            i = b + 1


def split_css(css):
    """(light, dark): the stylesheet without its dark-mode rules, and with them always on"""
    light, dark, k = [], [], 0
    for a, b, e in dark_blocks(css):
        light.append(css[k:a]); dark.append(css[k:a]); dark.append(css[b + 1:e]); k = e + 1
    light.append(css[k:]); dark.append(css[k:])
    return "".join(light), "".join(dark)


def install_assets():
    DST.mkdir(parents=True, exist_ok=True)
    for key, *_ in THEMES:
        if key == "classic" or (key.endswith("-dark") and key[:-5] in SPLIT):
            continue
        src = (SRC / "css" / f"{key}.css").read_text()
        if key in SPLIT:
            light, dark = split_css(src)
            if light == src:
                raise SystemExit(f"{key}: no dark-mode rules found to split")
            (DST / f"{key}.css").write_text(light)
            (DST / f"{key}-dark.css").write_text(dark)
        else:
            (DST / f"{key}.css").write_text(src)
    if (SRC / "css" / "et-book").is_dir():
        shutil.copytree(SRC / "css" / "et-book", DST / "et-book", dirs_exist_ok=True)
    shutil.copy2(SRC / "compat.css", DST / "compat.css")


def inject(html_path: Path, base: str = "assets/themes/"):
    s = html_path.read_text()
    s = re.sub(r'<script id="wc-theme-js".*?</script>\n?', "", s, flags=re.S)
    s = re.sub(r'<style id="wc-theme-css">.*?</style>\n?', "", s, flags=re.S)
    if 'id="book-style"' not in s:
        s = s.replace("<style>", '<style id="book-style">', 1)
    js = (PICKER_JS.replace("__THEMES__", json.dumps([list(t) for t in THEMES])).replace("__EXTRA__", json.dumps(EXTRA))
          .replace("__DEFAULT__", json.dumps(DEFAULT)))
    s = s.replace("</head>", f'<style id="wc-theme-css">{PICKER_CSS}</style>\n</head>', 1)
    i = s.rindex("</body>")
    s = s[:i] + f'<script id="wc-theme-js" data-base="{base}">{js}</script>\n' + s[i:]
    html_path.write_text(s)


if __name__ == "__main__":
    install_assets()
    inject(BOOK / "wc-book.html")
    print(f"theme switcher added: {len(THEMES)} themes, assets in {DST}")
