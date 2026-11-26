"""Deck for Chapter 13: Mean field theory for spiking networks."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck13(GeoDeck):
    chapter = "Chapter 13"
    title = "Mean Field Theory for Spiking Networks"
    subtitle = "θ-neurons, the Klimontovich equation, and where the gain function comes from"

    def construct(self):
        self.title_card()
        self.circle()
        self.klim()
        self.density()
        self.gain_steps()
        self.show_figure("ch13_gain", "Gain functions derived from θ-neurons",
                         "A spread of excitabilities smooths the square-root corner into a sigmoid-like curve.")
        self.mpr()
        self.recap(["A spiking neuron is a point running round a circle; a population is a density",
                    "Conservation: $\\partial_t\\eta + \\partial_\\theta(F\\eta) = 0$ (Klimontovich)",
                    "Steady density $C/F$: crowded where slow; flux $C = 1/T(s)$ is the gain",
                    "Mean field alone never relaxes; MPR is an exact two-variable mean field"])

    def circle(self):
        h = heading("A spiking neuron is a point running round a circle")
        ax = plane((-1.5, 1.5, 1.5), (-1.5, 1.5, 1.5), width=4.8, height=4.8, at=pt(-3.4, -0.5), xlabel="", ylabel="", ticks=False)
        R = ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0]
        circ = m.Circle(radius=R, color=MUTED, stroke_width=3).move_to(ax.c2p(0, 0))
        e = tex(r"\dot\theta = 1 - \cos\theta + (1 + \cos\theta)(\eta + s)", font_size=34).move_to(pt(3.4, 2.0))
        self.play(m.FadeIn(h), m.Create(circ), m.Write(e), run_time=1.2)
        sp = m.Dot(ax.c2p(-1, 0), radius=0.12, color=ORANGE)
        self.add(sp, prose("spike", font_size=22, color=ORANGE).next_to(sp, m.LEFT, buff=0.1))
        eta = 0.3
        T = m.ValueTracker(0.0)
        def p():
            tt = T.get_value()
            th = 2 * np.arctan(np.sqrt(eta) * np.tan(np.sqrt(eta) * tt - np.pi / 2 + 1e-6))
            return m.Dot(ax.c2p(np.cos(th + np.pi), np.sin(th + np.pi)), radius=0.12, color=MAGENTA)
        d = m.always_redraw(p)
        self.add(d)
        t = prose("slow near $\\theta = 0$ (speed $2\\eta$),\nfast through the spike (speed 2)", font_size=26, color=YELLOW).move_to(pt(3.4, 0.2))
        self.play(m.FadeIn(t))
        self.play(T.animate.set_value(3 * np.pi / np.sqrt(eta) - 0.01), run_time=8, rate_func=m.linear)
        self.wait(BEAT)
        self.next_slide("one neuron")
        self.clear()

    def klim(self):
        self.steps("From points to a density", [
            (r"\eta_i(\theta, t) = \delta(\theta - \theta_i(t))", "density of one neuron: a spike of density at its phase"),
            (r"\delta(t - t_j^s) = F(\pi, s_j)\,\eta_j(\pi, t)", "firing = flux through $\\theta = \\pi$"),
            (r"\partial_t\eta + \partial_\theta(F\eta) = 0", "neurons are conserved: inflow minus outflow"),
            (r"F\,\eta = C \;\Rightarrow\; \eta = C/F", "at steady state: constant flux, crowded where slow"),
        ], eq_size=36)

    def density(self):
        d = data("ch13_density")
        th, F, C, ph = d["th"], d["F"], float(d["C"]), d["phases"]
        h = heading("Crowded where slow, like traffic")
        ax = plane((-3, 3, 3), (0, 0.35, 0.1), width=6.4, height=4.0, at=pt(-3.0, -0.4), xlabel="\\theta", ylabel="\\eta")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        hist, edges = np.histogram(ph, bins=24, range=(-np.pi, np.pi), density=True)
        bars = m.VGroup(*[m.Polygon(ax.c2p(a, 0), ax.c2p(b, 0), ax.c2p(b, v), ax.c2p(a, v), fill_color=MAGENTA, fill_opacity=0.45, stroke_width=0)
                          for a, b, v in zip(edges[:-1], edges[1:], hist)])
        self.play(m.FadeIn(bars), run_time=1.0)
        self.play(m.Create(curve(ax, np.column_stack([th, C / F]), color=INK, width=4)), run_time=1.2)
        t = prose("200 neurons (XPPAUT) vs $C/F(\\theta)$", font_size=24).next_to(ax, m.UP, buff=0.05)
        self.play(m.FadeIn(t))
        ax2 = plane((0, 35, 10), (0, 0.35, 0.1), width=5.0, height=3.2, at=pt(3.7, -0.4), xlabel="t", ylabel="A")
        self.play(m.Create(ax2), m.Create(curve(ax2, np.column_stack([d["tu"], d["ru"]]), color=TEAL, width=3)), run_time=2)
        t2 = prose("started uniformly: the rate\nnever settles (no dissipation)", font_size=22, color=TEAL).next_to(ax2, m.UP, buff=0.05)
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("density")
        self.clear()

    def gain_steps(self):
        self.steps("Where the gain function comes from", [
            (r"\langle F\eta\rangle \to F(\theta, \langle s\rangle)\langle\eta\rangle", "mean field: factorise all averages"),
            (r"\tau_s\dot s = -s + \sum_j w\,F(\pi)\langle\eta_j(\pi)\rangle", "the STM form, with the firing rate as gain"),
            (r"F(\pi)\,\eta(\pi) = C = 1/T(s)", "steady density: the rate is one over the period"),
            (r"f(s) = \sqrt{\eta + s}/\pi", "for the θ-neuron"),
        ], eq_size=36)

    def mpr(self):
        d = data("ch13_mpr")
        d12 = data("ch12_transient")
        h = heading("Exact mean field (Montbrió–Pazó–Roxin): two variables catch the volleys")
        e = tex(r"\dot r = \frac{\Delta}{\pi} + 2rv,\qquad \dot v = v^2 + \eta_0 + I - \pi^2r^2", font_size=34).to_edge(m.UP, buff=1.1)
        ax = plane((5, 40, 5), (0, 4, 2), width=6.0, height=3.2, at=pt(-3.2, -0.6), xlabel="t", ylabel="r")
        ax2 = plane((-3, 3, 3), (0, 1.2, 0.6), width=4.2, height=3.2, at=pt(3.8, -0.6), xlabel="v", ylabel="r")
        self.play(m.FadeIn(h), m.Write(e), m.Create(ax), m.Create(ax2), run_time=1.2)
        net = np.column_stack([d12["tc"], np.minimum(d12["r0"], 4)])
        net = net[net[:, 0] >= 5]
        self.play(m.Create(curve(ax, net, color=MAGENTA, width=3)), run_time=1.5)
        sel = d["t0"] >= 5
        mp = np.column_stack([d["t0"][sel], np.minimum(d["r0"][sel], 4)])[::4]
        self.play(m.Create(curve(ax, mp, color=INK, width=2.5)), run_time=2.5)
        sel2 = d["t1"] > 10
        vr = np.column_stack([d["v1"][sel2], d["r1"][sel2]])[::4]
        vr0 = np.column_stack([d["v0"][d["t0"] > 10], d["r0"][d["t0"] > 10]])[::2]
        vr0 = vr0[(np.abs(vr0[:, 0]) < 3) & (vr0[:, 1] < 1.2)]
        self.play(m.Create(curve(ax2, vr, color=BLUE, width=3)), run_time=2)
        t = prose("magenta: network; white: MPR. In the $(v, r)$ plane: a spiral into a focus,\na second variable that remembers the phase", font_size=20, color=YELLOW).to_edge(m.DOWN, buff=0.08)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("MPR")
        self.clear()
