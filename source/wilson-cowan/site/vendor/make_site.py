"""
The project page (GitHub Pages) for ZetaOne/pyauto-xpp: site/ (index.html plus
icons, a web manifest and a gallery of tutorial figures).

Looks and behaves like its sister project XPPAUT-Web: the same themes
(src/style.css colours, src/main.ts names and swatches), the same toolbar,
theme menu, system fonts and phone layout.  The tutorial lists come from the
two tutorial READMEs, the gallery from the figures the tutorial scripts write
to figures/<script>/.  Called by make_release.py.
"""
import html
import json
import math
import re
import shutil
from pathlib import Path

REPO = "ZetaOne/pyauto-xpp"
WEB = Path(__file__).resolve().parent / "xpp-web-src"   # XPPAUT-Web src/ (style.css, main.ts), fetched from GitHub
FIGS = Path.home() / "Documents" / "XPPAUT-pkg-dev" / "py-tuts" / "figures"
GH = f"https://github.com/{REPO}"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
SISTER = "https://zetaone.github.io/XPPAUT-Web/"
BOOK = "https://zetaone.github.io/notebook/"   # notebook, the isochron book (built in ~/Documents/isochron-site)
BOOK_ICON = Path.home() / "Documents" / "isochron-site" / "site" / "icon-192.png"

# a few figures that the tutorial scripts make: (script, figure, title, caption)
GALLERY = [
    ("16_2D-FLOWS_morris-lecar-bifurcation", "ml-bifurcation.png", "Morris-Lecar in AUTO",
     "Equilibria in the applied current i (red stable, thin line unstable), the two Hopf points, "
     "and the periodic orbits between them (green stable, blue unstable)."),
    ("01_2D-FLOWS_fitzhugh-nagumo", "phase_plane.png", "FitzHugh-Nagumo phase plane",
     "Nullclines, direction field and trajectories that all end on the stable equilibrium."),
    ("37_DELAYS_mackey-glass-period-doubling", "orbit_diagram.png", "Mackey-Glass, a delay equation",
     "AUTO's periodic orbits and period doublings, drawn over the maxima of simulations: "
     "the route to chaos."),
    ("07_3D-FLOWS_lorenz", "attractor.png", "The Lorenz attractor",
     "r = 27, in 3-D and projected on (x, z), with the two unstable equilibria."),
    ("28_SPACE_fhn-chain-arrays", "space_time.png", "Waves along a chain",
     "A chain of 20 FitzHugh-Nagumo cells driven at one end: voltage against cell and time."),
    ("06_MAPS_henon-map", "attractor.png", "The Henon map",
     "Its strange attractor and the layers seen when zooming in near a fixed point."),
]


# ---- themes, as XPPAUT-Web defines them -------------------------------------
def theme_css():
    css = (WEB / "style.css").read_text()
    out = []
    i = css.index(":root {")
    out.append(css[i:css.index("}", i) + 1])
    m = re.search(r"@media \(prefers-color-scheme: dark\) \{.*?\n\}\n", css, re.S)
    out.append(m.group(0))
    for m in re.finditer(r"(/\*[^*]*\*/\s*)?:root\[data-theme='[^']+'\] \{.*?\n\}", css, re.S):
        out.append(m.group(0))
    return "\n".join(out)


def theme_list():
    """[{id, name, swatch}], 'system' first, exactly as XPPAUT-Web's menu"""
    ts = (WEB / "main.ts").read_text()
    return [{"id": a, "name": b, "swatch": re.findall(r"'(#[0-9a-fA-F]+)'", c)}
            for a, b, c in re.findall(r"\{ id: '([^']+)', name: '([^']+)', swatch: \[([^\]]*)\] \}", ts)]


# ---- tutorials --------------------------------------------------------------
def md_rows(text):
    """rows of the markdown tables, with the group (## heading) they are under"""
    group, rows = "", []
    for ln in text.splitlines():
        if ln.startswith("## "):
            group = ln[3:].strip()
        elif ln.startswith("|") and not re.match(r"\|\s*-", ln) and "script |" not in ln and "notebook |" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            rows.append((group, cells))
    return rows


def tutorials(out):
    items = []
    level, nbfile = "", ""
    for ln in (out / "tutorials" / "worked-examples" / "README.md").read_text().splitlines():
        m = re.match(r"## (Level \d+[^:]*?)(?::| \(|$).*?(?:\[`([^`]+\.ipynb)`\])?", ln)
        if ln.startswith("## Level"):
            level = re.split(r":|\[", ln[3:])[0].strip()
            f = re.findall(r"`([^`]+\.ipynb)`", ln)
            nbfile = f[0] if f else nbfile
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")] if ln.startswith("|") else []
        if len(c) >= 3 and c[0].isdigit():
            nb = nbfile
            if c[0].isdigit() and level.startswith("Level 6"):
                nb = "06a_delay-equations-simulation.ipynb" if int(c[0]) <= 31 else "06b_delay-equations-with-auto.ipynb"
            items.append(dict(kind="example", group=level, file=f"tutorials/worked-examples/{nb}",
                              title=c[1], what=c[2]))
    groups = {}            # notebooks: the level heading they are under
    g = "2D-FLOWS"
    for g_head, c in md_rows((out / "tutorials" / "notebooks" / "README.md").read_text()):
        if len(c) < 3:
            continue
        g = g_head or g
        name = re.search(r"\(([^)]+\.ipynb)\)", c[1]).group(1)
        items.append(dict(kind="notebook", group=g, file=f"tutorials/notebooks/{name}", title=c[2],
                          what="Interactive notebook: sliders, direction field, clickable phase plane, AUTO panel."))
    for i in items:
        assert (out / i["file"]).is_file(), i["file"]
    return items


# ---- the mark: a van der Pol relaxation cycle around its cubic nullcline -----
def _mark_paths():
    """polylines in a 64 x 64 box: (cubic nullcline, limit cycle around it)"""
    mu, x, y, dt = 1.3, 0.5, 0.0, 0.002
    f = lambda x, y: (mu * (x - x ** 3 / 3 - y), x / mu)
    pts = []
    for n in range(int(80 / dt)):
        k1 = f(x, y); k2 = f(x + dt / 2 * k1[0], y + dt / 2 * k1[1])
        k3 = f(x + dt / 2 * k2[0], y + dt / 2 * k2[1]); k4 = f(x + dt * k3[0], y + dt * k3[1])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        if n * dt > 50:
            pts.append((x, y))
    # one period, from an upward crossing of y = 0 to the next, about every 0.04 along the curve
    ups = [k for k in range(1, len(pts)) if pts[k - 1][1] < 0 <= pts[k][1]]
    cyc, last = [], None
    for p in pts[ups[0]:ups[1]]:
        if last is None or math.dist(p, last) > 0.05:
            cyc.append(p); last = p
    null = [(u, u - u ** 3 / 3) for u in [-2.25 + 4.5 * k / 60 for k in range(61)]]
    xs = [p[0] for p in cyc + null]; ys = [p[1] for p in cyc + null]
    sx, sy = 42 / (max(xs) - min(xs)), 40 / (max(ys) - min(ys))
    tf = lambda p: (32 + sx * p[0], 32 - sy * p[1])
    return [tf(p) for p in null], [tf(p) for p in cyc]


BG, NULL, CYC = "#1d3150", "#8fb8e6", "#ffb04a"


LOGO = Path(__file__).resolve().parent / "logo" / "pyauto-xpp-logo.svg"   # the chosen logo (see logo-drafts/)


def mark_svg():
    return LOGO.read_text()


