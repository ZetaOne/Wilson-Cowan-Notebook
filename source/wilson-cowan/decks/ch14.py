"""Deck for Chapter 14: Fluctuations and finite size."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck14(GeoDeck):
    chapter = "Chapter 14"
    title = "Fluctuations and Finite Size"
    subtitle = "Moment hierarchies, Fokker–Planck and the linear noise approximation"

    def construct(self):
        self.title_card()
        self.model()
        self.show_figure("ch14_finite", "Finite populations fluctuate; the variance falls like $1/N$",
                         "Exact (Gillespie) simulations against the linear noise approximation.")
        self.lna()
        self.wells()
        self.recap(["$N$ two-state neurons: an exact master equation; mean field = Wilson–Cowan",
                    "Variance $\\propto 1/N$: $\\sigma^2 = G/(2|F'|N)$ (linear noise)",
                    "Curved flow + fluctuations shift the mean by $O(1/N)$",
                    "Bistable states become metastable: switching time $\\sim e^{N\\Delta\\Phi}$"])

    def model(self):
        self.steps("A population of $N$ stochastic neurons", [
            (r"n \to n+1 \;\text{ at rate } (N-n)\,f(wn/N + I)", "a quiescent neuron switches on"),
            (r"n \to n-1 \;\text{ at rate } n", "an active neuron switches off"),
            (r"\dot a = -a + (1 - a)\,f(wa + I)", "large $N$: (up $-$ down)$/N$, a Wilson–Cowan equation"),
        ], eq_size=36)

    def lna(self):
        self.steps("Why the variance is $G/(2|F'|N)$", [
            (r"\dot a = F(a) + \sqrt{G(a)/N}\;\xi(t)", "Langevin: drift = difference, noise = sum of rates"),
            (r"x = a - a^*:\quad \dot x = F'(a^*)\,x + \sqrt{G/N}\,\xi", "linearise near the steady state"),
            (r"\sigma^2 = \frac{G(a^*)}{2\,|F'(a^*)|\,N}", "restoring force vs noise: a steeper flow, a tighter cloud"),
        ], eq_size=36)

    def wells(self):
        d = data("ch14_switch")
        a, Phi, r = d["a"], d["Phi"], d["roots"]
        h = heading("Finite size can change the behaviour: hopping between wells")
        ax = plane((0, 0.6, 0.3), (0, 0.08, 0.04), width=5.2, height=3.8, at=pt(-3.6, -0.3), xlabel="a", ylabel="\\Phi")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        self.play(m.Create(curve(ax, np.column_stack([a, Phi])[::10], color=TEAL, width=4)), run_time=1.2)
        tq = prose("$p(a) \\propto e^{-N\\Phi(a)}$", font_size=28).next_to(ax, m.UP, buff=0.1)
        self.play(m.FadeIn(tq))
        ball = m.ValueTracker(0)
        traj = d["a80"]
        bd = m.always_redraw(lambda: m.Dot(ax.c2p(traj[int(ball.get_value())], np.interp(traj[int(ball.get_value())], a, Phi)) + np.array([0, 0.12, 0]),
                                           radius=0.11, color=MAGENTA))
        ax2 = plane((0, 400, 100), (0, 0.6, 0.3), width=5.4, height=3.8, at=pt(3.4, -0.3), xlabel="t", ylabel="a")
        tr = m.always_redraw(lambda: curve(ax2, np.column_stack([d["t80"], traj])[: max(2, int(ball.get_value()))], color=MAGENTA, width=1.5))
        self.play(m.Create(ax2))
        self.add(bd, tr)
        self.play(ball.animate.set_value(len(traj) - 1), run_time=9, rate_func=m.linear)
        t = prose("80 neurons (XPPAUT, Langevin): noise carries the state over the ridge.\nMean field says it stays forever; the waiting time grows like $e^{N\\Delta\\Phi}$.", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.12)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("switching")
        self.clear()
