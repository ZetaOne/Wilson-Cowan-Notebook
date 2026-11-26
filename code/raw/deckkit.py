"""Shared helpers for the Wilson–Cowan chapter decks (ManimGX + Manim Slides via sciviz).

Each chapter deck is one Scene in scripts/wilson-cowan/decks/chNN.py, rendered with
    .venv/bin/python -m sciviz render wc-chNN scripts/wilson-cowan/decks/chNN.py DeckNN
    .venv/bin/python -m sciviz deck wc-chNN --offline
Data come from rendered-anims/wilson-cowan/data/*.npz (written by scripts/wilson-cowan/figs/*.py, computed with
XPPAUT through pyauto-xpp); book figures come from rendered-anims/wilson-cowan/book/figs/*.png.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

import manimgx as m
from sciviz.manim import Slides

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "rendered-anims" / "wilson-cowan" / "data"
FIGS = ROOT / "rendered-anims" / "wilson-cowan" / "book" / "figs"

# palette (matches the book figures, brightened for a dark background)
INK = m.WHITE
MUTED = m.GREY_B
TEAL = m.ManimColor("#2ec4c9")
MAGENTA = m.ManimColor("#e0559a")
ORANGE = m.ManimColor("#f0a040")
BLUE = m.ManimColor("#5b9cf0")
GREEN = m.ManimColor("#59c36a")
RED = m.ManimColor("#ef5b5b")
YELLOW = m.YELLOW
PHASE = [m.ManimColor(c) for c in ("#00b7c7", "#4a6fd6", "#9a3fc4", "#e0339a")]

BEAT, HOLD, LONG = 1.5, 3.0, 4.5


def data(name: str) -> dict:
    return dict(np.load(DATA / f"{name}.npz", allow_pickle=True))


def phase_color(c: float) -> m.ManimColor:
    """cyan -> blue -> purple -> magenta, the book's isochron colours."""
    c = float(c) % 1.0
    x = c * (len(PHASE) - 1)
    i = min(int(x), len(PHASE) - 2)
    return m.interpolate_color(PHASE[i], PHASE[i + 1], x - i)


def tex(*parts: str, font_size: float = 40, **kw) -> m.MathTex:
    safe = [p.replace("{{", "{ {").replace("}}", "} }") for p in parts]
    return m.MathTex(*safe, font_size=font_size, **kw)


def prose(text: str, font_size: float = 28, color=INK, width: float | None = None) -> m.VGroup:
    """Left-aligned lines that may contain $maths$ (lines split at \\n)."""
    lines = [m.Tex(line, font_size=1.3 * font_size, color=color) for line in text.split("\n")]
    g = m.VGroup(*lines).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.14)
    if width and g.width > width:
        g.scale_to_fit_width(width)
    return g


def heading(text: str, font_size: float = 38) -> m.Mobject:
    if "$" in text:
        t = m.Tex(r"\textbf{" + text + "}", font_size=1.25 * font_size).to_edge(m.UP, buff=0.35)
    else:
        t = m.Text(text, font_size=font_size, weight=m.BOLD).to_edge(m.UP, buff=0.35)
    if t.width > 13.2:
        t.scale_to_fit_width(13.2)
    return t