def mark_png(path, size, maskable=False):
    """render the logo with Inkscape; maskable icons get a full-bleed background and a safe zone"""
    import subprocess, tempfile
    from PIL import Image
    inner = round(size * 0.78) if maskable else size
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "l.png"
        subprocess.run(["inkscape", str(LOGO), "-w", str(inner), "-h", str(inner), "-o", str(tmp)],
                       check=True, capture_output=True)
        img = Image.open(tmp).convert("RGBA")
        if maskable:
            out = Image.new("RGBA", (size, size), (0xdc, 0xe6, 0xf2, 255))
            out.alpha_composite(img, ((size - inner) // 2, (size - inner) // 2))
            img = out
        img.save(path)


def worked_notebook(n):
    """the worked-example notebook that holds model number n"""
    for hi, f in ((7, "01_first-steps"), (15, "02_bifurcations-with-auto"),
                  (19, "03_two-parameters-and-global-bifurcations"), (25, "04_forcing-tori-and-phase"),
                  (28, "05_noise-and-space"), (31, "06a_delay-equations-simulation"),
                  (39, "06b_delay-equations-with-auto"), (42, "07_maps-cobwebs-and-stable-manifolds")):
        if n <= hi:
            return f + ".ipynb"


# =============================================================================
# Display panel: theme, text size and font, shared by the main page and the manual
# -----------------------------------------------------------------------------
# The round button in the toolbar opens a "Display" panel with three groups.
# Choices are kept in localStorage ('pyauto-xpp-theme', 'pyauto-xpp-textsize',
# 'pyauto-xpp-font'), so both pages share them, and a small script in <head>
# applies them before the page is drawn (no flash):
#   <html data-theme=..>     XPPAUT-Web's colours (theme_css); none = System
#   <html data-textsize=..>  the root font size (90 / 100 / 112 / 125 %); all
#                            font sizes on both pages are in rem, so they follow it
#   <html data-font=..>      the body font (--font-body); code stays monospace
#   <html data-code=..>      'dark' or 'light': the colour scheme of the theme,
#                            used by the manual's code colours (VS Code Dark+/Light+)
# For checking, ?theme=..&textsize=..&font=.. in the address applies a choice
# to that one visit without saving it.
# Pieces: display_head() (the <head> script), TOOLBAR_CSS (the toolbar and its
# menus), DISPLAY_CSS, DISPLAY_BUTTON (the button and empty panel) and
# DISPLAY_JS (fills the panel, applies and saves the choices, menu keys).
# =============================================================================
TEXT_SIZES = ["90", "100", "112", "125"]
_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
# id, label in the panel, CSS font stack, Google Fonts family (None: nothing to download)
FONTS = [
    ("system", "System (default)", _SANS, None),
    ("serif", "Serif (Charter, Georgia)", "Charter, 'Bitstream Charter', 'Sitka Text', Cambria, Georgia, serif", None),
    ("atkinson", "Atkinson Hyperlegible", "'Atkinson Hyperlegible', " + _SANS,
     "Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400;1,700"),
    ("lexend", "Lexend", "'Lexend', " + _SANS, "Lexend:wght@400;500;600;700"),
]


def theme_dark():
    """{theme id: True if its colour scheme is dark}; 'system' follows the computer (None)"""
    css = theme_css()
    dark = {}
    for t in theme_list():
        m = re.search(r":root\[data-theme='%s'\] \{[^}]*?color-scheme: (\w+)" % re.escape(t["id"]), css)
        dark[t["id"]] = None if t["id"] == "system" else bool(m and m.group(1) == "dark")
    return dark


def display_head():
    """the <head> script: applies the saved theme, text size and font before the first paint,
    loads a web font only when one is chosen, and enables the matching code-colour stylesheet
    (<link data-code=dark|light>, the manual only)"""
    fonts = {f: (f"https://fonts.googleapis.com/css2?family={g}&display=swap" if g else "")
             for f, _, _, g in FONTS}
    return """<script>
  // apply the saved display choices before the page is drawn (no flash of the wrong colours or size);
  // new visitors get Funky 2 (Night Owl), 100 % text and the system font
  (function () {
    var d = document.documentElement, q = {}, DARK = __DARK__, FONTS = __FONTURLS__, SIZES = __SIZES__;
    function get(k) { try { return localStorage.getItem(k) } catch (e) { return null } }
    try { new URLSearchParams(location.search).forEach(function (v, k) { q[k] = v }) } catch (e) {}
    var t = q.theme || get('pyauto-xpp-theme') || 'funky2'; if (!(t in DARK)) t = 'funky2';
    var z = q.textsize || get('pyauto-xpp-textsize') || '100'; if (SIZES.indexOf(z) < 0) z = '100';
    var f = q.font || get('pyauto-xpp-font') || 'system'; if (!(f in FONTS)) f = 'system';
    if (t !== 'system') d.dataset.theme = t;
    d.dataset.textsize = z; d.dataset.font = f;
    var dark = t === 'system' ? matchMedia('(prefers-color-scheme: dark)').matches : DARK[t];
    d.dataset.code = dark ? 'dark' : 'light';
    var ls = document.querySelectorAll('link[data-code]');
    for (var i = 0; i < ls.length; i++) ls[i].media = ls[i].dataset.code === d.dataset.code ? 'all' : 'not all';
    if (FONTS[f]) {
      var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = FONTS[f]; l.id = 'webfont-' + f;
      document.head.appendChild(l);
    }
    window.PYX_DISPLAY = { theme: t, size: z, font: f, DARK: DARK, FONTS: FONTS, SIZES: SIZES };
  })();
</script>""".replace("__DARK__", json.dumps(theme_dark())).replace("__FONTURLS__", json.dumps(fonts)) \
        .replace("__SIZES__", json.dumps(TEXT_SIZES))


# the toolbar (XPPAUT-Web's .bar) and its drop-down menus, used by both pages
TOOLBAR_CSS = r"""
/* ---- toolbar and menus (shared by the main page and the manual) ------------- */
* { box-sizing: border-box }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }
.skip { position: absolute; left: -999px; top: 8px; z-index: 40; padding: 8px 12px; background: var(--bar); color: var(--fg); border: 1px solid var(--line); border-radius: 4px }
.skip:focus { left: 8px }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap }
.bar { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; gap: 16px; padding: 6px 12px;
       min-height: 48px; background: var(--bar); border-bottom: 1px solid var(--line); font-size: .875rem }
/* funky themes: a multi-coloured stripe under the toolbar (as XPPAUT-Web) */
:root[data-theme^='funky'] .bar { border-bottom: 3px solid transparent; border-image: var(--stripe) 1 }
.brand { display: inline-flex; align-items: center; gap: 6px; min-height: 40px; font-weight: 600; color: var(--fg); text-decoration: none; white-space: nowrap }
.brand img { width: 22px; height: 22px; border-radius: 5px; flex: none }
.right { margin-left: auto; display: flex; align-items: center; gap: 10px }
.bar details { position: relative }
.bar summary { list-style: none } .bar summary::-webkit-details-marker { display: none }
.round { display: grid; place-items: center; width: 32px; height: 32px; padding: 0; border: 1px solid var(--line); flex: none;
       border-radius: 50%; background: var(--bg); color: var(--fg); cursor: pointer }
.round:hover, details[open] > summary.round { background: var(--panel-bar-active) }
.panel { position: absolute; z-index: 100; top: calc(100% + 6px); right: 0; display: grid; gap: 2px; min-width: 220px;
       max-height: calc(100vh - 70px); overflow: auto; padding: 6px; background: var(--bar); border: 1px solid var(--line);
       border-radius: 6px; box-shadow: 0 6px 20px rgb(0 0 0 / 0.25) }
.panel button, .panel a { display: flex; align-items: center; gap: 10px; width: 100%; padding: 6px 8px; border: 0; border-radius: 4px;
       background: transparent; color: var(--fg); font: inherit; text-align: left; text-decoration: none; cursor: pointer }
.panel button:hover, .panel a:hover, .panel button[aria-checked='true'] { background: var(--panel-bar-active) }
.panel .head { padding: 4px 8px 2px; font-size: .75rem; color: var(--muted) }
.swatch { display: inline-flex; width: 34px; height: 18px; overflow: hidden; border: 1px solid rgb(127 127 127 / 0.5); border-radius: 3px; flex: none }
.swatch i { flex: 1 }
@media (pointer: coarse) {
  .panel button, .panel a { min-height: 44px }
  .round { width: 40px; height: 40px }
}
"""

DISPLAY_CSS = r"""
/* ---- display: text size and font (see DISPLAY_* in make_site.py) ------------ */
/* XPPAUT-Web's theme sets 14px on :root; here 1rem is the reader's text size */
:root { font-size: 100%; --font-mono: ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
        --font-body: __SANS__ }
:root[data-textsize='90'] { font-size: 90% }
:root[data-textsize='112'] { font-size: 112% }
:root[data-textsize='125'] { font-size: 125% }
__FONTVARS__
body { font-family: var(--font-body) }
code, pre, kbd, samp { font-family: var(--font-mono) }
/* the panel */
.dpanel { width: min(300px, calc(100vw - 24px)); gap: 0 }
.dpanel .head { padding: 8px 8px 4px; font-weight: 600 }
.dpanel .head:first-child { padding-top: 2px }
.dpanel .grp { display: grid; gap: 2px }
.dpanel .sep { height: 1px; margin: 6px 2px 0; background: var(--line) }
.dpanel .seg { grid-template-columns: repeat(4, 1fr); gap: 4px; padding: 0 2px }
.dpanel .seg button { flex-direction: column; justify-content: center; gap: 0; padding: 4px 0; border: 1px solid var(--line); text-align: center }
.dpanel .seg button[aria-checked='true'] { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent) }
.dpanel .seg b { line-height: 1.15 }
.dpanel .seg small { font-size: .6875rem; color: var(--muted) }
.dpanel .fontlist button[aria-checked='true'], .dpanel .themelist button[aria-checked='true'] { box-shadow: inset 3px 0 0 var(--accent) }
.dpanel .fontlist span { flex: 1 }
.dpanel .fontlist small { color: var(--muted); font-size: .75rem; font-family: var(--font-body) }
""".replace("__SANS__", _SANS).replace("__FONTVARS__", "\n".join(
    f":root[data-font='{f}'] {{ --font-body: {stack} }}" for f, _, stack, _ in FONTS if f != "system"))

# the toolbar button and its panel (DISPLAY_JS fills the three groups)
DISPLAY_BUTTON = """<details class="display" id="themes">
      <summary class="round" title="Display: theme, text size, font" aria-label="Display: theme, text size and font">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none"
          stroke="currentColor" stroke-width="2"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>
      </summary>
      <div class="panel dpanel" id="displaypanel" role="group" aria-label="Display">
        <div class="head" id="dh-size">Text size</div>
        <div class="grp seg" id="sizelist" role="radiogroup" aria-labelledby="dh-size"></div>
        <div class="sep"></div>
        <div class="head" id="dh-font">Font</div>
        <div class="grp fontlist" id="fontlist" role="radiogroup" aria-labelledby="dh-font"></div>
        <div class="sep"></div>
        <div class="head" id="dh-theme">Theme (as XPPAUT-Web)</div>
        <div class="grp themelist" id="themelist" role="radiogroup" aria-labelledby="dh-theme"></div>
      </div>
    </details>"""


def display_js():
    """fills the Display panel, applies and saves the choices; Esc / a click elsewhere closes
    the toolbar menus, arrow keys move inside them.  After every change it fires the
    document event 'pyx-display' (the pages re-measure their layout on it)."""
    return r"""
(function () {
  const D = window.PYX_DISPLAY, root = document.documentElement, $ = id => document.getElementById(id);
  const THEMES = __THEMELIST__, FONTS = __FONTLIST__;
  const store = {
    get(k) { try { return localStorage.getItem(k) } catch (e) { return null } },
    set(k, v) { try { localStorage.setItem(k, v) } catch (e) {} },
  };
  const changed = () => document.dispatchEvent(new CustomEvent('pyx-display'));
  const check = (box, key, v) => { for (const b of box.querySelectorAll('button')) b.setAttribute('aria-checked', String(b.dataset[key] === v)) };
  // the code colours follow the theme: VS Code Dark+ on dark themes, Light+ on light ones
  function setCode(scheme) {
    const dark = D.theme === 'system' ? matchMedia('(prefers-color-scheme: dark)').matches : D.DARK[D.theme];
    root.dataset.code = scheme || (dark ? 'dark' : 'light');
    for (const l of document.querySelectorAll('link[data-code]')) l.media = l.dataset.code === root.dataset.code ? 'all' : 'not all';
  }
  function applyTheme(id) {
    D.theme = id;
    if (id === 'system') delete root.dataset.theme; else root.dataset.theme = id;
    check($('themelist'), 'theme', id);
    setCode();
    // the phone's status bar takes the toolbar's colour
    const bar = getComputedStyle(root).getPropertyValue('--bar').trim(), meta = document.querySelector('meta[name="theme-color"]');
    if (bar && meta) meta.setAttribute('content', bar);
    changed();
  }
  function applySize(z) { D.size = z; root.dataset.textsize = z; check($('sizelist'), 'size', z); changed() }
  function applyFont(f) {
    D.font = f; root.dataset.font = f; check($('fontlist'), 'font', f);
    // a web font is downloaded only when it is chosen
    if (D.FONTS[f] && !$('webfont-' + f)) {
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = D.FONTS[f]; l.id = 'webfont-' + f;
      l.onload = changed; document.head.append(l);
    }
    if (document.fonts) document.fonts.ready.then(changed);
    changed();
  }
  window.pyxSetCode = setCode;
  const button = (box, attrs, html, onclick) => {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'radio');
    for (const k in attrs) b.dataset[k] = attrs[k];
    b.innerHTML = html; b.addEventListener('click', onclick); box.append(b); return b;
  };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  for (const z of D.SIZES) {
    const b = button($('sizelist'), { size: z }, '<b style="font-size:' + (0.95 * z / 100) + 'rem">A</b><small>' + z + '%</small>',
      () => { applySize(z); store.set('pyauto-xpp-textsize', z) });
    b.setAttribute('aria-label', 'Text size ' + z + '%');
  }
  for (const [id, name, stack] of FONTS)
    button($('fontlist'), { font: id }, '<span style="font-family:' + esc(stack) + '">' + esc(name) + '</span>' +
      (D.FONTS[id] ? '<small>web font</small>' : ''), () => { applyFont(id); store.set('pyauto-xpp-font', id) });
  for (const t of THEMES)
    button($('themelist'), { theme: t.id }, '<span class="swatch">' + t.swatch.map(c => '<i style="background:' + c + '"></i>').join('') +
      '</span>' + esc(t.name), () => { applyTheme(t.id); store.set('pyauto-xpp-theme', t.id); closeMenus(true) });
  applyTheme(D.theme); applySize(D.size); applyFont(D.font);
  matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => applyTheme(D.theme));
  // printing: light code colours on white paper
  addEventListener('beforeprint', () => setCode('light'));
  addEventListener('afterprint', () => setCode());

  // ---- toolbar menus: Esc or a click elsewhere closes them; arrows move inside --
  const menus = () => [...document.querySelectorAll('header details')];
  function closeMenus(refocus) {
    for (const d of menus()) if (d.open) { d.open = false; if (refocus) d.querySelector('summary').focus() }
  }
  for (const d of menus()) {
    d.addEventListener('toggle', () => {
      if (!d.open) return;
      for (const o of menus()) if (o !== d) o.open = false;
      const items = [...d.querySelectorAll('.panel button, .panel a')];
      (items.find(b => b.getAttribute('aria-checked') === 'true') || items[0])?.focus();
    });
    d.addEventListener('keydown', e => {
      const items = [...d.querySelectorAll('.panel button, .panel a')], i = items.indexOf(document.activeElement);
      if (!d.open || i < 0) return;
      const go = { ArrowDown: i + 1, ArrowUp: i - 1, Home: 0, End: items.length - 1 }[e.key];
      if (go === undefined) return;
      e.preventDefault(); items[(go + items.length) % items.length].focus();
    });
  }
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menus().some(d => d.open)) { e.preventDefault(); closeMenus(true) } });
  document.addEventListener('pointerdown', e => { for (const d of menus()) if (d.open && !d.contains(e.target)) d.open = false });
})();
""".replace("__THEMELIST__", json.dumps(theme_list())).replace(
        "__FONTLIST__", json.dumps([[f, n, s] for f, n, s, _ in FONTS]))


# =============================================================================
# The manual: site/manual/index.html from docs/usage/USAGE.mdx (pandoc)
# -----------------------------------------------------------------------------
# Pandoc writes plain <pre class="LANG"><code> blocks (--no-highlight); _code_blocks()
# turns them into Prism blocks (python, bash; output blocks plain, XPP .ode text
# with a small grammar defined in MANUAL_JS) with a header and a copy button.
# The page has a contents sidebar (scroll-spy, collapsible, filter with "/"; a
# drawer on phones), heading links, a reading-progress bar, "back to top", and
# a print stylesheet.  Display panel as on the main page.  Prism and its
# VS Code colours (prism-themes) come from cdnjs, pinned, with SRI hashes.
# =============================================================================
MANUAL_SRC = Path(__file__).resolve().parent.parent / "pyauto-xpp" / "docs" / "usage"
CDN = "https://cdnjs.cloudflare.com/ajax/libs/"
PRISM_CSS = {   # data-code scheme: (file, SRI)
    "dark": ("prism-themes/1.9.0/prism-vsc-dark-plus.min.css",
             "sha512-ML8rkwYTFNcblPFx+VLgFIT2boa6f8DDP6p6go4+FT0/mJ8DCbCgi6S0UdjtzB3hKCr1zhU+YVB0AHhIloZP8Q=="),
    "light": ("prism-themes/1.9.0/prism-vs.min.css",
              "sha512-Jn4HzkCnzA7Bc+lbSQHAMeen0EhSTy71o9yJbXZtQx9VvozKVBV/2zfR3VyuDFIxGvHgbOMMNvb80l+jxFBC1Q=="),
}
PRISM_JS = [
    ("prism/1.29.0/prism.min.js",
     "sha512-7Z9J3l1+EYfeaPKcGXu3MS/7T+w19WtKQY/n+xzmw4hZhJ9tyYmcUS+4QqAlzhicE5LAfMQSF3iFTK9bQdTxXg=="),
    ("prism/1.29.0/components/prism-python.min.js",
     "sha512-AKaNmg8COK0zEbjTdMHJAPJ0z6VeNqvRvH4/d5M4sHJbQQUToMBtodq4HaV4fa+WV2UTfoperElm66c9/8cKmQ=="),
    ("prism/1.29.0/components/prism-bash.min.js",
     "sha512-whYhDwtTmlC/NpZlCr6PSsAaLOrfjVg/iXAnC4H/dtiHawpShhT2SlIMbpIhT/IL/NrpdMm+Hq2C13+VKpHTYw=="),
]
# fenced-block language -> (Prism language, label in the block's header)
CODE_LANGS = {"python": ("python", "Python"), "py": ("python", "Python"), "bash": ("bash", "Shell"),
              "sh": ("bash", "Shell"), "shell": ("bash", "Shell"), "console": ("bash", "Shell"),
              "ode": ("ode", "XPP .ode"), "text": ("none", "Output"), "": ("none", "Text")}
ICON_COPY = ('<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2" '
             'fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" '
             'fill="none" stroke="currentColor" stroke-width="2"/></svg>')
ICON_MENU = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" '
             'stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
ICON_CHEVRON = ('<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" '
                'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _is_ode(text):
    """an output block that is an XPP .ode file (e.g. what ModelBuilder.render() printed)"""
    lines = text.splitlines()
    keys = sum(bool(re.match(r"\s*(par|param|p|init|i|aux|number|num|@|wiener|table|set|global|bdry|markov)\b|\s*@", ln))
               for ln in lines)
    eqs = any(re.match(r"\s*(\w+'|d\w+/dt)\s*=", ln) for ln in lines)
    return eqs and (keys >= 2 or any(ln.strip() == "done" for ln in lines))


def _code_blocks(body):
    """pandoc's <pre class="LANG"><code> -> a Prism block with a header (language, copy button)"""
    def one(m):
        lang, code = (m.group(1) or "").lower(), m.group(2)
        prism, label = CODE_LANGS.get(lang, ("none", lang or "Text"))
        if prism == "none" and _is_ode(html.unescape(code)):
            prism, label = "ode", "XPP .ode"
        kind = "out" if label == "Output" else "code"
        return (f'<div class="cb cb-{kind}"><div class="cb-head"><span class="cb-lang">{label}</span>'
                f'<button type="button" class="cb-copy" aria-label="Copy {label.lower()} to the clipboard">'
                f'{ICON_COPY}<span class="cb-msg">Copy</span></button></div>'
                f'<pre class="language-{prism}" tabindex="0"><code class="language-{prism}">{code}</code></pre></div>')
    return re.sub(r'<pre(?: class="([\w+-]+)")?><code>(.*?)</code></pre>', one, body, flags=re.S)


def _topic_ids(body):
    """the guide has no h3s: its sections are made of paragraphs that start with a bold topic
    (**Load a model.** ...).  They get an id (topic-...) and appear in the sidebar under their section."""
    seen = set()

    def one(m):
        slug = "topic-" + (re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).lower()).strip("-") or "x")
        k, n = slug, 2
        while k in seen:
            k, n = f"{slug}-{n}", n + 1
        seen.add(k)
        return f'<p class="topic" id="{k}"><strong>{m.group(1)}</strong>'
    return re.sub(r"<p><strong>(.*?)</strong>", one, body)


def _manual_toc(body):
    """the sidebar: every h2 (except the page's own Contents list) with its h3s and bold topics, as nested lists"""
    groups = []
    for lvl, hid, inner in re.findall(r'<(?:h([23])|p class="topic") id="([^"]+)">(?:<strong>)?(.*?)</(?:h[23]|strong)>', body, re.S):
        if hid == "contents":
            continue
        label = re.sub(r"<(?!/?code\b)[^>]*>", "", inner).strip().rstrip(".:")
        if lvl == "2":
            groups.append((hid, label, []))
        elif groups:
            groups[-1][2].append((hid, label))
    out = []
    for hid, label, kids in groups:
        plain = html.escape(re.sub(r"<[^>]+>", "", html.unescape(label)), quote=True)
        if kids:
            sub = "".join(f'<li class="l3"><a href="#{k}">{lab}</a></li>' for k, lab in kids)
            out.append(f'<li class="l2"><div class="row"><button type="button" class="tg" aria-expanded="false" '
                       f'aria-label="Subsections of {plain}">{ICON_CHEVRON}</button><a href="#{hid}">{label}</a></div>'
                       f'<ul>{sub}</ul></li>')
        else:
            out.append(f'<li class="l2"><div class="row"><span class="tg-sp"></span><a href="#{hid}">{label}</a></div></li>')
    return "<ul>" + "".join(out) + "</ul>"


def _manual_body(body):
    """code blocks, heading links, scrollable tables, lazy images"""
    body = _code_blocks(body)
    body = re.sub(r'<(h[234]) id="([^"]+)">(.*?)</\1>',
                  lambda m: f'<{m.group(1)} id="{m.group(2)}">{m.group(3)}<a class="anchor" href="#{m.group(2)}" '
                            f'aria-label="Link to this section (copies the address)" title="Copy the link to this section">#</a></{m.group(1)}>',
                  body, flags=re.S)
    body = re.sub(r"<table>(.*?)</table>",
                  r'<div class="table-wrap" tabindex="0" role="region" aria-label="Table"><table>\1</table></div>', body, flags=re.S)
    body = body.replace("<img ", '<img loading="lazy" decoding="async" ')
    return body


MANUAL_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>pyauto-xpp manual</title>
<meta name="description" content="The pyauto-xpp manual: every part of the package with an example that has been run.">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="../icon.svg" type="image/svg+xml">
__PRISM_CSS__
__DISPLAY_HEAD__
<style>
__THEMES__
__TOOLBAR_CSS__
__DISPLAY_CSS__
__MANUAL_CSS__
</style>
</head>
<body>
<div class="progress" aria-hidden="true"><i id="progress"></i></div>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <button type="button" class="round tocbtn" id="tocbtn" aria-controls="toc" aria-expanded="false" title="Contents" aria-label="Contents">__ICON_MENU__</button>
  <a class="brand" href="../" title="The pyauto-xpp main page"><img src="../icon.svg" alt="" width="22" height="22">pyauto-xpp</a>
  <span class="crumb">Manual</span>
  <nav class="mnav" aria-label="Site">
    <a href="../">Main page</a><a class="more" href="../#install">Install</a><a class="more" href="../#tutorials">Tutorials</a><a href="__GH__">GitHub</a>
  </nav>
  <div class="right">
    __DISPLAY_BUTTON__
  </div>
</header>
<div class="layout">
  <aside class="toc" id="toc" aria-label="Contents">
    <div class="toc-head">
      <label class="tsearch"><span class="vh">Filter the sections</span>
        <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <input type="search" id="tocq" placeholder="Filter sections" autocomplete="off" aria-keyshortcuts="/" aria-controls="tocnav">
        <kbd aria-hidden="true">/</kbd></label>
      <button type="button" class="round tocclose" id="tocclose" aria-label="Close the contents">&#215;</button>
    </div>
    <nav class="toc-nav" id="tocnav" aria-label="Sections">
      <a class="toc-home" href="../">&#8592; pyauto-xpp main page</a>
      __TOC__
      <p class="toc-empty" id="tocempty" hidden>No section matches.</p>
    </nav>
  </aside>
  <div class="scrim" id="scrim" hidden></div>
  <main id="main" class="doc" tabindex="-1">
__BODY__
  </main>
</div>
<button type="button" class="totop" id="totop" aria-label="Back to top" title="Back to top">
  <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
</button>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>window.Prism = { manual: true };</script>
__PRISM_JS__
<script>
__DISPLAY_JS__
</script>
<script>
__MANUAL_JS__
</script>
</body>
</html>
"""

MANUAL_CSS = r"""
/* ---- the manual ------------------------------------------------------------------ */
html { scroll-padding-top: calc(var(--barh, 49px) + 14px); -webkit-text-size-adjust: 100% }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth } }
body { margin: 0; background: var(--bg); color: var(--fg); font-size: 1rem; line-height: 1.65; overflow-x: clip }
a { color: var(--accent) }
.bar { z-index: 20 }
.crumb { color: var(--muted); white-space: nowrap; margin-left: -8px }
.mnav { display: flex; align-items: center; gap: 2px; margin-left: 8px; min-width: 0; overflow: hidden }
.mnav a { color: var(--fg); text-decoration: none; padding: 5px 9px; border-radius: 4px; white-space: nowrap }
.mnav a:hover { background: var(--panel-bar-active) }
.tocbtn, .tocclose { display: none }
.progress { position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 30; pointer-events: none }
.progress i { display: block; height: 100%; background: var(--accent); transform-origin: 0 50%; transform: scaleX(0) }

