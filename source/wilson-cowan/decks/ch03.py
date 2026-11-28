"""Deck for Chapter 3: Where the sigmoid comes from."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403
from scipy.stats import norm


class Deck03(GeoDeck):
    chapter = "Chapter 3"
    title = "Where the Sigmoid Comes From"
    subtitle = "Threshold distributions, f–I curves and the refractory factor"

    def construct(self):
        self.title_card()
        self.area_picture()
        self.show_figure("ch03_thresholds", "The shape of the threshold density sets the shape of the gain",
                         "One peak: one S. Two groups of cells: two steps.")
        self.show_figure("ch03_gain", "Checked on 150 simulated θ-neurons (XPPAUT)",
                         "The population rate is the average of the single-cell f–I curves.")
        self.refractory_steps()
        self.window()
        self.show_figure("ch03_refractory", "Wilson and Cowan's Figure 3: integral equation vs ODE",
                         "The ODE (coarse-grained) misses the fast ringing but gets the steady state.")
        self.recap(["Cells have different thresholds; $f(x)$ = fraction whose threshold is below $x$",
                    "So the sigmoid is the cumulative distribution of thresholds: an area",
                    "Peaks of the density give inflection points of $f$",
                    "Refractory cells cannot fire: multiply by the sensitive fraction $1 - rE$"])

    def area_picture(self):
        h = heading("The gain function is an area")
        top = plane((0, 10, 2), (0, 0.4, 0.2), width=9.0, height=2.3, at=pt(-0.6, 1.4), xlabel="\\theta", ylabel="p(\\theta)")
        bot = plane((0, 10, 2), (0, 1, 0.5), width=9.0, height=2.3, at=pt(-0.6, -2.0), xlabel="x", ylabel="f(x)")
        xs = np.linspace(0, 10, 400)
        dens = norm.pdf(xs, 5, 1.2)
        dcur = curve(top, np.column_stack([xs, dens]), color=TEAL, width=4)
        self.play(m.FadeIn(h), m.Create(top), m.Create(bot), m.Create(dcur), run_time=1.2)
        t1 = prose("thresholds vary\nfrom cell to cell", font_size=24, color=TEAL).move_to(pt(5.4, 1.6))
        self.play(m.FadeIn(t1))
        self.next_slide("density")
        x = m.ValueTracker(0.5)

        def shade():
            xv = x.get_value()
            sel = xs <= xv
            if sel.sum() < 2:
                return m.VGroup()
            pts = [top.c2p(xs[0], 0)] + [top.c2p(a, b) for a, b in zip(xs[sel], dens[sel])] + [top.c2p(xs[sel][-1], 0)]
            return m.Polygon(*pts, fill_color=MAGENTA, fill_opacity=0.45, stroke_width=0)
        sh = m.always_redraw(shade)
        line = m.always_redraw(lambda: m.DashedLine(top.c2p(x.get_value(), 0), bot.c2p(x.get_value(), norm.cdf(x.get_value(), 5, 1.2)),
                                                    color=YELLOW, stroke_width=2))
        fc = m.always_redraw(lambda: curve(bot, np.column_stack([xs[xs <= x.get_value()], norm.cdf(xs[xs <= x.get_value()], 5, 1.2)]),
                                           color=MAGENTA, width=4) if (xs <= x.get_value()).sum() > 1 else m.VGroup())
        dd = m.always_redraw(lambda: dot(bot, (x.get_value(), norm.cdf(x.get_value(), 5, 1.2)), color=MAGENTA, r=0.09))
        self.add(sh, line, fc, dd)
        t2 = prose("input $x$: every cell whose\nthreshold is below $x$ fires.\nShaded area = $f(x)$", font_size=22, color=MAGENTA, width=3.4).move_to(pt(5.3, -1.6))
        self.play(m.FadeIn(t2))
        self.play(x.animate.set_value(9.8), run_time=7, rate_func=m.linear)
        self.wait(BEAT)
        self.next_slide("area grows into a sigmoid")
        msg = prose("steepest where the\ndensity peaks:\nthe inflection point", font_size=22, color=YELLOW).move_to(pt(5.3, 0.0))
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("inflection")
        self.clear()

    def refractory_steps(self):
        self.steps("Who is able to fire? The refractory factor", [
            (r"\int_{t-r}^{t} E(t')\,dt'", "fraction that fired in the last $r$: still refractory"),
            (r"1 - \int_{t-r}^{t} E(t')\,dt'", "the sensitive fraction"),
            (r"E(t+\tau) = \Big[1 - \int_{t-r}^{t}E\Big]\,\mathcal S(x)", "sensitive $\\times$ above threshold"),
            (r"\approx (1 - rE)\,\mathcal S(x)", "if $E$ changes slowly over $r$ (next slide)"),
        ], eq_size=38)

    def window(self):
        h = heading("Why the integral becomes $r\\,E(t)$: area = height $\\times$ width")
        ax = plane((0, 10, 2), (0, 1, 0.5), width=9.0, height=4.0, at=pt(-0.6, -0.2), xlabel="t", ylabel="E")
        ts = np.linspace(0, 10, 500)
        E = 0.45 + 0.25 * np.sin(0.45 * ts) + 0.05 * np.sin(2.3 * ts)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(curve(ax, np.column_stack([ts, E]), color=TEAL, width=4)), run_time=1.2)
        r = 1.2
        tt = m.ValueTracker(2.0)

        def area():
            t1 = tt.get_value(); sel = (ts >= t1 - r) & (ts <= t1)
            pts = [ax.c2p(t1 - r, 0)] + [ax.c2p(a, b) for a, b in zip(ts[sel], E[sel])] + [ax.c2p(t1, 0)]
            return m.Polygon(*pts, fill_color=MAGENTA, fill_opacity=0.45, stroke_width=0)
        def rect():
            t1 = tt.get_value(); e = np.interp(t1, ts, E)
            return m.Polygon(ax.c2p(t1 - r, 0), ax.c2p(t1, 0), ax.c2p(t1, e), ax.c2p(t1 - r, e), stroke_color=YELLOW, stroke_width=3, fill_opacity=0)
        A = m.always_redraw(area); R = m.always_redraw(rect)
        self.add(A); self.next_slide("area")
        self.add(R)
        t = prose("magenta: the exact area. yellow box: $r \\times E(t)$.\nThey agree when $E$ barely changes during $r$ (quasi-stationarity).", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(t))
        self.play(tt.animate.set_value(9.5), run_time=6, rate_func=m.linear)
        self.wait(HOLD)
        self.next_slide("window slides")
        self.clear()
