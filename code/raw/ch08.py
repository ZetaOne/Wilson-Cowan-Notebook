"""Deck for Chapter 8: Neural fields."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck08(GeoDeck):
    chapter = "Chapter 8"
    title = "Neural Fields"
    subtitle = "Wilson–Cowan 1973 and Amari: bumps, fronts and waves"

    def construct(self):
        self.title_card()
        self.sum_to_integral()
        self.kernel()
        self.bump_width()
        self.bump()
        self.front()
        self.pulse()
        self.recap(["Field: $\\sum_j w_{ij}a_j \\to \\int w(x-y)f(u(y))\\,dy$ (Amari)",
                    "Bumps: local excitation + surround inhibition; width solves $W(a) = \\theta$",
                    "Stable when the edge reaches into inhibition: $w(a) < 0$",
                    "Fronts: speed $(1 - 2\\theta)/2\\theta$; adaptation turns fronts into pulses"])

    def sum_to_integral(self):
        self.steps("From populations to a sheet", [
            (r"\sum_j w_{ij}\,f(s_j)", "input to population $i$ (Chapter 4)"),
            (r"w_{ij} \to w(x - y)", "put populations at positions; strength depends on distance"),
            (r"\partial_t u = -u + \int w(x-y)\,f\big(u(y,t)\big)\,dy + I", "Amari's equation: the sum becomes an integral"),
        ], eq_size=36)

    def kernel(self):
        d = data("ch08_kernel")
        h = heading("A Mexican hat: excite neighbours, inhibit the surround")
        ax = plane((-8, 8, 4), (-0.5, 1, 0.5), width=9.0, height=4.0, at=pt(-0.6, -0.4), xlabel="x - y", ylabel="w")
        c = curve(ax, np.column_stack([d["x"], d["w"]]), color=TEAL, width=4)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(c), run_time=1.5)
        t = prose("near: excitation (positive)\nfar: inhibition (negative)", font_size=26, color=YELLOW).move_to(pt(4.6, 1.4))
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("kernel")
        self.clear()

    def bump_width(self):
        d = data("ch08_kernel")
        h = heading("A bump of width $a$: the input at its edge is $W(a) = \\int_0^a w$")
        ax = plane((0, 6, 2), (-0.3, 0.6, 0.3), width=7.0, height=4.4, at=pt(-2.2, -0.4), xlabel="a", ylabel="W(a)")
        c = curve(ax, np.column_stack([d["d"], d["Wd"]]), color=TEAL, width=4)
        th = m.DashedLine(ax.c2p(0, 0.3), ax.c2p(6, 0.3), color=ORANGE, stroke_width=3)
        lab = prose("threshold $\\theta = 0.3$", font_size=24, color=ORANGE).next_to(ax.c2p(6, 0.3), m.UP, buff=0.1).shift(m.LEFT * 1.2)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(c), m.Create(th), m.FadeIn(lab), run_time=1.5)
        r1, r2 = d["roots"]
        d1 = m.Dot(ax.c2p(r1, 0.3), radius=0.11, color=m.BLACK, stroke_color=YELLOW, stroke_width=3)
        d2 = m.Dot(ax.c2p(r2, 0.3), radius=0.11, color=YELLOW)
        self.play(m.FadeIn(d1), m.FadeIn(d2))
        t = prose(f"edge exactly at threshold:\ntwo widths, $a = {r1:.2f}$ and $a = {r2:.2f}$", font_size=24).move_to(pt(4.6, 1.6))
        self.play(m.FadeIn(t))
        self.next_slide("two widths")
        t2 = prose("grow the wide bump a little:\n$W$ falls, the edge drops below\nthreshold, the bump shrinks back.\nStable. The narrow one is a\nthreshold: unstable.", font_size=24, color=YELLOW).move_to(pt(4.6, -1.2))
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("stability")
        self.clear()

    def bump(self):
        d = data("ch08_bump")
        t, x, U = d["t"], d["x"], d["strong"]
        h = heading("A brief stimulus leaves a bump: a memory of position")
        ax = plane((-8, 8, 4), (-0.6, 1.2, 0.6), width=9.0, height=4.2, at=pt(-0.6, -0.4), xlabel="x", ylabel="u")
        thl = m.DashedLine(ax.c2p(-8, 0.3), ax.c2p(8, 0.3), color=ORANGE, stroke_width=2)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(thl), run_time=1.0)
        k = m.ValueTracker(0)
        sel = (x >= -8) & (x <= 8)
        prof = m.always_redraw(lambda: curve(ax, np.column_stack([x[sel], U[sel, int(k.get_value())]]), color=MAGENTA, width=4))
        stim = m.always_redraw(lambda: curve(ax, np.column_stack([x[sel], np.exp(-x[sel] ** 2)]), color=BLUE, width=2)
                               .set_stroke(opacity=1.0 if t[int(k.get_value())] < 5 else 0.0))
        lab = m.always_redraw(lambda: prose(f"$t = {t[int(k.get_value())]:.1f}$" + ("   stimulus on" if t[int(k.get_value())] < 5 else "   stimulus off"),
                                            font_size=28).move_to(pt(4.2, 2.1)))
        self.add(prof, stim, lab)
        self.play(k.animate.set_value(len(t) - 1), run_time=8, rate_func=m.linear)
        msg = prose("active in the middle, pushed below rest on both sides by the inhibitory surround", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("bump")
        self.clear()

    def front(self):
        d = data("ch08_front")
        t, x, U = d["t"], d["x"], d["u"]
        h = heading("Excitation only: a front of activity invades")
        ax = plane((0, 80, 20), (0, 1.2, 0.6), width=9.0, height=3.6, at=pt(-0.6, 0.4), xlabel="x", ylabel="u")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        k = m.ValueTracker(0)
        prof = m.always_redraw(lambda: curve(ax, np.column_stack([x, U[:, int(k.get_value())]]), color=MAGENTA, width=4))
        self.add(prof)
        self.play(k.animate.set_value(len(t) - 1), run_time=6, rate_func=m.linear)
        e = tex(r"c = \frac{1 - 2\theta}{2\theta}", font_size=48, color=YELLOW).move_to(pt(-3.0, -2.4))
        w = prose("cells ahead of the edge are pushed over threshold\nby the tail of the kernel; at $\\theta = 1/2$ the front stalls.\nXPPAUT speeds match this to three digits.", font_size=22).move_to(pt(2.6, -2.4))
        self.play(m.Write(e), m.FadeIn(w))
        self.wait(HOLD)
        self.next_slide("front")
        self.clear()

    def pulse(self):
        d = data("ch08_pulse")
        t, x, U, V = d["t"], d["x"], d["u"], d["v"]
        h = heading("Add a slow brake (adaptation): the front grows a back")
        ax = plane((0, 100, 25), (-0.6, 1.0, 0.5), width=9.0, height=4.0, at=pt(-0.6, -0.2), xlabel="x", ylabel="")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        k = m.ValueTracker(0)
        pu = m.always_redraw(lambda: curve(ax, np.column_stack([x, U[:, int(k.get_value())]]), color=MAGENTA, width=4))
        pv = m.always_redraw(lambda: curve(ax, np.column_stack([x, V[:, int(k.get_value())]]), color=BLUE, width=3))
        lab = m.VGroup(prose("activity $u$", font_size=26, color=MAGENTA), prose("adaptation $v$", font_size=26, color=BLUE)).arrange(m.RIGHT, buff=0.6).next_to(ax, m.UP, buff=0.05)
        self.add(pu, pv, lab)
        self.play(k.animate.set_value(len(t) - 1), run_time=8, rate_func=m.linear)
        msg = prose("$v$ builds up behind the front and switches the activity off: a travelling pulse", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("pulse")
        self.clear()