/* sidebar */
.layout { display: grid; grid-template-columns: 290px minmax(0, 1fr); max-width: 1440px; margin: 0 auto }
.toc { position: sticky; top: var(--barh, 49px); align-self: start; height: calc(100vh - var(--barh, 49px));
       display: flex; flex-direction: column; border-right: 1px solid var(--line); background: var(--bg); font-size: .875rem }
.toc-head { display: flex; gap: 6px; align-items: center; padding: 12px 12px 8px }
.tsearch { position: relative; flex: 1; display: block }
.tsearch svg { position: absolute; left: 9px; top: 50%; transform: translateY(-50%); color: var(--muted) }
.tsearch input { width: 100%; min-height: 34px; padding: 5px 30px 5px 30px; border: 1px solid var(--line); border-radius: 6px;
       background: var(--bar); color: var(--fg); font: inherit }
.tsearch kbd { position: absolute; right: 7px; top: 50%; transform: translateY(-50%); padding: 0 5px; border: 1px solid var(--line);
       border-radius: 4px; color: var(--muted); font-size: .75rem; line-height: 1.4; pointer-events: none }
.tsearch input:focus + kbd, .tsearch input:not(:placeholder-shown) + kbd { display: none }
.toc-nav { flex: 1; overflow-y: auto; overscroll-behavior: contain; padding: 0 8px 28px }
.toc-home { display: block; padding: 4px 8px 8px; color: var(--muted); text-decoration: none }
.toc-home:hover { color: var(--accent) }
.toc ul { list-style: none; margin: 0; padding: 0 }
.toc .row { display: flex; align-items: flex-start; gap: 2px }
.toc-nav ul a { display: block; flex: 1; min-width: 0; padding: 4px 8px; border-radius: 5px; color: var(--fg); text-decoration: none; line-height: 1.35 }
.toc ul ul { margin: 0 0 4px 22px; padding-left: 6px; border-left: 1px solid var(--line) }
.toc ul ul a { color: var(--muted); font-size: .8125rem }
.toc-nav ul a:hover { background: var(--panel-bar-active); color: var(--fg) }
.toc-nav ul a.active { color: var(--accent); font-weight: 600; background: color-mix(in srgb, var(--accent) 14%, transparent) }
.toc-nav code { font-size: .92em }
.doc p.topic { margin-top: 1.4em }
.toc .tg, .toc .tg-sp { flex: none; width: 22px; height: calc(1.35em + 8px) }   /* one line of its link */
.toc .tg { display: grid; place-items: center; padding: 0; border: 0; border-radius: 4px; background: none; color: var(--muted); cursor: pointer }
.toc .tg:hover { background: var(--panel-bar-active); color: var(--fg) }
.toc .tg svg { transition: transform .15s }
.toc li.open > .row .tg svg { transform: rotate(90deg) }
.toc li.l2:not(.open) > ul { display: none }
.toc-nav.filtering li.l2 > ul { display: block }
.toc-nav.filtering .tg svg { transform: rotate(90deg) }
.toc-empty { padding: 4px 8px; color: var(--muted) }