def pt(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


def figure_card(name: str, height: float = 5.6, at=pt(0, -0.35)) -> m.Group:
    """A book figure (PNG, white background) on a rounded card."""
    path = FIGS / f"{name}.png"
    if not path.exists():
        path = FIGS / f"{name}_still.png"
    im = m.ImageMobject(str(path))
    im.scale_to_fit_height(height)
    if im.width > 13.2:
        im.scale_to_fit_width(13.2)
    im.move_to(at)
    card = m.RoundedRectangle(width=im.width + 0.25, height=im.height + 0.25, corner_radius=0.12,
                              fill_color=m.WHITE, fill_opacity=1, stroke_width=0).move_to(im)
    return m.Group(card, im)


def plane(xr, yr, width=7.0, height=5.0, at=pt(0, -0.4), xlabel="x", ylabel="y", ticks=True) -> m.Axes:
    ax = m.Axes(x_range=xr, y_range=yr, x_length=width, y_length=height, tips=False,
                axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False, "include_numbers": False,
                             "font_size": 26})
    ax.move_to(at)
    if ticks:
        # numbered axes: hide the axes through the origin and draw a frame along the left and bottom edges
        for a in (ax.x_axis, ax.y_axis):
            a.set_opacity(0)
        x0, x1, dx = xr[:3]; y0, y1, dy = yr[:3]
        frame = m.VGroup(m.Line(ax.c2p(x0, y0), ax.c2p(x1, y0), color=MUTED, stroke_width=2),
                         m.Line(ax.c2p(x0, y0), ax.c2p(x0, y1), color=MUTED, stroke_width=2))
        def fmt(v):
            return f"{v:g}"
        for v in np.arange(x0, x1 + 1e-9, dx):
            frame.add(m.Line(ax.c2p(v, y0), ax.c2p(v, y0) + np.array([0, -0.08, 0]), color=MUTED, stroke_width=2))
            frame.add(m.MathTex(fmt(round(v, 6)), font_size=24, color=MUTED).next_to(ax.c2p(v, y0), m.DOWN, buff=0.15))
        for v in np.arange(y0, y1 + 1e-9, dy):
            frame.add(m.Line(ax.c2p(x0, v), ax.c2p(x0, v) + np.array([-0.08, 0, 0]), color=MUTED, stroke_width=2))
            frame.add(m.MathTex(fmt(round(v, 6)), font_size=24, color=MUTED).next_to(ax.c2p(x0, v), m.LEFT, buff=0.15))
        ax.add(frame)
        lx = m.MathTex(xlabel, font_size=40, color=MUTED).next_to(ax.c2p(x1, y0), m.RIGHT, buff=0.55)
        ly = m.MathTex(ylabel, font_size=40, color=MUTED).next_to(ax.c2p(x0, y1), m.UP, buff=0.2)
        ax.add(lx, ly)
        return ax
    lx = m.MathTex(xlabel, font_size=40, color=MUTED).next_to(ax.x_axis.get_end(), m.RIGHT, buff=0.2)
    ly = m.MathTex(ylabel, font_size=40, color=MUTED).next_to(ax.y_axis.get_end(), m.UP, buff=0.2)
    ax.add(lx, ly)
    return ax


def curve(ax: m.Axes, X: np.ndarray, color=INK, width: float = 3.0, step: int = 1) -> m.VMobject:
    X = np.asarray(X, float)[::step]
    X = X[np.all(np.isfinite(X), axis=1)]
    pts = [ax.c2p(x, y) for x, y in X]
    v = m.VMobject(color=color, stroke_width=width)
    v.set_points_as_corners(pts) if len(pts) > 1 else None
    return v


def dot(ax: m.Axes, p, color=INK, r: float = 0.07) -> m.Dot:
    return m.Dot(ax.c2p(*p), radius=r, color=color)


def cite(text: str) -> m.Text:
    return m.Text(text, font_size=18, color=m.GREY_C).to_corner(m.DR, buff=0.15)


