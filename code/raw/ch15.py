"""Deck for Chapter 15: Effective action and path integrals."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


def S(x):
    return x ** 2 / 2 - 0.2 * x ** 3 + x ** 4 / 4


class Deck15(GeoDeck):
    chapter = "Chapter 15"
    title = "Effective Action and Path Integrals"
    subtitle = "MSRJD, the loop expansion and generalized activity equations"

    def construct(self):
        self.title_card()
        self.mountain()
        self.histories()
        self.show_figure("ch15_diagrams", "Trees and loops",
                         "Mean field = tree diagrams. Each loop (a fluctuation feeding back) adds a power of $1/N$.")
        self.gae()
        self.show_figure("ch15_oneloop", "Testing the one-loop equations",
                         "Left: $N = 40$, exact average vs mean field vs one loop. Right: the shift of the mean approaches the one-loop value.")
        self.recap(["Laplace: $e^{-S/\\epsilon}$ is a mountain at the minimum of $S$; mean field = the peak",
                    "Gaussian width = fluctuations; asymmetry shifts the mean by $O(\\epsilon)$",
                    "Networks: a path integral over histories with action $N S$, so $\\epsilon = 1/N$",
                    "Effective action $\\Rightarrow$ generalised activity equations for means and correlations"])

    def mountain(self):
        h = heading("A mountain of probability: $e^{-S(x)/\\epsilon}$")
        ax = plane((-2.5, 2.5, 1), (0, 1.5, 0.5), width=8.0, height=4.2, at=pt(-1.4, -0.4), xlabel="x", ylabel="")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        xs = np.linspace(-2.5, 2.5, 500)
        eps = m.ValueTracker(1.0)
        def dens():
            e = eps.get_value(); y = np.exp(-S(xs) / e); y /= np.trapezoid(y, xs)
            return curve(ax, np.column_stack([xs, np.minimum(y, 1.5)]), color=MAGENTA, width=4)
        def gauss():
            e = eps.get_value(); y = np.exp(-xs ** 2 / (2 * e)) / np.sqrt(2 * np.pi * e)
            return m.DashedVMobject(curve(ax, np.column_stack([xs, np.minimum(y, 1.5)]), color=MUTED, width=2), num_dashes=40)
        def mean():
            e = eps.get_value(); y = np.exp(-S(xs) / e); y /= np.trapezoid(y, xs); mu = np.trapezoid(xs * y, xs)
            return m.Line(ax.c2p(mu, 0), ax.c2p(mu, 1.4), color=YELLOW, stroke_width=3)
        D = m.always_redraw(dens); G = m.always_redraw(gauss); M = m.always_redraw(mean)
        lab = m.always_redraw(lambda: prose(f"$\\epsilon = {eps.get_value():.2f}$", font_size=30).move_to(pt(4.8, 1.8)))
        self.add(D, G, M, lab)
        t = prose("magenta: exact\ndashed: Gaussian\nyellow: the mean", font_size=24).move_to(pt(4.8, 0.3))
        self.play(m.FadeIn(t))
        self.next_slide("wide")
        self.play(eps.animate.set_value(0.08), run_time=6)
        t2 = prose("small $\\epsilon$: sharp, Gaussian, mean $\\to$ peak.\nmean field = the peak; corrections $\\propto \\epsilon$", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("narrow")
        self.clear()

    def histories(self):
        self.steps("From one variable to whole histories", [
            (r"\delta[G] = \int \mathcal D\tilde\eta\; e^{-\int\tilde\eta\,G}", "write the equations of motion as a delta functional"),
            (r"P[\eta, s] \propto \int \mathcal D\tilde\eta\,\mathcal D\tilde s\; e^{-N\,S[\eta,\tilde\eta,s,\tilde s]}", "average over initial conditions: an action $\\times N$"),
            (r"\epsilon = 1/N", "a large population is a sharp mountain"),
            (r"\delta S = 0", "the most probable history solves the mean field equations"),
        ], eq_size=34)

    def gae(self):
        self.steps("Generalised activity equations (one loop)", [
            (r"\dot{\bar a} = F(\bar a) + \tfrac12F''(\bar a)\,C", "fluctuations push the mean through the curvature"),
            (r"\dot C = 2F'(\bar a)\,C + G(\bar a)/N", "the covariance: contraction vs noise"),
            (r"C \to 0:\; \dot{\bar a} = F(\bar a)", "mean field theory (Wilson–Cowan) is the $N\\to\\infty$ limit"),
        ], eq_size=36)
