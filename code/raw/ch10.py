"""Deck for Chapter 10: Before Wilson and Cowan."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


def gB(a):
    return (4 * a) ** 4 / (1 + (4 * a) ** 4)


def gG(a):
    return 1 / (1 + np.exp(-8 * (1.6 * a - 0.45)))


class Deck10(GeoDeck):
    chapter = "Chapter 10"
    title = "Before Wilson and Cowan"
    subtitle = "McCulloch–Pitts, Shimbel–Rapoport, Beurle and Griffith"

    def construct(self):
        self.title_card()
        self.show_figure("ch10_timeline", "Thirty years of ideas", "After Table 1 of the review.")
        self.show_figure("ch10_mcp", "1943: McCulloch and Pitts, neurons as logic gates",
                         "Fire when $\\sum_i w_ix_i \\geq h$: AND, OR, NOT, hence any computation.")
        self.bullets("1948: Shimbel and Rapoport, statistics instead of wiring", [
            "many different circuits compute the same thing; brains survive losing neurons",
            "genes cannot specify every synapse, only statistics of connectivity",
            "so: describe the fraction of neurons firing, from probabilities",
            "firing probability depends only on the mean input: mean field"], font_size=28)
        self.compare()
        self.griffith()
        self.recap(["McCulloch–Pitts: threshold logic", "Shimbel–Rapoport: statistical laws, mean input",
                    "Beurle: first neural field; excitation only, so activity dies or saturates",
                    "Griffith: inhibition and the gain function allow stable spontaneous activity"])

    def compare(self):
        h = heading("Beurle vs Griffith on a line: $\\dot A = -A + (1-A)\\,g(A)$")
        axl = plane((0, 0.6, 0.3), (-0.2, 0.2, 0.2), width=4.8, height=3.8, at=pt(-3.7, -0.2), xlabel="A", ylabel="\\dot A")
        axr = plane((0, 0.6, 0.3), (-0.2, 0.2, 0.2), width=4.8, height=3.8, at=pt(3.3, -0.2), xlabel="A", ylabel="\\dot A")
        l1 = prose("Beurle 1956: excitation only", font_size=26, color=TEAL).next_to(axl, m.UP, buff=0.1)
        l2 = prose("Griffith 1963: sigmoid, spontaneous output", font_size=24, color=MAGENTA, width=5.6).next_to(axr, m.UP, buff=0.1)
        a = np.linspace(0, 0.6, 400)
        F1 = -a + (1 - a) * gB(a); F2 = -a + (1 - a) * gG(a)
        self.play(m.FadeIn(h), m.Create(axl), m.Create(axr), m.FadeIn(l1), m.FadeIn(l2), run_time=1.0)
        self.play(m.Create(curve(axl, np.column_stack([a, F1]), color=TEAL, width=4)),
                  m.Create(curve(axr, np.column_stack([a, F2]), color=MAGENTA, width=4)), run_time=1.4)
        fa = flow_arrows(axl, np.linspace(0.03, 0.57, 12), lambda x: -x + (1 - x) * gB(x), scale=0.18)
        fb = flow_arrows(axr, np.linspace(0.03, 0.57, 12), lambda x: -x + (1 - x) * gG(x), scale=0.18)
        self.play(m.FadeIn(fa), m.FadeIn(fb))
        self.next_slide("flows")
        t1 = prose("middle state repels: activity\ndies (to 0) or saturates", font_size=22, color=TEAL).next_to(axl, m.DOWN, buff=0.35)
        t2 = prose("a stable LOW state exists:\nongoing spontaneous activity", font_size=22, color=MAGENTA).next_to(axr, m.DOWN, buff=0.35)
        self.play(m.FadeIn(t1), m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("compare")
        self.clear()

    def griffith(self):
        d = data("ch10_griffith")
        t, x, S = d["t"], d["x"], d["s"]
        h = heading("Griffith's reaction–diffusion field: a front of excitation")
        e = tex(r"\partial_t s = \nabla^2 s - \mu s + f(s)", font_size=40).to_edge(m.UP, buff=1.2)
        ax = plane((0, 100, 25), (0, 2.2, 1), width=9.0, height=3.6, at=pt(-0.6, -1.0), xlabel="x", ylabel="s")
        self.play(m.FadeIn(h), m.Write(e), m.Create(ax), run_time=1.2)
        k = m.ValueTracker(0)
        prof = m.always_redraw(lambda: curve(ax, np.column_stack([x, S[:, int(k.get_value())]]), color=MAGENTA, width=4))
        self.add(prof)
        self.play(k.animate.set_value(len(t) - 1), run_time=6, rate_func=m.linear)
        msg = prose("moves towards the weaker state; stalls when $\\int (f(s) - \\mu s)\\,ds = 0$", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("front")
        self.clear()
