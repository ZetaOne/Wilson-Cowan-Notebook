"""Deck for Chapter 2: One population (flow on a line, bistability, hysteresis, saddle-nodes)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403

W, BETA, TH = 10.0, 1.0, 5.0


def f(x):
    return 1 / (1 + np.exp(-BETA * (x - TH)))


def F(a, I):
    return -a + f(W * a + I)


def roots(I):
    a = np.linspace(-0.05, 1.05, 4001)
    v = F(a, I)
    out = []
    for k in np.where(np.diff(np.sign(v)) != 0)[0]:
        lo, hi = a[k], a[k + 1]
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if np.sign(F(lo, I)) * np.sign(F(mid, I)) <= 0:
                hi = mid
            else:
                lo = mid
        r = 0.5 * (lo + hi)
        slope = -1 + W * BETA * f(W * r + I) * (1 - f(W * r + I))
        out.append((r, slope < 0))
    return out


class Deck02(GeoDeck):
    chapter = "Chapter 2"
    title = "One Population"
    subtitle = "A flow on a line: bistability, hysteresis and saddle-nodes"

    def construct(self):
        self.title_card()
        self.equation()
        self.crossings()
        self.phase_line()
        self.slide_input()
        self.s_curve()
        self.show_figure("ch02_switch", "A memory: a pulse switches the population on, and it stays on")
        self.show_figure("ch02_cusp", "Two knobs, $I$ and $w$: the cusp",
                         "Inside the wedge: two stable states. The wedge closes at the cusp, $w = 4/\\beta$.")
        self.recap(["One population: $\\dot a = -a + f(wa + I)$, a flow on a line",
                    "Steady states: where $f(wa+I)$ crosses the diagonal $a$",
                    "Stable where the curve crosses from above to below; stable and unstable alternate",
                    "Changing $I$ slides the curve: pairs of steady states are born or die (saddle-node)",
                    "S-shaped curve of steady states $\\Rightarrow$ hysteresis: a memory of past input"])

    def equation(self):
        self.steps("One excitatory population talking to itself", [
            (r"\dot a = -a + f(w\,a + I)", "self-excitation $w$, outside input $I$"),
            (r"\dot a = 0 \iff a = f(wa + I)", "steady state: activity reproduces itself"),
            (r"a \;=\; f(wa+I)", "intersection of a line and an S-curve: draw both"),
        ])

    def crossings(self):
        h = heading("Steady states: where the S-curve meets the diagonal")
        ax = plane((0, 1, 0.5), (0, 1, 0.5), width=5.4, height=5.4, at=pt(-3.3, -0.5), xlabel="a", ylabel="")
        diag = curve(ax, np.array([[0, 0], [1, 1]]), color=MUTED, width=3)
        lab_d = prose("$a$", font_size=26, color=MUTED).next_to(ax.c2p(1, 1), m.RIGHT, buff=0.1)
        aa = np.linspace(0, 1, 300)
        S = curve(ax, np.column_stack([aa, f(W * aa + 0.0)]), color=TEAL, width=4)
        lab_s = prose("$f(wa+I)$", font_size=26, color=TEAL).next_to(ax.c2p(0.95, 1.0), m.UP, buff=0.05)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(diag), m.FadeIn(lab_d), run_time=1.0)
        self.play(m.Create(S), m.FadeIn(lab_s), run_time=1.2)
        dots = m.VGroup(*[m.Dot(ax.c2p(r, r), radius=0.11, color=YELLOW if st else m.BLACK, stroke_color=YELLOW, stroke_width=3)
                          for r, st in roots(0.0)])
        self.play(m.FadeIn(dots))
        t = prose("three crossings at $I = 0$:\nlow, middle, high.\nWhich are stable?", font_size=28).move_to(pt(3.4, 1.2))
        self.play(m.FadeIn(t))
        self.next_slide("three crossings")
        t2 = prose("Above the diagonal: $f > a$, so $a$ grows.\nBelow: $a$ shrinks.\nFilled = stable, open = unstable.", font_size=26, color=YELLOW).move_to(pt(3.4, -1.4))
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("stability rule")
        self.clear()

    def phase_line(self):
        h = heading("The same thing as a flow on a line: $\\dot a$ against $a$")
        ax = plane((0, 1, 0.5), (-0.4, 0.4, 0.2), width=9.0, height=4.0, at=pt(-0.6, -0.1), xlabel="a", ylabel="\\dot a")
        aa = np.linspace(0, 1, 400)
        g = curve(ax, np.column_stack([aa, F(aa, 0.0)]), color=TEAL, width=4)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(g), run_time=1.2)
        arr = flow_arrows(ax, np.linspace(0.04, 0.96, 18), lambda a: F(a, 0.0))
        self.play(m.LaggedStart(*[m.GrowArrow(a) for a in arr], lag_ratio=0.05), run_time=1.6)
        dots = m.VGroup(*[m.Dot(ax.c2p(r, 0), radius=0.12, color=YELLOW if st else m.BLACK, stroke_color=YELLOW, stroke_width=3)
                          for r, st in roots(0.0)])
        self.play(m.FadeIn(dots))
        t = prose("arrows point towards the outer crossings and away from the middle one:\nthe middle state is a threshold between the low and high states", font_size=26, color=YELLOW).to_edge(m.DOWN, buff=0.2)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("phase line")
        self.clear()

    def slide_input(self):
        h = heading("Turn the input knob: the S-curve slides sideways")
        ax = plane((0, 1, 0.5), (0, 1, 0.5), width=5.4, height=5.4, at=pt(-3.3, -0.5), xlabel="a", ylabel="")
        diag = curve(ax, np.array([[0, 0], [1, 1]]), color=MUTED, width=3)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(diag), run_time=1.0)
        I = m.ValueTracker(-4.0)
        aa = np.linspace(0, 1, 300)
        S = m.always_redraw(lambda: curve(ax, np.column_stack([aa, f(W * aa + I.get_value())]), color=TEAL, width=4))
        dots = m.always_redraw(lambda: m.VGroup(*[m.Dot(ax.c2p(r, r), radius=0.11, color=YELLOW if st else m.BLACK,
                                                        stroke_color=YELLOW, stroke_width=3) for r, st in roots(I.get_value())]))
        lab = m.always_redraw(lambda: prose(f"$I = {I.get_value():+.2f}$, {len(roots(I.get_value()))} steady state" +
                                            ("s" if len(roots(I.get_value())) > 1 else ""), font_size=30).move_to(pt(3.5, 1.5)))
        self.add(S, dots, lab)
        self.next_slide("start low input")
        self.play(I.animate.set_value(4.0), run_time=7, rate_func=m.linear)
        self.next_slide("slide up")
        t = prose("At $I \\approx \\pm 1.8$ the curve just touches the diagonal:\ntwo steady states merge and vanish.\nThis is a saddle-node (fold) bifurcation.", font_size=26, color=YELLOW).move_to(pt(3.5, -1.2))
        self.play(m.FadeIn(t))
        self.play(I.animate.set_value(-4.0), run_time=7, rate_func=m.linear)
        self.wait(BEAT)
        self.next_slide("saddle node")
        self.clear()

    def s_curve(self):
        d = data("ch02_ramp")
        h = heading("Stack the steady states for every $I$: the S-curve, and hysteresis")
        ax = plane((-4, 4, 2), (0, 1, 0.5), width=8.0, height=4.2, at=pt(-1.4, -0.1), xlabel="I", ylabel="a^*")
        a = np.linspace(1e-4, 1 - 1e-4, 3000)
        Ia = TH - np.log(1 / a - 1) / BETA - W * a
        st = W * BETA * a * (1 - a) < 1
        stab = curve(ax, np.column_stack([np.where(st, Ia, np.nan), a]), color=INK, width=4)
        uns = m.DashedVMobject(curve(ax, np.column_stack([np.where(~st, Ia, np.nan), a]), color=INK, width=2.5), num_dashes=40)
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        # stable branches drawn piecewise (np.nan splits)
        lo = a < 0.5
        b1 = curve(ax, np.column_stack([Ia[st & lo], a[st & lo]]), color=INK, width=4)
        b2 = curve(ax, np.column_stack([Ia[st & ~lo], a[st & ~lo]]), color=INK, width=4)
        mid = m.DashedVMobject(curve(ax, np.column_stack([Ia[~st], a[~st]]), color=INK, width=2.5), num_dashes=30)
        self.play(m.Create(b1), m.Create(b2), m.Create(mid), run_time=1.6)
        t = prose("solid: stable\ndashed: unstable\n(thresholds)", font_size=24, color=MUTED).move_to(pt(5.4, 0.6))
        self.play(m.FadeIn(t))
        self.next_slide("S curve")
        X = np.column_stack([d["I"], d["A"]])[::10]
        self.trace(ax, X, color=MAGENTA, run_time=8, width=3)
        t2 = prose("ramp $I$ up: stay low until the low state dies, then jump up.\nramp down: stay high until the high state dies.\nIn between, the state remembers the past.", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.1)
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("hysteresis")
        self.clear()