class Deck(Slides, m.Scene):
    """Base: title card and helpers to step through slides."""
    chapter = "Chapter"
    title = ""
    subtitle = ""

    def title_card(self):
        k = m.Text(self.chapter.upper(), font_size=24, color=MAGENTA)
        t = m.Text(self.title, font_size=54, weight=m.BOLD)
        if t.width > 12.5:
            t.scale_to_fit_width(12.5)
        s = m.Text(self.subtitle, font_size=28, color=MUTED, slant=m.ITALIC)
        if s.width > 12.5:
            s.scale_to_fit_width(12.5)
        g = m.VGroup(k, t, s).arrange(m.DOWN, buff=0.35)
        line = m.Line(pt(-5, 0), pt(5, 0), color=TEAL, stroke_width=3).next_to(g, m.DOWN, buff=0.4)
        self.play(m.FadeIn(k, shift=m.DOWN * 0.2), m.Write(t), run_time=1.6)
        self.play(m.FadeIn(s), m.Create(line), run_time=1.0)
        self.wait(BEAT)
        self.next_slide(self.title)
        self.play(m.FadeOut(m.Group(k, t, s, line)), run_time=0.6)

    def clear(self, run_time: float = 0.6):
        if self.mobjects:
            self.play(*[m.FadeOut(mob) for mob in self.mobjects], run_time=run_time)

    def show_figure(self, name: str, title: str, caption: str = "", height: float = 5.6, notes: str = ""):
        if not (FIGS / f"{name}.png").exists() and not (FIGS / f"{name}_still.png").exists():
            print(f"[deck] figure {name} not built yet: slide skipped")
            return
        h = heading(title)
        card = figure_card(name, height=height, at=pt(0, -0.35 if not caption else -0.15))
        self.play(m.FadeIn(h), m.FadeIn(card, scale=0.97), run_time=1.0)
        if caption:
            c = prose(caption, font_size=22, color=MUTED, width=12.8).to_edge(m.DOWN, buff=0.18)
            self.play(m.FadeIn(c), run_time=0.6)
        self.wait(HOLD)
        self.next_slide(notes or title)
        self.clear()

    def bullets(self, title: str, items: list[str], font_size: float = 30, notes: str = ""):
        h = heading(title)
        self.play(m.FadeIn(h), run_time=0.6)
        rows = [prose("• " + it, font_size=font_size, width=12.4) for it in items]
        g = m.VGroup(*rows).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4).next_to(h, m.DOWN, buff=0.6)
        g.to_edge(m.LEFT, buff=0.8)
        for r in rows:
            self.play(m.FadeIn(r, shift=m.RIGHT * 0.2), run_time=0.7)
            self.wait(BEAT)
            self.next_slide(notes)
        self.clear()

    def recap(self, items: list[str]):
        self.bullets("What to carry forward", items, font_size=28, notes="recap")


# ---------------------------------------------------------------------------------------------------
# extra helpers for the Wilson–Cowan decks (geometry first)
import sys as _sys
_sys.path.insert(0, str(ROOT / "scripts" / "wilson-cowan"))


def wc():
    """the numerics library (pure-numpy parts: nullclines, vector field, steady-state curves)"""
    import wc_lib
    return wc_lib


def flow_arrows(ax: m.Axes, xs, F, y0: float = 0.0, color=ORANGE, scale: float = 0.22) -> m.VGroup:
    """Arrows along the x-axis showing the direction of x' = F(x) (phase line)."""
    g = m.VGroup()
    for x in xs:
        v = F(x)
        if abs(v) < 1e-9:
            continue
        p = ax.c2p(x, y0)
        g.add(m.Arrow(p, p + np.array([scale * np.sign(v), 0, 0]), buff=0, color=color, stroke_width=4,
                      max_tip_length_to_length_ratio=0.6))
    return g


def vfield(ax: m.Axes, F, xr, yr, n: int = 13, color=m.GREY_D, length: float = 0.32) -> m.VGroup:
    """Normalised direction field of a planar flow F(x, y) -> (u, v)."""
    g = m.VGroup()
    for x in np.linspace(xr[0], xr[1], n):
        for y in np.linspace(yr[0], yr[1], n):
            u, v = F(x, y)
            p0 = ax.c2p(x, y)
            d = ax.c2p(x + u, y + v) - p0
            L = np.linalg.norm(d)
            if L < 1e-12:
                continue
            g.add(m.Arrow(p0, p0 + d / L * length, buff=0, color=color, stroke_width=2, max_tip_length_to_length_ratio=0.35))
    return g


def image_from_array(A: np.ndarray, cmap: str = "magma", vmin=None, vmax=None, height: float = 4.0, origin_lower=True) -> m.ImageMobject:
    """Colour-map a 2-D array (rows = y) into an ImageMobject."""
    import matplotlib
    cm = matplotlib.colormaps[cmap]
    vmin = np.nanmin(A) if vmin is None else vmin
    vmax = np.nanmax(A) if vmax is None else vmax
    Z = np.clip((A - vmin) / (vmax - vmin + 1e-12), 0, 1)
    if origin_lower:
        Z = Z[::-1]
    rgba = (cm(Z) * 255).astype(np.uint8)
    im = m.ImageMobject(rgba)
    im.scale_to_fit_height(height)
    return im


