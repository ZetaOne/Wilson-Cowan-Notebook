"""Deck for Chapter 12: When rate models fail."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck12(GeoDeck):
    chapter = "Chapter 12"
    title = "When Rate Models Fail"
    subtitle = "Gerstner's spike-response formalism and fast transients"

    def construct(self):
        self.title_card()
        self.volleys()
        self.why()
        self.show_figure("ch12_srm", "Gerstner's spike-response model",
                         "Potential = refractory kernel after own spike + sum of response kernels to input spikes.")
        self.validity()
        self.recap(["Rate models assume quasi-stationarity",
                    "After a sudden input, similar neurons fire in synchronous volleys",
                    "Heterogeneity or noise dephases them into asynchronous firing",
                    "Valid when $\\langle\\Delta t_{isi}\\rangle\\,\\dot A/A \\ll 1$"])

    def volleys(self):
        d = data("ch12_transient")
        h = heading("A step of input to 300 θ-neurons at $t = 10$")
        axs = []
        for col, (lab, ymax) in enumerate([("nearly identical ($\\Delta = 0.01$)", 3.5), ("heterogeneous ($\\Delta = 0.2$)", 0.8)]):
            ax = plane((0, 40, 10), (0, ymax, ymax / 2), width=5.6, height=3.8, at=pt(-3.4 + 6.8 * col, -0.3), xlabel="t", ylabel="A")
            axs.append(ax)
            self.add(prose(lab, font_size=24, color=MUTED).next_to(ax, m.UP, buff=0.1))
        self.play(m.FadeIn(h), *[m.Create(a) for a in axs], run_time=1.0)
        for col, ax in enumerate(axs):
            rm = np.column_stack([d["tm"], d[f"rm{col}"]])[::10]
            self.play(m.Create(curve(ax, rm, color=BLUE, width=3)), run_time=1.0)
        t1 = prose("blue: rate model $\\dot r = -r + F$", font_size=24, color=BLUE).to_edge(m.DOWN, buff=0.6)
        self.play(m.FadeIn(t1))
        self.next_slide("rate model")
        for col, ax in enumerate(axs):
            r = np.column_stack([d["tc"], np.minimum(d[f"r{col}"], 3.5 if col == 0 else 0.8)])
            self.play(m.Create(curve(ax, r, color=MAGENTA, width=3)), run_time=3)
        t2 = prose("magenta: the spiking network. Identical neurons fire in volleys the rate model cannot show.", font_size=24, color=MAGENTA).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("volleys")
        self.clear()

    def why(self):
        h = heading("Why: the population remembers when the step came")
        ax = plane((-1.5, 1.5, 1.5), (-1.5, 1.5, 1.5), width=4.6, height=4.6, at=pt(-3.6, -0.5), xlabel="", ylabel="", ticks=False)
        circ = m.Circle(radius=ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0], color=MUTED, stroke_width=3).move_to(ax.c2p(0, 0))
        spike = m.Dot(ax.c2p(-1, 0), radius=0.12, color=ORANGE)
        # inside the circle, right of the dot: the neurons move on the circle, the inside stays free
        sl = prose("spike at $\\theta = \\pi$", font_size=22, color=ORANGE).next_to(spike, m.RIGHT, buff=0.2)
        self.play(m.FadeIn(h), m.Create(circ), m.FadeIn(spike), m.FadeIn(sl), run_time=1.0)
        rng = np.random.default_rng(1)
        N = 40
        eta_same = 0.7 + 0.01 * rng.standard_cauchy(N).clip(-5, 5)
        eta_diff = 0.7 + 0.2 * rng.standard_cauchy(N).clip(-5, 5)
        T = m.ValueTracker(0.0)
        th0 = -0.5
        def pos(etas):
            tt = T.get_value()
            etas = np.clip(etas, 0.05, None)
            th = 2 * np.arctan(np.sqrt(etas) * np.tan(np.sqrt(etas) * tt + np.arctan(np.tan(th0 / 2) / np.sqrt(etas))))
            ph = np.sqrt(etas) * tt / np.pi
            return th, ph
        def dots(etas, col, shift):
            th, ph = pos(etas)
            ang = 2 * np.pi * (ph + (th0 + np.pi) / (2 * np.pi)) - np.pi
            return m.VGroup(*[m.Dot(ax.c2p(np.cos(a), np.sin(a)) + shift, radius=0.07, color=col) for a in ang])
        g1 = m.always_redraw(lambda: dots(eta_same, MAGENTA, np.array([0, 0, 0])))
        self.add(g1)
        t1 = prose("all start at rest together:\nthey run around the cycle\nas a clump, firing together", font_size=24, color=MAGENTA).move_to(pt(3.6, 1.2))
        self.play(m.FadeIn(t1))
        self.play(T.animate.set_value(12), run_time=6, rate_func=m.linear)
        self.next_slide("clump")
        self.remove(g1)
        T.set_value(0)
        g2 = m.always_redraw(lambda: dots(eta_diff, TEAL, np.array([0, 0, 0])))
        self.add(g2)
        t2 = prose("different speeds: the clump\nspreads out after a few laps\n(asynchronous firing)", font_size=24, color=TEAL).move_to(pt(3.6, -1.2))
        self.play(m.FadeIn(t2))
        self.play(T.animate.set_value(12), run_time=6, rate_func=m.linear)
        self.wait(HOLD)
        self.next_slide("spread")
        self.clear()

    def validity(self):
        self.steps("Gerstner's validity condition for rate models", [
            (r"\langle\Delta t_{\rm isi}\rangle\;\frac{\dot A(t)}{A(t)} \ll 1", "activity must change little within one interspike interval"),
            (r"\text{volleys: } \dot A/A \text{ huge}", "fails: rate models miss synchrony"),
            (r"\text{asynchronous: } \dot A \approx 0", "holds: rate models are excellent"),
        ], eq_size=36)