/* the text: prose at a comfortable line length, code and tables may be wider */
.doc { min-width: 0; max-width: 980px; padding: 20px clamp(16px, 4vw, 48px) 96px; outline: none }
.doc p, .doc ul, .doc ol, .doc dl, .doc blockquote, .doc h1, .doc h2, .doc h3, .doc h4 { max-width: 75ch }
.doc h1 { font-size: 2rem; line-height: 1.2; margin: .4em 0 .5em }
.doc h2 { font-size: 1.5rem; line-height: 1.25; margin: 2.2em 0 .6em; padding-top: .7em; border-top: 1px solid var(--line); max-width: none }
.doc h3 { font-size: 1.2rem; line-height: 1.3; margin: 1.8em 0 .5em }
.doc h4 { font-size: 1.05rem; margin: 1.5em 0 .4em }
.doc ul, .doc ol { padding-left: 1.7em }
.doc ol { padding-left: 2.3em }
.doc li + li { margin-top: .2em }
.anchor { margin-left: .4em; padding: 0 .2em; color: var(--muted); text-decoration: none; font-weight: 400; opacity: 0; transition: opacity .15s }
.doc :is(h2, h3, h4):hover .anchor, .anchor:focus-visible { opacity: 1 }
@media (hover: none) { .anchor { opacity: .45 } }
.doc :not(pre) > code { padding: .1em .35em; border-radius: 5px; background: var(--panel-bar); font-size: .875em; overflow-wrap: anywhere }
.doc blockquote { margin: 1em 0; padding: 8px 14px; border-left: 3px solid var(--accent); background: var(--panel-bar); border-radius: 0 6px 6px 0 }
.doc img { max-width: 100%; height: auto; border-radius: 8px; background: #fff; vertical-align: middle }
.doc p > img:only-child { display: block; margin: 0 auto }
.doc hr { border: 0; border-top: 1px solid var(--line); margin: 2em 0 }

/* code blocks: colours as VS Code (Dark+ / Light+), a header with the language and a copy button */
:root[data-code='dark'] { --cb-bg: #1e1e1e; --cb-out: #181818; --cb-head: #252526; --cb-headfg: #c5c5c5; --cb-line: #3c3c3c; --cb-fg: #d4d4d4; --cb-ok: #4ec98a }
:root[data-code='light'] { --cb-bg: #ffffff; --cb-out: #f7f7f7; --cb-head: #f3f3f3; --cb-headfg: #5c5c5c; --cb-line: #dcdcdc; --cb-fg: #1f1f1f; --cb-ok: #1a7f37 }
.cb { margin: 1em 0 1.3em; border: 1px solid var(--cb-line); border-radius: 8px; overflow: hidden; background: var(--cb-bg) }
.cb-out { background: var(--cb-out) }
.cb + .cb-out { margin-top: -.7em }
.cb-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 30px; padding: 0 4px 0 12px;
       background: var(--cb-head); color: var(--cb-headfg); border-bottom: 1px solid var(--cb-line); font-size: .75rem; letter-spacing: .02em }
.cb-out .cb-head { background: transparent }
.cb-copy { display: inline-flex; align-items: center; gap: 5px; min-height: 26px; padding: 2px 8px; border: 1px solid transparent;
       border-radius: 5px; background: transparent; color: inherit; font: inherit; cursor: pointer }
.cb-copy:hover, .cb-copy:focus-visible { background: rgb(127 127 127 / .2); color: var(--cb-fg) }
.cb-copy.ok { color: var(--cb-ok) }
.doc pre[class*='language-'] { margin: 0; padding: 12px 16px; border: 0; border-radius: 0; background: transparent; color: var(--cb-fg);
       font-family: var(--font-mono); font-size: .84375rem; line-height: 1.55; overflow: auto; white-space: pre; tab-size: 4; text-shadow: none }
.doc code[class*='language-'] { font-family: var(--font-mono); font-size: inherit; line-height: inherit; background: none; color: inherit;
       white-space: pre; text-shadow: none; padding: 0; border: 0 }
.doc pre[class*='language-']:focus-visible { outline-offset: -2px }
/* VS Code Light+ colours on top of prism-vs */
:root[data-code='light'] .token.comment, :root[data-code='light'] .token.prolog { color: #008000; font-style: normal }
:root[data-code='light'] .token.string, :root[data-code='light'] .token.triple-quoted-string, :root[data-code='light'] .token.char { color: #a31515 }
:root[data-code='light'] .token.number { color: #098658 }
:root[data-code='light'] .token.keyword, :root[data-code='light'] .token.boolean { color: #0000ff }
:root[data-code='light'] .token.function, :root[data-code='light'] .token.decorator { color: #795e26 }
:root[data-code='light'] .token.builtin, :root[data-code='light'] .token.class-name { color: #267f99 }
:root[data-code='light'] .token.property, :root[data-code='light'] .token.variable, :root[data-code='light'] .token.parameter { color: #001080 }
:root[data-code='light'] .token.operator, :root[data-code='light'] .token.punctuation { color: #1f1f1f }
/* as VS Code: control-flow keywords (import, if, for, return ...) purple, built-in functions yellow */
:root[data-code='light'] .token.keyword.control-flow { color: #af00db }
:root[data-code='light'] .language-python .token.builtin { color: #795e26 }
:root[data-code='dark'] .language-python .token.builtin, :root[data-code='dark'] .token.decorator { color: #dcdcaa }
.language-ode .token.comment { font-style: italic }

/* tables */
.table-wrap { margin: 1em 0 1.3em; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px }
.doc table { width: 100%; border-collapse: collapse; font-size: .9375rem; line-height: 1.45 }
.doc th { background: var(--panel-bar); text-align: left; font-weight: 600 }
.doc th, .doc td { padding: 7px 12px; border-bottom: 1px solid var(--line); vertical-align: top }
.doc tbody tr:last-child td { border-bottom: 0 }
.doc tbody tr:nth-child(even) { background: color-mix(in srgb, var(--panel-bar) 45%, transparent) }

/* back to top, the "copied" note */
.totop { position: fixed; right: max(14px, env(safe-area-inset-right)); bottom: max(14px, env(safe-area-inset-bottom)); z-index: 15; display: grid; place-items: center; width: 44px; height: 44px;
       border: 1px solid var(--line); border-radius: 50%; background: var(--bar); color: var(--fg); cursor: pointer;
       box-shadow: 0 4px 14px rgb(0 0 0 / .25); opacity: 0; transform: translateY(10px); pointer-events: none; transition: opacity .2s, transform .2s }
.totop.show { opacity: 1; transform: none; pointer-events: auto }
.totop:hover { background: var(--panel-bar-active) }
.toast { position: fixed; left: 50%; bottom: 22px; z-index: 40; padding: 7px 14px; border-radius: 6px; background: var(--fg); color: var(--bg);
       font-size: .875rem; transform: translate(-50%, 20px); opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s }
.toast.show { opacity: 1; transform: translate(-50%, 0) }

/* narrow windows: the contents become a drawer opened by the menu button */
@media (max-width: 960px) {
  .layout { display: block }
  .tocbtn, .tocclose { display: grid }
  .mnav { display: none }
  .bar { gap: 10px }
  .toc { position: fixed; top: 0; left: 0; bottom: 0; z-index: 35; width: min(330px, 86vw); height: auto; border-right: 1px solid var(--line);
         box-shadow: 8px 0 30px rgb(0 0 0 / .35); transform: translateX(-104%); visibility: hidden; transition: transform .2s, visibility .2s }
  .toc.open { transform: none; visibility: visible }
  .scrim { position: fixed; inset: 0; z-index: 34; background: rgb(0 0 0 / .45) }
  body.noscroll { overflow: hidden }
  .toc-nav ul a { padding: 7px 8px }
  .toc .tg { height: calc(1.35em + 14px); width: 30px }
  .toc .tg-sp { width: 30px }
  .toc ul ul { margin-left: 30px }
}
@media (max-width: 1180px) { .mnav a.more { display: none } }
@media (max-width: 480px) {
  .doc { padding: 14px 16px 80px }
  .doc h1 { font-size: 1.6rem }
  .doc h2 { font-size: 1.3rem }
  .doc pre[class*='language-'] { padding: 10px 12px; font-size: .8125rem }
  .crumb { display: none }
}
@media (prefers-reduced-motion: reduce) { .toc, .totop, .toast, .toc .tg svg { transition: none } }

/* print: the text and the code only, code wraps */
@media print {
  .bar, .toc, .scrim, .totop, .toast, .progress, .skip, .cb-copy, .anchor { display: none !important }
  .layout { display: block; max-width: none }
  body, .doc { background: #fff !important; color: #000 !important }
  .doc { max-width: none; padding: 0 }
  .doc a { color: #000 }
  .doc :not(pre) > code { background: #eee }
  .cb { break-inside: avoid; border-color: #bbb; background: #fff !important }
  .cb-head { background: #f3f3f3 !important; color: #333 !important }
  .doc pre[class*='language-'] { white-space: pre-wrap; overflow: visible; overflow-wrap: anywhere }
  .doc code[class*='language-'] { white-space: pre-wrap }
  /* printing switches the code to the light colours (DISPLAY_JS, beforeprint); without that, plain dark text */
  :root[data-code='dark'] .doc pre[class*='language-'], :root[data-code='dark'] .doc pre[class*='language-'] * { color: #1f1f1f !important }
  .doc h2, .doc h3 { break-after: avoid }
  .table-wrap { overflow: visible }
}
"""

MANUAL_JS = r"""
(function () {
  const $ = id => document.getElementById(id), root = document.documentElement;
  const bar = document.querySelector('.bar'), toc = $('toc'), nav = $('tocnav'), q = $('tocq');

  // ---- toast: a short note at the bottom ("Copied", "Link copied") --------------------
  let toastTimer;
  function toast(msg) {
    const t = $('toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 1600);
  }
  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true } catch (e) {
      const ta = document.createElement('textarea');   // older browsers, pages not served over https
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.append(ta); ta.select();
      let ok = false; try { ok = document.execCommand('copy') } catch (e2) {}
      ta.remove(); return ok;
    }
  }

  // ---- syntax colours: Prism (python, bash) and a small grammar for XPP .ode files ----
  if (window.Prism && Prism.languages) {
    Prism.languages.ode = {
      'after-done': { pattern: /(^done[ \t]*\n)[\s\S]*/m, lookbehind: true, alias: 'comment' },
      comment: [{ pattern: /(^|\s)#.*/m, lookbehind: true }, { pattern: /^\s*".*/m }],
      keyword: { pattern: /^(\s*)(?:par(?:am)?|p|init|i|aux|number|num|done|set|global|table|wiener|markov|bdry|volt|special|only|export|options)\b|^\s*@/m, lookbehind: true },
      property: { pattern: /^(\s*)(?:\w+'|d\w+\/dt|\w+\(t\+dt\))(?=\s*=)/m, lookbehind: true },
      function: /\b\w+(?=\()/,
      number: /(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?\b/i,
      operator: /[-+*\/^=<>!]/,
      punctuation: /[(){},;\[\]]/,
    };
    // VS Code colours Python's control-flow keywords apart from the others (def, class, lambda, None ...)
    const flow = /^(?:import|from|as|if|elif|else|for|while|try|except|finally|return|with|break|continue|pass|raise|yield|await|assert|del)$/;
    Prism.hooks.add('wrap', env => {
      if (env.language !== 'python' || env.type !== 'keyword') return;
      if (flow.test(env.content)) env.classes.push('control-flow');
      // Prism still counts Python 2's print as a keyword; VS Code colours it as the built-in function it is
      else if (env.content === 'print' || env.content === 'exec') env.classes = env.classes.map(c => c === 'keyword' ? 'builtin' : c);
    });
    try { Prism.highlightAll() } catch (e) {}
  }

  // ---- copy buttons: the exact text of the block (without $ / >>> prompts) ---------------
  for (const b of document.querySelectorAll('.cb-copy')) {
    b.addEventListener('click', async () => {
      const code = b.closest('.cb').querySelector('code');
      let text = code.textContent.replace(/\n$/, '');
      if (code.classList.contains('language-bash')) text = text.replace(/^\$ /gm, '');
      if (/^>>> /m.test(text)) text = text.split('\n').filter(l => /^(>>>|\.\.\.)( |$)/.test(l)).map(l => l.slice(4)).join('\n');
      const ok = await copyText(text), msg = b.querySelector('.cb-msg');
      msg.textContent = ok ? 'Copied' : 'Select and copy'; b.classList.toggle('ok', ok);
      toast(ok ? 'Copied to the clipboard' : 'Could not copy: select the text and copy it');
      clearTimeout(b._t); b._t = setTimeout(() => { msg.textContent = 'Copy'; b.classList.remove('ok') }, 1600);
    });
  }

  // ---- heading links: go there and copy the address ------------------------------------
  document.addEventListener('click', async e => {
    const a = e.target.closest('a.anchor');
    if (!a) return;
    e.preventDefault();
    const hash = a.getAttribute('href');
    history.replaceState(null, '', hash);
    a.parentElement.scrollIntoView({ block: 'start' });
    toast(await copyText(location.href) ? 'Link copied' : 'Link in the address bar');
  });

  // ---- the toolbar's height (it grows with the text size): the sidebar sits below it ----
  const setBar = () => root.style.setProperty('--barh', bar.offsetHeight + 'px');
  setBar(); addEventListener('resize', setBar); document.addEventListener('pyx-display', setBar);

  // ---- contents: collapsible groups, scroll-spy -------------------------------------------
  const links = [...nav.querySelectorAll('ul a')];
  const heads = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1))));
  let current = null, autoOpen = null;
  function setOpen(li, on) {
    li.classList.toggle('open', on);
    li.querySelector(':scope > .row > .tg')?.setAttribute('aria-expanded', String(on));
  }
  for (const t of nav.querySelectorAll('.tg')) t.addEventListener('click', () => {
    const li = t.closest('li'); li.dataset.user = '1'; if (autoOpen === li) autoOpen = null;
    setOpen(li, !li.classList.contains('open'));
  });
  function setActive(a) {
    if (a === current) return;
    if (current) { current.classList.remove('active'); current.removeAttribute('aria-current') }
    current = a;
    if (!a) return;
    a.classList.add('active'); a.setAttribute('aria-current', 'location');
    // open the group of the section being read; close the one opened before (unless the reader opened it)
    const li = a.closest('li.l2');
    if (autoOpen && autoOpen !== li && !autoOpen.dataset.user) setOpen(autoOpen, false);
    if (li && li.querySelector('ul') && !li.classList.contains('open')) { setOpen(li, true); autoOpen = li }
    // keep it in view inside the sidebar
    const r = a.getBoundingClientRect(), n = nav.getBoundingClientRect();
    if (n.height && (r.top < n.top + 8 || r.bottom > n.bottom - 8)) nav.scrollTop += r.top - n.top - n.height / 3;
  }
  function spy() {
    const y = bar.offsetHeight + 24;
    let k = -1;
    for (let i = 0; i < heads.length; i++) { if (heads[i] && heads[i].getBoundingClientRect().top <= y) k = i; else if (heads[i]) break }
    if (innerHeight + scrollY >= root.scrollHeight - 4) k = heads.length - 1;
    setActive(k >= 0 ? links[k] : null);
  }

  // ---- reading progress and "back to top" ----------------------------------------------
  const prog = $('progress'), top = $('totop');
  function onScroll() {
    const h = root.scrollHeight - innerHeight;
    prog.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
    top.classList.toggle('show', scrollY > 700);
    spy();
  }
  let ticking = false;
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; onScroll() }) } }, { passive: true });
  addEventListener('resize', onScroll); document.addEventListener('pyx-display', onScroll);
  top.addEventListener('click', () => { scrollTo({ top: 0 }); history.replaceState(null, '', location.pathname + location.search); $('main').focus({ preventScroll: true }) });
  onScroll();

  // ---- filter the contents ("/" focuses it) ------------------------------------------------
  const words = el => el.textContent.toLowerCase();
  function filter() {
    const w = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean), has = el => w.every(x => words(el).includes(x));
    nav.classList.toggle('filtering', w.length > 0);
    let any = false;
    for (const li of nav.querySelectorAll('li.l2')) {
      const self = !w.length || has(li.querySelector(':scope > .row > a'));
      let kid = false;
      for (const k of li.querySelectorAll('li.l3')) { const m = self || has(k); k.hidden = !m; kid = kid || (m && w.length > 0 && has(k)) }
      li.hidden = !(self || kid); any = any || !li.hidden;
    }
    $('tocempty').hidden = any;
  }
  q.addEventListener('input', filter);
  q.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const a = links.find(l => !l.closest('li[hidden]'));
      if (a) { a.click(); location.hash = a.hash }
    } else if (e.key === 'Escape') {
      if (q.value) { e.stopPropagation(); q.value = ''; filter() } else if (toc.classList.contains('open')) { e.stopPropagation(); openToc(false, true) } else q.blur();
    }
  });
  document.addEventListener('keydown', e => {
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target;
    if (t.closest('input, textarea, select, [contenteditable=""], [contenteditable="true"]')) return;
    e.preventDefault();
    if (drawer() && !toc.classList.contains('open')) openToc(true, false, true);
    q.focus(); q.select();
  });

  // ---- phones: the contents as a drawer ---------------------------------------------------
  const btn = $('tocbtn'), scrim = $('scrim');
  const drawer = () => matchMedia('(max-width: 960px)').matches;
  function openToc(on, refocus, focusFilter) {
    toc.classList.toggle('open', on); scrim.hidden = !on; btn.setAttribute('aria-expanded', String(on));
    document.body.classList.toggle('noscroll', on);
    if (on) {
      if (current) { const r = current.getBoundingClientRect(), n = nav.getBoundingClientRect(); nav.scrollTop += r.top - n.top - n.height / 3 }
      // from "/": the filter; from the button: the section being read (no keyboard popping up on phones)
      setTimeout(() => (focusFilter ? q : (current || nav.querySelector('a'))).focus({ preventScroll: true }), 60);
    } else if (refocus) btn.focus();
  }
  btn.addEventListener('click', () => openToc(!toc.classList.contains('open'), true));
  $('tocclose').addEventListener('click', () => openToc(false, true));
  scrim.addEventListener('click', () => openToc(false));
  nav.addEventListener('click', e => { if (e.target.closest('a') && drawer()) openToc(false) });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && toc.classList.contains('open')) openToc(false, true) });
  addEventListener('resize', () => { if (!drawer() && toc.classList.contains('open')) openToc(false) });
})();
"""


def manual(site):
    """site/manual/index.html from the usage guide (pandoc), themed like the page (see the notes above)"""
    import subprocess
    text = (MANUAL_SRC / "USAGE.mdx").read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    text = re.sub(r"pyauto-xpp runs XPPAUT 8\.1 and its own AUTO from Python, without the X11\s+window\.",
                  "pyauto-xpp runs XPPAUT 8.4 and its own AUTO from Python.", text)
    # links to XPPAUT's page and Bard Ermentrout's homepage (with his permission)
    text = text.replace("pyauto-xpp runs XPPAUT 8.4 and its own AUTO from Python",
                        "pyauto-xpp runs [XPPAUT](https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html) 8.4 and its own AUTO from Python", 1)
    text = text.replace("The package carries Bard Ermentrout's XPPAUT 8.4 source",
                        "The package carries [Bard Ermentrout](https://sites.pitt.edu/~phase/)'s [XPPAUT](https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html) 8.4 source", 1)
    body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none", "--no-highlight"], input=text, text=True,
                          capture_output=True, check=True).stdout
    out = site / "manual"; out.mkdir()
    shutil.copytree(MANUAL_SRC / "figures", out / "figures")
    body = _topic_ids(body)
    toc = _manual_toc(body)
    body = _manual_body(body)
    prism_css = "\n".join(
        f'<link rel="stylesheet" data-code="{k}" media="not all" href="{CDN}{f}" integrity="{sri}" crossorigin="anonymous" referrerpolicy="no-referrer">'
        for k, (f, sri) in PRISM_CSS.items())
    prism_js = "\n".join(f'<script src="{CDN}{f}" integrity="{sri}" crossorigin="anonymous" referrerpolicy="no-referrer"></script>'
                         for f, sri in PRISM_JS)
    page = MANUAL_PAGE
    for k, v in {   # __BODY__ last: the manual's text is not searched for placeholders
        "__PRISM_CSS__": prism_css, "__PRISM_JS__": prism_js, "__DISPLAY_HEAD__": display_head(),
        "__THEMES__": theme_css(), "__TOOLBAR_CSS__": TOOLBAR_CSS, "__DISPLAY_CSS__": DISPLAY_CSS,
        "__MANUAL_CSS__": MANUAL_CSS, "__DISPLAY_BUTTON__": DISPLAY_BUTTON, "__DISPLAY_JS__": display_js(),
        "__MANUAL_JS__": MANUAL_JS, "__ICON_MENU__": ICON_MENU, "__GH__": GH, "__TOC__": toc,
    }.items():
        page = page.replace(k, v)
    left = set(re.findall(r"__[A-Z_]+__", page)) - {"__BODY__"}
    assert not left, left
    page = page.replace("__BODY__", body)
    (out / "index.html").write_text(page)


def gallery(site):
    """copy the gallery figures to site/gallery/; return their entries.  An animated GIF
    (gallery_gif.py) is used when there is one, with its last frame as a PNG poster;
    otherwise the static figure (made smaller)"""
    from PIL import Image
    (site / "gallery").mkdir()
    out = []
    for script, fig, title, cap in GALLERY:
        gif = Path(__file__).resolve().parent / "gallery-build" / "gifs" / f"{script}_{Path(fig).stem}.gif"
        poster = gif.with_suffix(".png")
        if gif.is_file() and poster.is_file():
            shutil.copy2(gif, site / "gallery" / gif.name)
            shutil.copy2(poster, site / "gallery" / poster.name)
            with Image.open(gif) as im:
                w, h = im.size
            out.append(dict(src=f"gallery/{gif.name}", poster=f"gallery/{poster.name}", w=w, h=h,
                            title=title, cap=cap,
                            file="tutorials/worked-examples/" + worked_notebook(int(script[:2]))))
            continue
        pub = Path(__file__).resolve().parent / "gallery-build" / "figures" / script / fig        # publication style (gallery_pub.py)
        src = pub if pub.is_file() else FIGS / script / fig
        if not src.is_file():
            print(f"  gallery: {src.name} of {script} is missing (run the script); left out")
            continue
        name = f"{script}_{fig}"
        im = Image.open(src).convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        if src != pub:
            im = im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        im.save(site / "gallery" / name, optimize=True)
        out.append(dict(src=f"gallery/{name}", w=im.width, h=im.height, title=title, cap=cap,
                        file="tutorials/worked-examples/" + worked_notebook(int(script[:2]))))
    return out


# ---- the page ---------------------------------------------------------------
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>pyauto-xpp: XPPAUT and AUTO in Python</title>
<meta name="description" content="XPPAUT 8.4 and its AUTO as a Python module (import pyxpp): simulations, phase planes, nullclines and bifurcation diagrams from Python, with __N__ tutorials.">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta property="og:title" content="pyauto-xpp">
<meta property="og:description" content="XPPAUT 8.4 and AUTO as a Python module, with __N__ tutorials.">
<meta property="og:image" content="__OGIMAGE__">
__DISPLAY_HEAD__
<style>
__THEMES__
__TOOLBAR_CSS__
__DISPLAY_CSS__
:root[data-theme^='funky'] .hero { background: var(--desk) }

* { box-sizing: border-box }
html { scroll-behavior: smooth; scroll-padding-top: 64px; -webkit-text-size-adjust: 100% }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto } }
body { margin: 0; background: var(--bg); color: var(--fg); font-size: .9375rem; line-height: 1.55; overflow-x: hidden }
a { color: var(--accent) }
a.btn { color: var(--accent-fg) } a.btn.ghost { color: var(--fg) }
code, pre, kbd, .mono { font-family: var(--font-mono); font-size: .8125rem }
.muted { color: var(--muted) }

/* ---- top bar: the shared parts (.bar, .brand, menus) are in TOOLBAR_CSS ---- */
.ver { font: .75rem ui-monospace, Menlo, Consolas, monospace; padding: 1px 6px; border: 1px solid var(--line); border-radius: 10px; color: var(--muted); text-decoration: none }
.nav { display: flex; align-items: center; gap: 2px; flex-wrap: wrap }
.nav a { color: var(--fg); text-decoration: none; padding: 5px 9px; border-radius: 4px }
.nav a:hover, .nav a[aria-current='true'] { background: var(--panel-bar-active) }
.menu { display: none }
/* the section links fold into the menu when they do not fit: on phones (below), earlier with larger
   text (here), and whenever the script finds that they wrap (.bar.fold, e.g. with a wide font) */
.bar.fold .nav, .bar.fold .ver { display: none }
.bar.fold .menu { display: block }
@media (max-width: 900px) {
  :root[data-textsize='112'] .nav, :root[data-textsize='112'] .bar .ver { display: none }
  :root[data-textsize='112'] .menu { display: block }
}
@media (max-width: 1000px) {
  :root[data-textsize='125'] .nav, :root[data-textsize='125'] .bar .ver { display: none }
  :root[data-textsize='125'] .menu { display: block }
}

/* ---- buttons --------------------------------------------------------------- */
.btn { display: inline-flex; align-items: center; gap: 8px; min-height: 38px; padding: 7px 14px; border-radius: 6px;
       background: var(--accent); color: var(--accent-fg); border: 1px solid var(--accent); text-decoration: none;
       font: inherit; font-size: .875rem; font-weight: 600; cursor: pointer }
.btn:hover { filter: brightness(1.08) }
.btn.ghost { background: var(--bar); color: var(--fg); border-color: var(--line); font-weight: 500 }
.btn.ghost:hover { background: var(--panel-bar-active); filter: none }
.btn svg { flex: none }

/* ---- layout ---------------------------------------------------------------- */
main { display: block }
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 16px }
section { padding: 30px 0 6px }
h2 { font-size: 1.25rem; margin: 0 0 6px; display: flex; align-items: baseline; gap: 10px }
h2 a.anchor { font-size: .875rem; color: var(--muted); text-decoration: none; opacity: 0 }
h2:hover a.anchor, h2 a.anchor:focus { opacity: 1 }
h3 { font-size: .9375rem; margin: 0 0 4px }
.lead { margin: 0 0 14px; color: var(--muted); max-width: 70ch }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center }

.hero { background: var(--panel-bar); border-bottom: 1px solid var(--line) }
.hero .wrap { display: grid; grid-template-columns: auto 1fr; gap: 22px; align-items: center; padding-top: 30px; padding-bottom: 28px }
.mark-wrap { position: relative; margin: 0; outline: none }
.mark-tip { position: absolute; left: 0; top: calc(100% + 10px); z-index: 5; width: min(340px, 80vw); padding: 12px 14px;
  border-radius: 12px; background: var(--bar); color: var(--fg); border: 1px solid var(--accent); font-size: .875rem; line-height: 1.45;
  box-shadow: 0 10px 28px rgb(0 0 0 / 0.35); opacity: 0; transform: translateY(-6px); pointer-events: none; transition: opacity .18s, transform .18s }
.mark-wrap:hover .mark-tip, .mark-wrap:focus .mark-tip, .mark-wrap:focus-within .mark-tip { opacity: 1; transform: none }
.hero img.mark { cursor: help; width: 150px; height: 150px; border-radius: 22px; box-shadow: 0 6px 22px rgb(0 0 0 / 0.25) }
.hero h1 { margin: 0; font-size: 1.875rem; line-height: 1.15 }
.hero p { margin: 8px 0 14px; max-width: 64ch }
.facts { display: flex; flex-wrap: wrap; gap: 6px 14px; margin: 0 0 16px; padding: 0; list-style: none; font-size: .8125rem; color: var(--muted) }
.facts li::before { content: '\25CF'; color: var(--accent); margin-right: 6px; font-size: .5625rem; vertical-align: 2px }

/* ---- gallery --------------------------------------------------------------- */
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px }
.shot { margin: 0; background: var(--bar); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; display: flex; flex-direction: column }
.shot button { display: block; padding: 0; border: 0; background: var(--bar); cursor: zoom-in; aspect-ratio: 16 / 10; width: 100% }
.shot img { width: 100%; height: 100%; object-fit: contain; display: block }
.shot figcaption { padding: 8px 12px 10px; font-size: .8125rem; color: var(--muted); border-top: 1px solid var(--line); flex: 1 }
.shot figcaption b { display: block; color: var(--fg); font-size: .875rem }
dialog.lightbox { width: min(1200px, calc(100vw - 24px)); max-height: calc(100vh - 24px); padding: 0; border: 1px solid var(--line);
       border-radius: 8px; background: var(--bar); color: var(--fg) }
dialog.lightbox::backdrop { background: rgb(0 0 0 / 0.7) }
dialog.lightbox img { display: block; width: 100%; height: auto; max-height: calc(100vh - 140px); object-fit: contain; background: var(--bar) }
.lb-bar { display: flex; align-items: center; gap: 8px; padding: 8px 10px; flex-wrap: wrap }
.lb-bar .t { flex: 1 1 220px; font-size: .8125rem; color: var(--muted) } .lb-bar .t b { color: var(--fg) }
.iconbtn { min-width: 38px; min-height: 38px; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); color: var(--fg); font: inherit; font-size: 1.125rem; cursor: pointer }
.iconbtn:hover { background: var(--panel-bar-active) }

/* ---- quick start ------------------------------------------------------------ */
.tabs { display: flex; gap: 0; border-bottom: 1px solid var(--line); overflow-x: auto; scrollbar-width: none }
.tabs button { flex: none; padding: 9px 14px; border: 0; border-bottom: 3px solid transparent; background: transparent; color: var(--muted);
       font: inherit; font-size: .875rem; cursor: pointer; margin-bottom: -1px }
.tabs button[aria-selected='true'] { color: var(--fg); border-bottom-color: var(--accent); font-weight: 600 }
.tabs button:hover { color: var(--fg) }
.tabpanel { padding: 14px 0 0 }
.tabpanel p { margin: 0 0 10px; max-width: 75ch }
.os { display: inline-flex; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin-bottom: 10px }
.os button { padding: 6px 12px; border: 0; background: var(--bar); color: var(--fg); font: inherit; font-size: .8125rem; cursor: pointer; min-height: 34px }
.os button + button { border-left: 1px solid var(--line) }
.os button[aria-pressed='true'] { background: var(--accent); color: var(--accent-fg) }
.code { position: relative; margin: 0 0 12px }
.code pre { margin: 0; background: var(--term-bg); color: var(--term-fg); padding: 12px 14px; padding-right: 64px; border-radius: 6px;
       overflow-x: auto; line-height: 1.5; border: 1px solid var(--line) }
.code pre .c { color: #8f9aa5 }
.copy { position: absolute; top: 7px; right: 7px; padding: 3px 9px; min-height: 28px; border: 1px solid #ffffff33; border-radius: 4px;
       background: var(--term-head); color: var(--term-fg); font: .75rem system-ui, sans-serif; cursor: pointer }
.copy:hover { background: #ffffff22 }
.note { padding: 9px 12px; border-left: 3px solid var(--accent); background: var(--panel-bar); border-radius: 0 6px 6px 0; font-size: .875rem; max-width: 80ch }

/* ---- downloads -------------------------------------------------------------- */
.dl { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px }
.dl a.box { display: flex; flex-direction: column; gap: 2px; padding: 12px 14px; min-height: 64px; background: var(--bar); border: 1px solid var(--line);
       border-radius: 8px; color: var(--fg); text-decoration: none }
.dl a.box:hover { border-color: var(--accent); background: var(--panel-bar-active) }
.dl a.box b { display: flex; align-items: center; gap: 8px; font-size: .875rem }
.dl a.box span { font-size: .78125rem; color: var(--muted) }
.dl a.box .mono { font-size: .75rem }
.dl a.box.soon { opacity: 0.75; border-style: dashed }

/* ---- tutorials -------------------------------------------------------------- */
.filters { display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; margin: 6px 0 12px; position: sticky; top: 48px; z-index: 3; background: var(--bg); padding: 8px 0;
       border-bottom: 1px solid var(--line) }
.search { position: relative; flex: 1 1 260px; max-width: 420px; min-width: 0 }   /* min-width: no wider than a phone */
.search input { width: 100%; font: inherit; font-size: .9375rem; min-height: 38px; padding: 6px 10px 6px 34px; border-radius: 6px;
       border: 1px solid var(--line); background: var(--bar); color: var(--fg) }
.search svg { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--muted) }
.chips { display: flex; gap: 6px; flex-wrap: wrap }
.chip { padding: 4px 11px; min-height: 32px; border: 1px solid var(--line); border-radius: 16px; background: var(--bar); color: var(--fg);
       font: inherit; font-size: .8125rem; cursor: pointer; white-space: nowrap }
.chip:hover { background: var(--panel-bar-active) }
.chip[aria-pressed='true'] { background: var(--accent); color: var(--accent-fg); border-color: var(--accent) }
.chip small { opacity: 0.75; margin-left: 3px }
.count { font-size: .8125rem; color: var(--muted) }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 10px }
.card { display: flex; flex-direction: column; background: var(--bar); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px 8px }
.card .k { display: flex; gap: 6px; font-size: .6875rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted) }
.card .k .nb { color: var(--accent) }
.card h3 { margin: 4px 0 2px; font-size: .90625rem }
.card.iso img { width: 100%; height: auto; border-radius: 6px; margin: 2px 0 8px; background: #fff }
.card p { margin: 2px 0 6px; font-size: .8125rem; color: var(--muted); flex: 1 }
.card .f { font-size: .71875rem; color: var(--muted); overflow-wrap: anywhere }
.card .links { display: flex; gap: 2px; margin: 6px -6px 0; flex-wrap: wrap }
.card .links a { padding: 5px 6px; font-size: .8125rem; border-radius: 4px; text-decoration: none }
.card .links a:hover { background: var(--panel-bar-active) }
.empty { padding: 20px; text-align: center; color: var(--muted); border: 1px dashed var(--line); border-radius: 8px }
.empty button { font: inherit; color: var(--accent); background: none; border: 0; text-decoration: underline; cursor: pointer }

/* ---- sister project, footer --------------------------------------------------- */
.sister { display: grid; grid-template-columns: auto 1fr auto; gap: 20px; align-items: center; padding: 20px 22px;
  border-radius: 16px; text-decoration: none; color: var(--fg); border: 2px solid var(--accent);
  background: linear-gradient(120deg, color-mix(in srgb, var(--accent) 16%, var(--bar)), var(--bar) 70%);
  box-shadow: 0 8px 26px color-mix(in srgb, var(--accent) 22%, transparent); transition: transform .15s, box-shadow .15s }
.sister:hover { transform: translateY(-2px); box-shadow: 0 12px 32px color-mix(in srgb, var(--accent) 32%, transparent) }
.sister b { font-size: 1.3125rem }
.sister p { margin: 4px 0 0; color: var(--muted); font-size: .9375rem }
.sister .logo { width: 96px; height: 96px; border-radius: 20px; box-shadow: 0 4px 14px rgb(0 0 0 / 0.25) }
/* the smaller card under it (notebook, the isochron book) */
.sister.mini { margin-top: 10px; gap: 12px; padding: 4px 6px 4px 10px; border-width: 1.5px; border-radius: 10px; box-shadow: 0 3px 10px color-mix(in srgb, var(--accent) 14%, transparent) }
.sister.mini > div { display: flex; align-items: baseline; gap: 10px; min-width: 0 }
.sister.mini b { font-size: .9375rem; white-space: nowrap }
.sister.mini p { margin: 0; font-size: .8125rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0 }
.sister.mini .logo { width: 28px; height: 28px; border-radius: 7px; box-shadow: 0 1px 5px rgb(0 0 0 / 0.2) }
.sister.mini .btn { padding: 3px 10px; font-size: .75rem; min-height: 0 }
footer { margin-top: 36px; padding: 22px 0 30px; border-top: 1px solid var(--line); background: var(--bar); font-size: .84375rem; color: var(--muted) }
footer ul { margin: 6px 0 12px; padding-left: 18px }
footer .row a { color: var(--fg); display: inline-block; padding: 8px 4px }

/* ---- phones (as XPPAUT-Web: the toolbar folds into a menu) -------------------- */
@media (max-width: 760px) {
  .nav, .bar .ver { display: none }
  .menu { display: block }
  .bar { gap: 8px }
  .hero .wrap { grid-template-columns: 1fr; gap: 12px; padding-top: 20px; padding-bottom: 20px }
  .hero img.mark { width: 120px; height: 120px; border-radius: 20px }
  .hero h1 { font-size: 1.5625rem }
  .sister { grid-template-columns: auto 1fr }
  .sister .btn { grid-column: 1 / -1; justify-content: center }
  .sister .logo { width: 72px; height: 72px }
  .sister.mini .btn { display: none }
  .gallery { grid-template-columns: 1fr }
  .filters { top: 48px }
  .search { max-width: none }
  .chips { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; margin: 0 -16px; padding: 0 16px }
  .chips::-webkit-scrollbar, .tabs::-webkit-scrollbar { display: none }
  .cards { grid-template-columns: 1fr }
  h2 a.anchor { display: none }
}
/* comfortable touch targets */
@media (pointer: coarse) {
  .nav a, .panel button, .panel a { min-height: 44px }
  summary.round { width: 40px; height: 40px }
  .chip { min-height: 40px; padding: 6px 14px }
  .card .links a { padding: 10px 8px }
  .os button, .tabs button { min-height: 44px }
  .btn { min-height: 44px }
  .copy { min-height: 34px; padding: 4px 12px }
}
/* the top section's Editor button: a moving gradient, a soft glow */
.btn.shiny { position: relative; border: 0; color: #011627; font-weight: 700;
             background: linear-gradient(115deg, #82aaff, #c792ea, #f78c6c, #addb67, #7fdbca, #82aaff);
             background-size: 300% 300%; animation: edglow 6s linear infinite, throb 2.4s ease-in-out infinite;
             transform-origin: center }
@keyframes throb {
  0%   { transform: scale(1);    box-shadow: 0 0 0 0 rgba(199,146,234,.65), 0 4px 18px rgba(199,146,234,.45) }
  45%  { transform: scale(1.07); box-shadow: 0 0 0 12px rgba(199,146,234,0), 0 6px 26px rgba(130,170,255,.6) }
  100% { transform: scale(1);    box-shadow: 0 0 0 0 rgba(199,146,234,0), 0 4px 18px rgba(199,146,234,.45) }
}
.btn.shiny:hover { filter: brightness(1.1); animation: edglow 6s linear infinite; transform: scale(1.07);
                   box-shadow: 0 6px 26px rgba(130,170,255,.65) }
.btn.shiny svg { fill: currentColor }
.btn.shiny .new { font-size: .68rem; font-weight: 800; letter-spacing: .05em; text-transform: uppercase;
                  padding: 1px 6px; border-radius: 99px; background: #011627; color: #fff }
@media (prefers-reduced-motion: reduce) { .btn.shiny { animation: none; box-shadow: 0 4px 18px rgba(199,146,234,.45) } }
/* the editor card: a moving gradient border */
.edcard { position: relative; margin: 26px 0 6px; padding: 2px; border-radius: 14px; overflow: hidden;
          background: linear-gradient(115deg, #82aaff, #c792ea, #f78c6c, #addb67, #7fdbca, #82aaff);
          background-size: 300% 300%; animation: edglow 9s linear infinite }
@keyframes edglow { 0% { background-position: 0% 50% } 100% { background-position: 300% 50% } }
@media (prefers-reduced-motion: reduce) { .edcard { animation: none } }
.edcard .in { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px 24px; align-items: center;
              padding: 20px 22px; border-radius: 12px; background: var(--bg) }
.edcard .tag { display: inline-block; font-size: .75rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
               padding: 2px 8px; border-radius: 99px; background: linear-gradient(115deg, #82aaff, #c792ea); color: #011627 }
.edcard h2 { margin: 8px 0 6px; font-size: 1.35rem }
.edcard p { margin: 0 0 8px; color: var(--muted) }
.edcard ul { margin: 6px 0 0; padding-left: 1.2em; color: var(--muted) }
.edcard ul li { margin: 2px 0 }
.edcard .go { display: flex; flex-direction: column; gap: 10px; align-items: stretch; min-width: 230px }
.edcard .go .btn { justify-content: center; text-align: center }
.edcard { margin: 34px 0 10px }
@media (max-width: 720px) { .edcard .in { grid-template-columns: 1fr } .edcard .go { min-width: 0 } }
/* landscape phones: little height, so the bar scrolls away */
@media (max-height: 500px) and (orientation: landscape) {
  .bar { position: static }
  .filters { position: static }
  html { scroll-padding-top: 8px }
}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <a class="brand" href="#top"><img src="icon.svg" alt="" width="22" height="22">pyauto-xpp</a>
  <a class="ver" href="__GH__/releases/tag/v__VER__" title="Latest release">v__VER__</a>
  <nav class="nav" aria-label="Sections">__NAV__</nav>
  <div class="right">
    <details class="menu" id="menu">
      <summary class="round" title="Menu" aria-label="Menu">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </summary>
      <div class="panel" role="menu">__NAVMENU__</div>
    </details>
    __DISPLAY_BUTTON__
  </div>
</header>

<main id="main">
<div class="hero" id="top">
  <div class="wrap">
    <figure class="mark-wrap" tabindex="0" aria-describedby="mark-tip">
      <img class="mark" src="icon.svg" alt="The pyauto-xpp logo: an auto-rickshaw doing a wheelie on a bifurcation diagram" width="96" height="96">
      <figcaption class="mark-tip" id="mark-tip" role="tooltip">On the streets of India, auto-rickshaw drivers thread through
        the busiest traffic with remarkable finesse, always finding a way through the tightest gap. The logo is a tribute
        to them: our AUTO keeps its balance on a bifurcation branch the same way.</figcaption>
    </figure>
    <div>
      <h1>pyauto-xpp</h1>
      <p><a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a> 8.4, by <a href="https://sites.pitt.edu/~phase/" target="_blank" rel="noopener">Bard Ermentrout</a>, and its AUTO, made available to Python. For batch work and Python workflows: every XPP command
         is a Python call, AUTO runs from scripts (also for delay equations), and models can be written in Python.
         For interactive exploration, <a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a> itself remains the place to go;
         both share the same numerics.</p>
      <ul class="facts">
        <li><code>import pyxpp</code></li><li>__N__ tutorials</li><li>Linux, macOS and Windows wheels, Python 3.9-3.15</li><li>GPL-3.0-or-later</li>
      </ul>
      <div class="row">
        <a class="btn shiny" href="editor/" title="Write and run pyauto-xpp code here; it runs on your computer">__ICON_PLAY__Try the editor <span class="new">new</span></a>
        <a class="btn ghost" href="https://colab.research.google.com/github/ZetaOne/pyauto-xpp/blob/main/tutorials/worked-examples/01_first-steps.ipynb" target="_blank" rel="noopener" title="Google Colab: the first cell installs pyauto-xpp with pip">__ICON_PLAY__Try it in Colab</a>
        <a class="btn ghost" href="https://codespaces.new/ZetaOne/pyauto-xpp?quickstart=1" title="Uses your GitHub account's free Codespaces hours">Open in Codespaces</a>
        <a class="btn ghost" href="#install">Install</a>
        <a class="btn ghost" href="#tutorials">Tutorials</a>
        <a class="btn ghost" href="manual/">Manual</a>
        <a class="btn ghost" href="__GH__">__ICON_GH__GitHub</a>
      </div>
    </div>
  </div>
</div>

<div class="wrap">
  <section id="gallery" aria-labelledby="h-gallery">
    <h2 id="h-gallery">Gallery <a class="anchor" href="#gallery" aria-label="Link to Gallery">#</a></h2>
    <p class="lead">Figures made by the tutorial scripts, with XPP's integrators and AUTO called from Python. Click one to enlarge it.</p>
    <div class="gallery">__GALLERY__</div>
  </section>
  <aside class="edcard" aria-labelledby="h-editor">
    <div class="in">
      <div>
        <span class="tag">New &middot; v0.6</span>
        <h2 id="h-editor">Code in your browser. Run it on your machine.</h2>
        <p>Write and run pyauto-xpp code on a web page, with no terminal work, environments or notebooks to manage.
           The code runs on <b>your own computer</b>, at full speed, with your files on your disk.</p>
        <ul>
          <li>one install line, shown for your system; it sets up everything else by itself</li>
          <li>tabs, folders, an arrow on the line that is running, figures right beside the code</li>
          <li>notebooks too: run the cells, outputs and equations under each</li>
          <li>updates with one click when a new version is out</li>
          <li>removed with one command when you are done (<a href="editor/#remove">how</a>); your files stay</li>
        </ul>
      </div>
      <div class="go">
        <a class="btn" href="editor/">__ICON_PLAY__Open the editor</a>
        <a class="btn ghost" href="#install">Or install it yourself</a>
      </div>
    </div>
  </aside>

  <section id="install" aria-labelledby="h-install">
    <h2 id="h-install">Quick start <a class="anchor" href="#install" aria-label="Link to Quick start">#</a></h2>
    <p class="lead">Ways to get it: one small tool that fetches everything (uv or pixi), or pip. Nothing to install at all: open a tutorial in Google Colab.</p>
    <div class="tabs" role="tablist" aria-label="Ways to install">
      <button role="tab" id="tab-uv" aria-controls="p-uv" aria-selected="true">uv (recommended)</button>
      <button role="tab" id="tab-pixi" aria-controls="p-pixi" aria-selected="false" tabindex="-1">pixi</button>
      <button role="tab" id="tab-pip" aria-controls="p-pip" aria-selected="false" tabindex="-1">pip: prebuilt wheel</button>
      <button role="tab" id="tab-src" aria-controls="p-src" aria-selected="false" tabindex="-1">pip: from source</button>
    </div>
    <div class="tabpanel" role="tabpanel" id="p-pixi" aria-labelledby="tab-pixi" hidden>
      <div class="os" role="group" aria-label="Your system">
        <button data-os="unix" aria-pressed="true">Linux / macOS</button><button data-os="win" aria-pressed="false">Windows</button>
      </div>
      <div data-for="unix">
        <div class="code"><pre><code>curl -fsSL https://pixi.sh/install.sh | bash   <span class="c"># installs pixi, once</span>
export PATH="$HOME/.pixi/bin:$PATH"            <span class="c"># use it in this terminal (new terminals have it)</span>
git clone __GH__ &amp;&amp; cd pyauto-xpp
pixi run lab        <span class="c"># JupyterLab with the tutorials opens in your browser</span>
pixi run examples   <span class="c"># every worked-example notebook, one line each</span>
pixi run test       <span class="c"># the package's tests</span></code></pre></div>
      </div>
      <div data-for="win" hidden>
        <div class="code"><pre><code>python -m pip install pyauto_xpp-__VER__-cp312-cp312-win_amd64.whl   <span class="c"># the wheel for your Python, from Releases</span>
python -m pip install matplotlib jupyterlab ipywidgets plotly anywidget jupytext
python tools/jupytext_default.py   <span class="c"># .py scripts open as notebooks</span>
jupyter lab         <span class="c"># in the unzipped repository folder</span></code></pre></div>
        <p class="note">On Windows use uv or the prebuilt wheel (Releases): building from source there needs
           the MinGW-w64 compiler (MSYS2), not Microsoft's.</p>
      </div>
      <p>The first run downloads Python and the packages and builds XPP's C library; after an update only what changed
         is downloaded again. No git? Take <a href="__GH__/archive/refs/heads/main.zip">the .zip</a>, unzip it and run
         <code>pixi run lab</code> in that folder.</p>
    </div>
    <div class="tabpanel" role="tabpanel" id="p-uv" aria-labelledby="tab-uv">
      <p>One small program, <a href="https://docs.astral.sh/uv/" target="_blank" rel="noopener">uv</a>, fetches Python,
         pyauto-xpp and the packages by itself, the same way on Linux, macOS and Windows. Nothing to download by hand:
         uv picks the right wheel for your computer from <a href="wheels/">the wheel list</a>.</p>
      <div class="os" role="group" aria-label="Your system">
        <button data-os="unix" aria-pressed="true">Linux / macOS</button><button data-os="win" aria-pressed="false">Windows</button>
      </div>
      <div data-for="unix">
        <div class="code"><pre><code>curl -LsSf https://astral.sh/uv/install.sh | sh   <span class="c"># installs uv, once (open a new terminal after)</span></code></pre></div>
      </div>
      <div data-for="win" hidden>
        <div class="code"><pre><code>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   <span class="c"># installs uv, once (open a new terminal after)</span></code></pre></div>
      </div>
      <div class="code"><pre><code>uv run --find-links https://zetaone.github.io/pyauto-xpp/wheels/ --with pyauto-xpp python -c "import pyxpp; print(pyxpp.__file__)"   <span class="c"># check</span>
uv run --find-links https://zetaone.github.io/pyauto-xpp/wheels/ --with pyauto-xpp --with matplotlib --with jupyterlab jupyter lab   <span class="c"># JupyterLab</span></code></pre></div>
      <p><b>The tutorials:</b> take <a href="__GH__/archive/refs/heads/main.zip">the .zip</a> (or <code>git clone __GH__</code>),
         unzip it, and run the JupyterLab line above in that folder.</p>
      <p class="muted">The first run downloads everything (a minute); after that uv reuses its cache and starts in about a second.
         Add <code>--python 3.12</code> to choose the Python version. In a project of your own:
         <code>uv add pyauto-xpp --find-links https://zetaone.github.io/pyauto-xpp/wheels/</code>.</p>
    </div>
    <div class="tabpanel" role="tabpanel" id="p-pip" aria-labelledby="tab-pip" hidden>
      <p>We suggest a fresh conda environment, so pyauto-xpp and its packages stay apart from everything else.
         Install conda once, with either
         <a href="https://www.anaconda.com/docs/getting-started/miniconda/install" target="_blank" rel="noopener">Miniconda</a>
         (small: conda and Python only) or
         <a href="https://www.anaconda.com/download" target="_blank" rel="noopener">Anaconda</a>
         (large: with many scientific packages). The commands are the same for both; on Windows type them in the
         <b>Anaconda Prompt</b>, on Linux and macOS in a terminal.</p>
      <div class="code"><pre><code>conda create -n pyxpp python=3.12 -y      <span class="c"># once: a new environment called pyxpp</span>
conda activate pyxpp                      <span class="c"># every time you use it</span></code></pre></div>
      <p>Then download the wheel for your system and Python version from the <a href="__GH__/releases/latest">Releases page</a>
         (see <a href="#downloads">Downloads</a> below) and install it with the tutorial packages:</p>
      <div class="code"><pre><code>python -m pip install pyauto_xpp-__VER__-cp312-cp312-<span class="c">&lt;your system&gt;</span>.whl
python -m pip install matplotlib jupyterlab ipywidgets plotly anywidget jupytext
python -c "import pyxpp; print(pyxpp.__file__)"   <span class="c"># check</span>
jupyter lab                                       <span class="c"># open the tutorials</span></code></pre></div>
      <p class="muted"><code>cp312</code> is Python 3.12: pick the wheel whose tag matches <code>python --version</code>
         (cp39 to cp315). Linux x86_64 and ARM (glibc 2.28+), macOS Apple Silicon (11+) and Intel (10.9+ up to
         Python 3.11, 10.13+ for 3.12-3.13, 10.15+ for 3.14-3.15), Windows x86_64.</p>
    </div>
    <div class="tabpanel" role="tabpanel" id="p-src" aria-labelledby="tab-src" hidden>
      <p>Builds XPP's C library on your computer, so it needs a C compiler (gcc or clang).</p>
      <div class="code"><pre><code>git clone __GH__ &amp;&amp; cd pyauto-xpp
python -m pip install .            <span class="c"># or: pip install ".[plot]" for matplotlib too</span>
python -m pytest -q tests          <span class="c"># optional: the tests (needs pytest)</span></code></pre></div>
    </div>

    <h3 style="margin-top:22px">A first look</h3>
    <div class="code"><pre><code>import pyxpp
from pyxpp.builder import ModelBuilder

mb = (ModelBuilder("fhn")
      .ode("v", "v-v^3/3-w+i").ode("w", "eps*(v+a-b*w)")
      .parameter(i=0.2, a=0.7, b=0.8, eps=0.08).initial(v=-1.2, w=-0.6))
m = mb.load()
tr = m.run(total=200)                         <span class="c"># Initialconds &gt; Go</span>
m.equilibrium({"v": -1.2, "w": -0.6})         <span class="c"># Newton + eigenvalues</span>
m.run(total=300); m.run_last()
d = m.auto.run("i", start="steady", ds=0.01, parmin=0, parmax=2)   <span class="c"># AUTO</span>
d.special("HB")</code></pre></div>
  </section>

  <section id="downloads" aria-labelledby="h-downloads">
    <h2 id="h-downloads">Downloads <a class="anchor" href="#downloads" aria-label="Link to Downloads">#</a></h2>
    <p class="lead">Prebuilt wheels of v__VER__ are on the Releases page, one per system and Python version (3.9 to 3.15).</p>
    <div class="dl">__DOWNLOADS__</div>
  </section>

  <section id="tutorials" aria-labelledby="h-tutorials">
    <h2 id="h-tutorials">Tutorials <a class="anchor" href="#tutorials" aria-label="Link to Tutorials">#</a></h2>
    <p class="lead">__NS__ worked examples in seven notebooks, one per level, from first steps to AUTO on delay equations:
      each model with its equations, step-by-step explanations and checks against exact or published values. And
      __NN__ interactive notebooks with sliders and an AUTO panel. Notebooks use <a href="__RAW__tutorials/notebooks/xpptut.py" data-dl>xpptut.py</a>
      from their folder: download it with them, or take <a href="__GH__/archive/refs/heads/main.zip">everything (.zip)</a>.</p>
    <div class="filters" role="search">
      <div class="row">
        <label class="search"><span class="vh">Search tutorials</span>
          <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          <input type="search" id="q" placeholder="Search: Hopf, delay, map, Lorenz..." autocomplete="off"></label>
        <div class="chips" role="group" aria-label="Kind" id="kinds"></div>
        <span class="count" id="count" aria-live="polite"></span>
      </div>
      <div class="chips" role="group" aria-label="Group" id="groups"></div>
    </div>
    <div class="cards" id="cards"></div>
  </section>

  <section id="isochrons" aria-labelledby="h-isochrons">
    <h2 id="h-isochrons">Isochrons <a class="anchor" href="#isochrons" aria-label="Link to Isochrons">#</a></h2>
    <p class="lead">An oscillator's phase, extended off its limit cycle: the isochrons are the curves of equal
      asymptotic phase. These notebooks start from the idea and lead to the global isochrons of the reduced
      Hodgkin&ndash;Huxley neuron by continuation, as in Osinga &amp; Moehlis, SIAM J. Appl. Dyn. Syst. 9 (2010).
      In Google Colab the first cell installs pyauto-xpp; run it first. Locally: <code>pixi run isochrons</code>.</p>
    <div class="cards">
      <article class="card iso">
        <img src="isochrons/fhn_phase_map_isochrons.png" width="936" height="676" loading="lazy"
             alt="FitzHugh-Nagumo phase map with the isochrons theta = 0, 0.1, ..., 0.9 and the limit cycle">
        <div class="k"><span class="nb">notebook</span><span>&middot;</span><span>Isochrons 01</span></div>
        <h3>What is an isochron? FitzHugh&ndash;Nagumo, then the reduced Hodgkin&ndash;Huxley neuron</h3>
        <p>Phase on the cycle, asymptotic phase, the phase map and its contour lines, points on one isochron moving
          together, kicks and the phase response curve; then why the reduced HH isochrons need continuation.</p>
        <div class="f mono">01_FHN_basics-isochron.ipynb</div>
        <div class="links">
          <a href="__GH__/blob/main/isochrons/01_FHN_basics-isochron.ipynb" aria-label="View 01_FHN_basics-isochron.ipynb on GitHub">View</a>
          <a href="__RAW__isochrons/01_FHN_basics-isochron.ipynb" data-dl aria-label="Download 01_FHN_basics-isochron.ipynb">Download</a>
          <a href="https://colab.research.google.com/github/ZetaOne/pyauto-xpp/blob/main/isochrons/01_FHN_basics-isochron.ipynb" target="_blank" rel="noopener" aria-label="Open 01_FHN_basics-isochron.ipynb in Google Colab">Open in Colab</a>
        </div>
      </article>
      <article class="card iso">
        <img src="isochrons/fhn_100_isochrons.png" width="850" height="630" loading="lazy"
             alt="One hundred FitzHugh-Nagumo isochrons computed by continuation, coloured by phase">
        <div class="k"><span class="nb">notebook</span><span>&middot;</span><span>Isochrons 02</span></div>
        <h3>One hundred FitzHugh&ndash;Nagumo isochrons by continuation</h3>
        <p>The method of Osinga &amp; Moehlis on FitzHugh&ndash;Nagumo: each isochron as a family of orbit segments of a
          boundary value problem, continued in AUTO stage by stage with the concatenation; checked against the
          brute-force phase.</p>
        <div class="f mono">02_FHN_isochrons-by-continuation.ipynb</div>
        <div class="links">
          <a href="__GH__/blob/main/isochrons/02_FHN_isochrons-by-continuation.ipynb" aria-label="View 02_FHN_isochrons-by-continuation.ipynb on GitHub">View</a>
          <a href="__RAW__isochrons/02_FHN_isochrons-by-continuation.ipynb" data-dl aria-label="Download 02_FHN_isochrons-by-continuation.ipynb">Download</a>
          <a href="https://colab.research.google.com/github/ZetaOne/pyauto-xpp/blob/main/isochrons/02_FHN_isochrons-by-continuation.ipynb" target="_blank" rel="noopener" aria-label="Open 02_FHN_isochrons-by-continuation.ipynb in Google Colab">Open in Colab</a>
        </div>
      </article>
      <article class="card iso">
        <img src="isochrons/hh_100_isochrons.png" width="850" height="630" loading="lazy"
             alt="One hundred isochrons of the reduced Hodgkin-Huxley model computed by continuation, coloured by phase">
        <div class="k"><span class="nb">notebook</span><span>&middot;</span><span>Isochrons 03</span></div>
        <h3>One hundred reduced Hodgkin&ndash;Huxley isochrons by continuation (the paper's Figure 2)</h3>
        <p>The same code on the model of Osinga &amp; Moehlis: boundary value problems continued in AUTO up to the
          time-4T map; the 0-phase isochron live, the others from stored results; checked against the brute-force
          phase and its almost phaseless set.</p>
        <div class="f mono">03_HH_isochrons-by-continuation.ipynb</div>
        <div class="links">
          <a href="__GH__/blob/main/isochrons/03_HH_isochrons-by-continuation.ipynb" aria-label="View 03_HH_isochrons-by-continuation.ipynb on GitHub">View</a>
          <a href="__RAW__isochrons/03_HH_isochrons-by-continuation.ipynb" data-dl aria-label="Download 03_HH_isochrons-by-continuation.ipynb">Download</a>
          <a href="https://colab.research.google.com/github/ZetaOne/pyauto-xpp/blob/main/isochrons/03_HH_isochrons-by-continuation.ipynb" target="_blank" rel="noopener" aria-label="Open 03_HH_isochrons-by-continuation.ipynb in Google Colab">Open in Colab</a>
        </div>
      </article>
    </div>
  </section>

  <section id="thanks" aria-labelledby="h-thanks">
    <h2 id="h-thanks">Thank you, Prof. Ermentrout <a class="anchor" href="#thanks" aria-label="Link to Thank you, Prof. Ermentrout">#</a></h2>
    <p><a href="https://sites.pitt.edu/~phase/" target="_blank" rel="noopener">Bard Ermentrout</a>'s <a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a>
       and his book <a href="https://doi.org/10.1137/1.9780898718195" target="_blank" rel="noopener"><i>Simulating,
       Analyzing, and Animating Dynamical Systems</i></a> have taught many of us how to explore dynamical systems.
       Every number on this page comes from his code. <b>Thank you, Prof. Ermentrout.</b></p>
  </section>

  <section id="xpp-web" aria-labelledby="h-sister">
    <h2 id="h-sister">Sister project <a class="anchor" href="#xpp-web" aria-label="Link to Sister project">#</a></h2>
    <a class="sister" href="__SISTER__" target="_blank" rel="noopener">
      <img class="logo" src="xppaut-web.png" alt="XPPAUT-Web logo" width="96" height="96">
      <div><b>XPPAUT-Web</b><p>The full XPPAUT 8.4, with its own windows, menus and AUTO, right in your browser
        and as an Android app. Nothing to install: open a model and start exploring.</p></div>
      <span class="btn">Try XPPAUT-Web &rarr;</span>
    </a>
    <a class="sister mini" href="__BOOK__" target="_blank" rel="noopener">
      <img class="logo" src="notebook.png" alt="" width="28" height="28">
      <div><b>notebook</b><p>A book, slide decks, code and a study kit on the global isochrons of Osinga &amp; Moehlis (2010).</p></div>
      <span class="btn">Open the book &rarr;</span>
    </a>
  </section>
</div>
</main>

<footer>
  <div class="wrap">
    <b style="color:var(--fg)">Credits</b>
    <ul>
      <li><b><a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a></b> is by <a href="https://sites.pitt.edu/~phase/" target="_blank" rel="noopener">G. Bard Ermentrout</a>; the C sources are his version 8.4, including AUTO for delay equations.</li>
      <li><b>AUTO</b> is by E. Doedel and collaborators.</li>
      <li><b>pyxpp</b>, the headless Python bridge this package grew from, is by Youngmin Park.</li>
      <li><b>The tutorial models</b> come from the examples of <a href="https://xpp-studio.github.io/xpp-studio/" target="_blank" rel="noopener">XPP Studio</a> (Peter Ashwin and Bard Ermentrout, GPL-3.0) and from
        the delay-equation examples that come with XPPAUT 8.2.</li>
    </ul>
    <p class="madeby">Made by <a href="https://github.com/ZetaOne" target="_blank" rel="noopener">Jeevan Kumar Gochhayat</a>.</p>
    <div class="row">
      <span>Licence: GPL-3.0-or-later.</span>
      <a href="__GH__">Source</a><a href="__GH__/releases">Releases</a><a href="__GH__/blob/main/CHANGES.md">Changes</a>
      <a href="__GH__/issues">Report a problem</a><a href="https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html" target="_blank" rel="noopener">XPPAUT</a><a href="__SISTER__" target="_blank" rel="noopener">XPPAUT-Web</a>
    </div>
  </div>
</footer>

<dialog class="lightbox" id="lightbox" aria-labelledby="lb-title">
  <img id="lb-img" alt="">
  <div class="lb-bar">
    <button class="iconbtn" id="lb-prev" aria-label="Previous figure">&#8249;</button>
    <button class="iconbtn" id="lb-next" aria-label="Next figure">&#8250;</button>
    <div class="t"><b id="lb-title"></b> <span id="lb-cap"></span></div>
    <a class="btn ghost" id="lb-src">The script</a>
    <button class="iconbtn" id="lb-close" aria-label="Close">&#215;</button>
  </div>
</dialog>

<script>
__DISPLAY_JS__
</script>
<script>
const ITEMS = __ITEMS__, SHOTS = __SHOTS__;
const GH = "__GH__", RAW = "__RAW__";
const $ = id => document.getElementById(id);
const root = document.documentElement;

// themes, text size, font and the toolbar menus: DISPLAY_JS (the script above, shared with the manual)
for (const a of document.querySelectorAll('#menu .panel a')) a.addEventListener('click', () => { $('menu').open = false });

// the section links fold into the menu when they wrap (large text, a wide font, a narrow window)
{
  const bar = document.querySelector('.bar'), nav = document.querySelector('.nav');
  const fit = () => {
    bar.classList.remove('fold');
    if (getComputedStyle(nav).display === 'none') return;
    const a = nav.querySelector('a');
    if (nav.offsetHeight > a.offsetHeight * 1.5 || bar.scrollWidth > bar.clientWidth + 1) bar.classList.add('fold');
  };
  addEventListener('resize', fit); document.addEventListener('pyx-display', fit);
  if (document.fonts) document.fonts.ready.then(fit);
  fit();
}

// the section in view is marked in the toolbar
{
  const links = [...document.querySelectorAll('.nav a[href^="#"]')];
  const obs = new IntersectionObserver(es => {
    for (const e of es) if (e.isIntersecting)
      for (const a of links) a.setAttribute('aria-current', String(a.getAttribute('href') === '#' + e.target.id));
  }, { rootMargin: '-45% 0px -50% 0px' });
  for (const a of links) { const s = document.querySelector(a.getAttribute('href')); if (s) obs.observe(s) }
}

// ---- quick start: tabs (arrow keys as in a tab list) and the system choice ----
{
  const tabs = [...document.querySelectorAll('[role=tab]')];
  const pick = (t, focus) => {
    for (const o of tabs) {
      const on = o === t;
      o.setAttribute('aria-selected', String(on)); o.tabIndex = on ? 0 : -1;
      $(o.getAttribute('aria-controls')).hidden = !on;
    }
    if (focus) t.focus();
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => pick(t));
    t.addEventListener('keydown', e => {
      const j = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (j !== undefined) { e.preventDefault(); pick(tabs[(j + tabs.length) % tabs.length], true) }
    });
  });
  const setOs = os => {
    for (const b of document.querySelectorAll('.os button')) b.setAttribute('aria-pressed', String(b.dataset.os === os));
    for (const el of document.querySelectorAll('[data-for]')) el.hidden = el.dataset.for !== os;
  };
  for (const b of document.querySelectorAll('.os button')) b.addEventListener('click', () => setOs(b.dataset.os));
  const plat = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
  setOs(/win/i.test(plat) ? 'win' : 'unix');
}

// ---- copy buttons on the commands ------------------------------------------------
for (const pre of document.querySelectorAll('.code pre')) {
  const b = document.createElement('button');
  b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy';
  b.setAttribute('aria-label', 'Copy these commands');
  b.addEventListener('click', async () => {
    const text = pre.innerText.replace(/[ \t]+#[^\n]*/g, '').replace(/[ \t]+$/gm, '');
    try { await navigator.clipboard.writeText(text); b.textContent = 'Copied' }
    catch (e) { b.textContent = 'Select and copy' }
    setTimeout(() => { b.textContent = 'Copy' }, 1600);
  });
  pre.parentNode.append(b);
}

// ---- downloads of single files (GitHub would show them as text) ---------------
async function download(a, e) {
  e.preventDefault();
  const name = a.href.split('/').pop();
  try {
    const r = await fetch(a.href);
    if (!r.ok) throw new Error(r.status);
    const url = URL.createObjectURL(await r.blob());
    const t = document.createElement('a'); t.href = url; t.download = name; document.body.append(t); t.click(); t.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  } catch (err) { location.href = a.href }
}
document.addEventListener('click', e => { const a = e.target.closest('a[data-dl]'); if (a) download(a, e) });

// ---- tutorials: kind and group chips, search ---------------------------------------
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const state = { kind: '', group: '' };
function chips(box, key, opts) {
  box.innerHTML = opts.map(([v, label]) => '<button type="button" class="chip" data-v="' + esc(v) + '" aria-pressed="' +
    (state[key] === v) + '">' + esc(label) + ' <small>' + ITEMS.filter(i => !v || i[key] === v).length + '</small></button>').join('');
  for (const b of box.querySelectorAll('button')) b.addEventListener('click', () => {
    state[key] = b.dataset.v;
    for (const o of box.querySelectorAll('button')) o.setAttribute('aria-pressed', String(o === b));
    draw();
  });
}
chips($('kinds'), 'kind', [['', 'All'], ['example', 'Worked examples'], ['notebook', 'Interactive notebooks']]);
chips($('groups'), 'group', [['', 'All groups'], ...[...new Set(ITEMS.map(i => i.group))].map(g => [g, g])]);
function card(i) {
  const name = i.file.split('/').pop();
  return '<article class="card"><div class="k"><span class="' + (i.kind === 'notebook' ? 'nb' : '') + '">' + i.kind +
    '</span><span>&middot;</span><span>' + esc(i.group) + '</span></div><h3>' + esc(i.title) + '</h3><p>' + esc(i.what) +
    '</p><div class="f mono">' + esc(name) + '</div><div class="links">' +
    '<a href="' + GH + '/blob/main/' + i.file + '" aria-label="View ' + esc(name) + ' on GitHub">View</a>' +
    '<a href="' + RAW + i.file + '" data-dl aria-label="Download ' + esc(name) + '">Download</a>' +
    (i.kind === 'example' ? '<a href="editor/?open=' + encodeURIComponent(i.file) + '" aria-label="Run ' + esc(name) + ' in the editor">Run in editor</a>' : '') +
    '<a href="https://colab.research.google.com/github/ZetaOne/pyauto-xpp/blob/main/' + i.file + '" target="_blank" rel="noopener" ' +
    'aria-label="Open ' + esc(name) + ' in Google Colab">Open in Colab</a></div></article>';
}
function draw() {
  const words = $('q').value.toLowerCase().split(/\s+/).filter(Boolean);
  const sel = ITEMS.filter(i => (!state.kind || i.kind === state.kind) && (!state.group || i.group === state.group) &&
    words.every(w => (i.title + ' ' + i.what + ' ' + i.file + ' ' + i.group).toLowerCase().includes(w)));
  $('count').textContent = sel.length + ' of ' + ITEMS.length;
  $('cards').innerHTML = sel.length ? sel.map(card).join('')
    : '<div class="empty">No tutorial matches. <button type="button" id="clear">Show all</button></div>';
  $('clear')?.addEventListener('click', () => {
    $('q').value = ''; state.kind = state.group = '';
    for (const b of document.querySelectorAll('.chips button')) b.setAttribute('aria-pressed', String(b.dataset.v === ''));
    draw();
  });
}
$('q').addEventListener('input', draw);
draw();

// ---- gallery lightbox (Esc closes, arrows step) ------------------------------------
{
  const dlg = $('lightbox'); let at = 0;
  const show = k => {
    at = (k + SHOTS.length) % SHOTS.length; const s = SHOTS[at];
    $('lb-img').src = s.src; $('lb-img').alt = s.title + ': ' + s.cap;
    $('lb-title').textContent = s.title; $('lb-cap').textContent = s.cap;
    $('lb-src').href = GH + '/blob/main/' + s.file;
  };
  for (const b of document.querySelectorAll('.shot button')) b.addEventListener('click', () => {
    show(+b.dataset.i); if (dlg.showModal) dlg.showModal(); else location.href = SHOTS[at].src;
  });
  $('lb-prev').onclick = () => show(at - 1); $('lb-next').onclick = () => show(at + 1);
  $('lb-close').onclick = () => dlg.close();
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close() });
  dlg.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') show(at - 1); else if (e.key === 'ArrowRight') show(at + 1);
  });
}
</script>
<script>
  // the logo beside the intro is as tall as the text next to it (desktop layout only)
  (function () {
    var m = document.querySelector('.hero img.mark'), t = document.querySelector('.hero .wrap > div');
    if (!m || !t || !window.ResizeObserver) return;
    function fit() {
      if (window.innerWidth <= 760) { m.style.width = m.style.height = ''; return; }
      var h = Math.round(Math.min(Math.max(t.offsetHeight, 110), 280));
      m.style.width = m.style.height = h + 'px';
    }
    new ResizeObserver(fit).observe(t); window.addEventListener('resize', fit); fit();
  })();
</script>
</body>
</html>
"""

ICON_PLAY = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">'
             '<path d="M8 5v14l11-7z" fill="currentColor"/></svg>')
ICON_GH = ('<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 '
           '3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-'
           '.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-'
           '1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-'
           '.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-'
           '1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-'
           '3.58-8-8-8z"/></svg>')

NAV = [("#gallery", "Gallery"), ("#install", "Quick start"), ("#downloads", "Downloads"),
       ("#tutorials", "Tutorials"), ("#isochrons", "Isochrons"), ("manual/", "Manual"), ("editor/", "Editor")]


def downloads():
    rel = f"{GH}/releases/latest"
    rows = [
        ("Linux x86_64", "ends in <span class=mono>x86_64.whl</span>", rel, ""),
        ("Linux ARM", "ends in <span class=mono>aarch64.whl</span>", rel, ""),
        ("macOS Intel", "10.9+ (10.13+ / 10.15+ for newer Pythons), <span class=mono>x86_64.whl</span>", rel, ""),
        ("macOS Apple Silicon", "11 or newer, <span class=mono>arm64.whl</span>", rel, ""),
        ("Windows x86_64", "ends in <span class=mono>win_amd64.whl</span>", rel, ""),
        ("Everything (.zip)", "package, C sources, tutorials, tests", f"{GH}/archive/refs/heads/main.zip", ""),
        ("Release notes and all files", "Releases page on GitHub", f"{GH}/releases", ""),
    ]
    return "".join(f'<a class="box{c}" href="{h}"><b>{t}</b><span>{s}</span></a>' for t, s, h, c in rows)


def build(out):
    items = tutorials(out)
    ver = re.search(r'^version = "([^"]+)"', (out / "pyproject.toml").read_text(), re.M).group(1)
    site = out / "site"
    if site.exists():
        shutil.rmtree(site)
    site.mkdir()

    # the editor: the page ships inside the package (pyxpp serve also serves it), the installers are here
    ed = site / "editor"
    ed.mkdir()
    shutil.copy2(out / "pyxpp" / "editor" / "index.html", ed / "index.html")
    for f in ("install.sh", "install.ps1", "install-pyxpp.bat"):
        shutil.copy2(Path(__file__).resolve().parent / "editor" / f, ed / f)

    # icons and web manifest
    (site / "icon.svg").write_text(mark_svg())
    manual(site)
    from PIL import Image as _I
    _I.open(Path.home() / "Downloads" / "XPPAUT-Web" / "public" / "icon-512.png").resize((192, 192), _I.LANCZOS).save(site / "xppaut-web.png")
    shutil.copy2(BOOK_ICON, site / "notebook.png")
    for name, size, mask in (("favicon-32.png", 32, False), ("apple-touch-icon.png", 180, True),
                             ("icon-192.png", 192, False), ("icon-512.png", 512, False),
                             ("icon-maskable-512.png", 512, True)):
        mark_png(site / name, size, mask)
    (site / "manifest.webmanifest").write_text(json.dumps({
        "name": "pyauto-xpp", "short_name": "pyauto-xpp",
        "description": "XPPAUT 8.4 and its AUTO as a Python module, with tutorials.",
        "start_url": "./", "scope": "./", "display": "browser",
        "background_color": "#1d3150", "theme_color": "#1d3150",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
                  {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1) + "\n")

    (site / "isochrons").mkdir()                    # preview animation of the Isochrons section
    shutil.copy2(out / "isochrons" / "figures" / "fhn_phase_map_isochrons.png", site / "isochrons" / "fhn_phase_map_isochrons.png")
    shutil.copy2(out / "isochrons" / "fhn_100_isochrons.png", site / "isochrons" / "fhn_100_isochrons.png")
    shutil.copy2(out / "isochrons" / "hh_100_isochrons.png", site / "isochrons" / "hh_100_isochrons.png")
    shots = gallery(site)
    gal = "".join(
        f'<figure class="shot"><button type="button" data-i="{k}" aria-label="Enlarge: {html.escape(s["title"])}">'
        f'<img src="{s["src"]}" width="{s["w"]}" height="{s["h"]}" loading="lazy" '
        f'alt="{html.escape(s["title"] + ": " + s["cap"])}"></button>'
        f'<figcaption><b>{html.escape(s["title"])}</b>{html.escape(s["cap"])} '
        f'<a href="{GH}/blob/main/{s["file"]}">Script</a></figcaption></figure>'
        for k, s in enumerate(shots))

    page = PAGE
    for k, v in {
        # the Display panel (shared with the manual) first: its pieces hold no placeholders
        "__DISPLAY_HEAD__": display_head(), "__TOOLBAR_CSS__": TOOLBAR_CSS, "__DISPLAY_CSS__": DISPLAY_CSS,
        "__DISPLAY_BUTTON__": DISPLAY_BUTTON, "__DISPLAY_JS__": display_js(),
        "__THEMES__": theme_css(),
        "__ITEMS__": json.dumps(items),
        "__SHOTS__": json.dumps(shots),
        "__GALLERY__": gal,
        "__DOWNLOADS__": downloads(),
        "__NAV__": "".join(f'<a href="{h}">{t}</a>' for h, t in NAV),
        "__NAVMENU__": "".join(f'<a role="menuitem" href="{h}">{t}</a>' for h, t in NAV)
                       + f'<a role="menuitem" href="{GH}">GitHub</a>',
        "__ICON_PLAY__": ICON_PLAY, "__ICON_GH__": ICON_GH,
        "__OGIMAGE__": f"https://zetaone.github.io/pyauto-xpp/{shots[0].get('poster', shots[0]['src'])}" if shots else "",
        "__NS__": str(sum(i["kind"] == "example" for i in items)),
        "__NN__": str(sum(i["kind"] == "notebook" for i in items)),
        "__N__": str(len(items)), "__VER__": ver,
        "__GH__": GH, "__RAW__": RAW, "__SISTER__": SISTER, "__BOOK__": BOOK,
    }.items():
        page = page.replace(k, v)
    left = re.findall(r"__[A-Z_]+__", page)
    assert not left, left
    (site / "index.html").write_text(page)
    return len(items), len(theme_list())
