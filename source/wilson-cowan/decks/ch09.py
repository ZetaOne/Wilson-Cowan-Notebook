"""Deck for Chapter 9: Patterns and hallucinations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403

A, C = 1.5, 0.6


def what(k):
    return np.sqrt(np.pi) * (A * np.exp(-k ** 2 / 4) - 3 * C * np.exp(-9 * k ** 2 / 4))


class Deck09(GeoDeck):
    chapter = "Chapter 9"
    title = "Patterns and Hallucinations"
    subtitle = "Turing instabilities and the Ermentrout–Cowan theory"

    def construct(self):
        self.title_card()
        self.linearise()
        self.dispersion()
        self.ring()
        self.sheets()
        self.logmap()
        self.show_figure("ch09_logpolar", "Stripes and spots in cortex, seen as form constants",
                         "Vertical stripes: tunnel. Horizontal: funnel. Oblique: spiral. Hexagons: a lattice of blobs.")
        self.recap(["Linearise a field: each wave $e^{ikx}$ grows at $\\lambda(k) = -1 + \\gamma\\hat w(k)$",
                    "Mexican hat: $\\hat w$ peaks at $k_c > 0$; raising gain destabilises a pattern first",
                    "2-D: stripes (symmetric gain) or hexagons (asymmetric)",
                    "Retina $\\to$ cortex is a complex log: stripes are seen as tunnels, funnels, spirals"])

    def linearise(self):
        self.steps("When does a uniform state break into a pattern?", [
            (r"u = u_0 + \delta u", "perturb the uniform state"),
            (r"\partial_t\delta u = -\delta u + \gamma\!\int w(x-y)\,\delta u(y)\,dy", "keep first order; $\\gamma = f'(u_0)$ is the gain"),
            (r"\delta u = e^{\lambda t}e^{ikx}", "try one wave: convolution just multiplies it by $\\hat w(k)$"),
            (r"\lambda(k) = -1 + \gamma\,\hat w(k)", "each wavelength grows or decays on its own"),
        ], eq_size=36)

    def dispersion(self):
        h = heading("Raise the gain: the peak of $\\lambda(k)$ crosses zero first")
        ax = plane((0, 4, 1), (-2, 1, 1), width=7.6, height=4.4, at=pt(-2.0, -0.3), xlabel="k", ylabel="\\lambda")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        k = np.linspace(0, 4, 400)
        gc = 1 / what(k).max()
        kc = k[np.argmax(what(k))]
        g = m.ValueTracker(0.5)
        cur = m.always_redraw(lambda: curve(ax, np.column_stack([k, np.clip(-1 + g.get_value() * gc * what(k), -2, 1)]), color=TEAL, width=4))
        zero = m.DashedLine(ax.c2p(0, 0), ax.c2p(4, 0), color=MUTED, stroke_width=2)
        lab = m.always_redraw(lambda: prose(f"gain $= {g.get_value():.2f}\\,\\gamma_c$", font_size=30).move_to(pt(4.6, 1.8)))
        self.add(zero, cur, lab)
        self.play(g.animate.set_value(1.3), run_time=6, rate_func=m.linear)
        mk = m.DashedLine(ax.c2p(kc, -2), ax.c2p(kc, 1), color=ORANGE, stroke_width=2)
        t = prose(f"$k = 0$ stays negative (far inhibition wins);\nthe peak at $k_c = {kc:.2f}$ grows first:\na pattern of wavelength $2\\pi/k_c$", font_size=22, color=YELLOW, width=4.0).move_to(pt(4.9, -1.6))
        self.play(m.Create(mk), m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("dispersion")
        self.clear()

    def ring(self):
        d = data("ch09_ring")
        t, x, U = d["t"], d["x"], d["u"]
        h = heading("On a ring of 256 populations (XPPAUT): noise grows into a pattern")
        ax = plane((0, 64, 16), (-0.8, 0.8, 0.4), width=9.0, height=4.0, at=pt(-0.6, -0.3), xlabel="x", ylabel="u - \\theta")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        k = m.ValueTracker(0)
        prof = m.always_redraw(lambda: curve(ax, np.column_stack([x, U[:, int(k.get_value())]]), color=MAGENTA, width=3))
        lab = m.always_redraw(lambda: prose(f"$t = {t[int(k.get_value())]:.0f}$", font_size=30).move_to(pt(5.2, 2.0)))
        self.add(prof, lab)
        self.play(k.animate.set_value(len(t) - 1), run_time=7, rate_func=m.linear)
        msg = prose("ten peaks on a ring of length 64: wavelength 6.4, the allowed one closest to $2\\pi/k_c = 5.76$", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("ring")
        self.clear()

    def sheets(self):
        d = data("ch09_2d")
        h = heading("On a sheet: stripes, spots or holes")
        ims = m.Group(*[image_from_array(d[k], cmap="RdBu_r", height=3.8) for k in ("stripes", "spots", "holes")]).arrange(m.RIGHT, buff=0.4).move_to(pt(0, -0.2))
        labs = m.VGroup(*[prose(s, font_size=24).next_to(im, m.DOWN, buff=0.2) for s, im in zip(
            ["symmetric gain: stripes", "threshold above: spots", "threshold below: holes"], ims)])
        self.play(m.FadeIn(h), m.FadeIn(ims), m.FadeIn(labs), run_time=1.4)
        t = prose("all directions with $|\\vec k| = k_c$ are equally unstable; the nonlinearity chooses the combination", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("2d patterns")
        self.clear()

    def logmap(self):
        h = heading("Retina to cortex is a complex logarithm: $(x_1, x_2) = (\\log r, \\varphi)$")
        cx = plane((-1.5, 1.5, 1.5), (-3.2, 3.2, 3.2), width=4.4, height=4.4, at=pt(-3.6, -0.6), xlabel="x_1", ylabel="x_2", ticks=False)
        vx = plane((-1.6, 1.6, 0.8), (-1.6, 1.6, 0.8), width=4.4, height=4.4, at=pt(3.4, -0.6), xlabel="", ylabel="", ticks=False)
        l1 = prose("cortex", font_size=26, color=MUTED).next_to(cx, m.UP, buff=0.05)
        l2 = prose("visual field", font_size=26, color=MUTED).next_to(vx, m.UP, buff=0.05)
        self.play(m.FadeIn(h), m.Create(cx), m.Create(vx), m.FadeIn(l1), m.FadeIn(l2), run_time=1.0)
        s = m.ValueTracker(0)
        # path 1: vertical line in cortex (x1 = 0) -> circle r = 1
        p1 = m.always_redraw(lambda: curve(cx, np.column_stack([np.zeros(50), np.linspace(-np.pi, -np.pi + s.get_value(), 50)]), color=MAGENTA, width=4))
        q1 = m.always_redraw(lambda: curve(vx, np.column_stack([np.cos(np.linspace(-np.pi, -np.pi + s.get_value(), 80)),
                                                                 np.sin(np.linspace(-np.pi, -np.pi + s.get_value(), 80))]), color=MAGENTA, width=4))
        self.add(p1, q1)
        self.play(s.animate.set_value(2 * np.pi), run_time=3, rate_func=m.linear)
        t1 = prose("vertical line $\\to$ circle", font_size=24, color=MAGENTA).move_to(pt(0, 2.2))
        self.play(m.FadeIn(t1))
        self.next_slide("vertical to circle")
        s2 = m.ValueTracker(-1.5)
        p2 = m.always_redraw(lambda: curve(cx, np.column_stack([np.linspace(-1.5, s2.get_value(), 50), np.full(50, 0.8)]), color=TEAL, width=4))
        q2 = m.always_redraw(lambda: curve(vx, np.column_stack([np.exp(np.linspace(-1.5, s2.get_value(), 50)) * np.cos(0.8),
                                                                 np.exp(np.linspace(-1.5, s2.get_value(), 50)) * np.sin(0.8)]), color=TEAL, width=4))
        self.add(p2, q2)
        self.play(s2.animate.set_value(0.4), run_time=3, rate_func=m.linear)
        t2 = prose("horizontal line $\\to$ ray", font_size=24, color=TEAL).move_to(pt(0, 1.6))
        self.play(m.FadeIn(t2))
        self.next_slide("horizontal to ray")
        s3 = m.ValueTracker(-1.5)
        p3 = m.always_redraw(lambda: curve(cx, np.column_stack([np.linspace(-1.5, s3.get_value(), 60), -2.5 + 2.0 * (np.linspace(-1.5, s3.get_value(), 60) + 1.5)]), color=ORANGE, width=4))
        q3 = m.always_redraw(lambda: curve(vx, np.column_stack([np.exp(np.linspace(-1.5, s3.get_value(), 120)) * np.cos(-2.5 + 2.0 * (np.linspace(-1.5, s3.get_value(), 120) + 1.5)),
                                                                 np.exp(np.linspace(-1.5, s3.get_value(), 120)) * np.sin(-2.5 + 2.0 * (np.linspace(-1.5, s3.get_value(), 120) + 1.5))]), color=ORANGE, width=4))
        self.add(p3, q3)
        self.play(s3.animate.set_value(0.45), run_time=3, rate_func=m.linear)
        t3 = prose("oblique line $\\to$ spiral", font_size=24, color=ORANGE).move_to(pt(0, 1.0))
        self.play(m.FadeIn(t3))
        msg = prose("so cortical stripes are seen as tunnels, funnels and spirals", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("spiral")
        self.clear()