class GeoDeck(Deck):
    """Deck with derivation steps and path tracing."""

    def steps(self, title: str, rows, eq_size: float = 40, note_size: float = 28, start_y: float = 2.0, gap: float = 1.15):
        """rows: list of (latex, explanation). Each row appears with its reason, one slide per row."""
        h = heading(title)
        self.play(m.FadeIn(h), run_time=0.6)
        y = start_y
        shown = []
        for latex, why in rows:
            if y < -2.6 and shown:                  # page full: clear and continue at the top
                self.play(*[m.FadeOut(x) for x in shown], run_time=0.5)
                shown = []
                y = start_y
            e = tex(latex, font_size=eq_size).move_to(pt(-1.6, y))
            if e.width > 8.2:
                e.scale_to_fit_width(8.2)
            e.to_edge(m.LEFT, buff=0.6)
            room = 6.9 - e.get_right()[0] - 0.5
            w = prose(why, font_size=note_size, color=YELLOW)
            if w.width <= room:
                w.next_to(e, m.RIGHT, buff=0.5)
            elif room >= 3.6 and w.width * 0.8 <= room:
                w.scale_to_fit_width(room).next_to(e, m.RIGHT, buff=0.5)
            else:                                   # not enough room beside it: put the reason underneath
                if w.width > 12.4:
                    w.scale_to_fit_width(12.4)
                w.next_to(e, m.DOWN, buff=0.12, aligned_edge=m.LEFT)
                y -= 0.45
            self.play(m.Write(e), run_time=1.0)
            self.play(m.FadeIn(w, shift=m.LEFT * 0.2), run_time=0.6)
            shown += [e, w]
            self.wait(BEAT)
            self.next_slide(why[:60])
            y -= gap
        self.wait(HOLD)
        self.clear()

    def trace(self, ax: m.Axes, X: np.ndarray, color=MAGENTA, run_time: float = 4.0, width: float = 3.0, r: float = 0.08):
        """Draw a trajectory progressively with a moving dot; returns the final path mobject."""
        X = np.asarray(X, float)
        k = m.ValueTracker(1)
        path = m.always_redraw(lambda: curve(ax, X[: max(2, int(k.get_value()))], color=color, width=width))
        d = m.always_redraw(lambda: dot(ax, X[min(len(X) - 1, int(k.get_value()))], color=color, r=r))
        self.add(path, d)
        self.play(k.animate.set_value(len(X) - 1), run_time=run_time, rate_func=m.linear)
        final = curve(ax, X, color=color, width=width)
        self.remove(path, d)
        self.add(final)
        return final


def rk4(F, x0, T: float, dt: float = 0.02) -> np.ndarray:
    """Integrate x' = F(x) (vectorised numpy F taking an array of shape (2,)) with RK4; returns (n, 2)."""
    n = int(T / dt)
    X = np.empty((n + 1, len(x0))); X[0] = x0
    x = np.array(x0, float)
    for k in range(n):
        k1 = F(x); k2 = F(x + dt / 2 * k1); k3 = F(x + dt / 2 * k2); k4 = F(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        X[k + 1] = x
    return X


def nullcline_curves(ax: m.Axes, pars: dict, emax: float = 0.49, n: int = 600, width: float = 4):
    """E-nullcline (green) and I-nullcline (red) of the WC pair as mobjects."""
    W = wc()
    q = dict(W.WC_OSC); q.update(pars)
    eg = np.linspace(0.0005, min(emax, W.wc_emax(q) - 1e-4), n)
    ie, ii = W.wc_nullclines(q, eg)
    ylo, yhi = ax.y_range[0] - 0.01, ax.y_range[1] + 0.01
    ie = np.where((ie >= ylo) & (ie <= yhi), ie, np.nan)
    ii = np.where((ii >= ylo) & (ii <= yhi), ii, np.nan)
    ce = curve(ax, np.column_stack([eg, ie]), color=GREEN, width=width)
    ci = curve(ax, np.column_stack([eg, ii]), color=RED, width=width)
    return ce, ci


def fp_dots(ax: m.Axes, pars: dict, r: float = 0.11, n: int = 1500) -> m.VGroup:
    W = wc()
    q = dict(W.WC_OSC); q.update(pars)
    return m.VGroup(*[m.Dot(ax.c2p(e, i), radius=r, color=YELLOW if st else m.BLACK, stroke_color=YELLOW, stroke_width=3)
                      for e, i, tr_, det_, st in W.wc_steady_states_fast(q, n=n)])
