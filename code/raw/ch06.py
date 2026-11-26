"""Deck for Chapter 6: Oscillations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403

Wl = wc()
OSC = dict(Wl.WC_OSC)


class Deck06(GeoDeck):
    chapter = "Chapter 6"
    title = "Oscillations"
    subtitle = "Hopf bifurcations, limit cycles, frequency and phase"

    def construct(self):
        self.title_card()
        self.loop()
        self.cycle()
        self.timecourse()
        self.hopf()
        self.show_figure("ch06_auto", "Where the rhythm lives: between a homoclinic and a Hopf bifurcation",
                         "Black: steady states (exact). Magenta: max/min of $E$ on the cycle (AUTO). Right: frequency rises with input.")
        self.show_figure("ch06_phase", "Phase: isochrons and phase response curves",
                         "Isochrons wind around the cycle; the PRC is the phase gradient on the cycle.")
        self.recap(["One nullcline crossing on the rising branch of the hump: the steady state repels",
                    "Bounded box + repelling centre: Poincaré–Bendixson gives a limit cycle",
                    "Inhibition lags excitation: that lag is the rhythm",
                    "Rhythm exists between a homoclinic ($T\\to\\infty$) and a Hopf ($A\\to 0$) point; frequency codes input"])

    def loop(self):
        F, ke, ki = Wl.wc_rhs(OSC)
        h = heading("Picture first: one crossing, on the rising part of the hump")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        vf = vfield(ax, lambda x, y: tuple(F(np.array([x, y]))), (0.02, 0.48), (0.02, 0.48), n=12)
        ce, ci = nullcline_curves(ax, OSC)
        self.play(m.FadeIn(h), m.Create(ax), m.FadeIn(vf), m.Create(ce), m.Create(ci), run_time=1.4)
        self.play(m.FadeIn(fp_dots(ax, OSC)))
        self.next_slide("one crossing")
        steps = ["1. right of the hump: self-excitation, $E$ grows",
                 "2. inhibition builds up, with a lag",
                 "3. above the hump: $E$ collapses",
                 "4. $E$ low: inhibition decays; back to 1"]
        rows = m.VGroup(*[prose(s, font_size=24) for s in steps]).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35).move_to(pt(3.7, 0.6))
        for r in rows:
            self.play(m.FadeIn(r, shift=m.RIGHT * 0.2), run_time=0.6)
            self.wait(0.6)
        self.next_slide("loop story")
        t = prose("the flow circulates; on the rising branch\nthe steady state pushes outward", font_size=24, color=YELLOW).move_to(pt(3.7, -2.0))
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("outward")
        self.clear()

    def cycle(self):
        d = data("ch06_cycle")
        h = heading("Wilson & Cowan's Figure 11: an unstable focus inside a limit cycle")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        ce, ci = nullcline_curves(ax, OSC)
        self.play(m.FadeIn(h), m.Create(ax), m.FadeIn(ce), m.FadeIn(ci), m.FadeIn(fp_dots(ax, OSC)), run_time=1.0)
        self.trace(ax, d["Y"][::4], color=BLUE, run_time=5, width=2.5)
        F, ke, ki = Wl.wc_rhs(OSC)
        Xout = rk4(F, (0.45, 0.45), 25, 0.02)
        self.trace(ax, Xout[::4], color=ORANGE, run_time=3, width=2.5)
        cyc = curve(ax, d["X"], color=MAGENTA, width=5)
        self.play(m.Create(cyc), run_time=1.2)
        t = prose("from inside: spirals out\nfrom outside: spirals in\nboth end on the magenta cycle\nperiod $T \\approx 5.0\\,\\tau$", font_size=26).move_to(pt(3.7, 0.6))
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("cycle")
        self.clear()

    def timecourse(self):
        d = data("ch06_cycle")
        X, T = d["X"], float(d["T"])
        t = np.linspace(0, T, len(X))
        tt = np.r_[t, t + T, t + 2 * T]
        h = heading("In time: inhibition peaks after excitation")
        ax = plane((0, 15, 5), (0, 0.3, 0.1), width=10.0, height=4.0, at=pt(0, -0.3), xlabel="t", ylabel="")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        Ec = np.column_stack([tt, np.tile(X[:, 0], 3)])[::6]
        Ic = np.column_stack([tt, np.tile(X[:, 1], 3)])[::6]
        self.play(m.Create(curve(ax, Ec, color=MAGENTA, width=4)), m.Create(curve(ax, Ic, color=BLUE, width=4)), run_time=3)
        lab = m.VGroup(prose("$E(t)$", font_size=28, color=MAGENTA), prose("$I(t)$", font_size=28, color=BLUE)).arrange(m.RIGHT, buff=0.6).next_to(ax, m.UP, buff=0.1)
        self.play(m.FadeIn(lab))
        msg = prose("the lag of $I$ behind $E$ is the whole story: instant inhibition would close the loop at once", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.2)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("lag")
        self.clear()

    def hopf(self):
        d = data("ch06_hopfgif")
        Ps, paths = d["Ps"], d["paths"]
        h = heading("Lowering $P$ through the Hopf point ($P = 1.88$)")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        k = m.ValueTracker(0)
        def scene():
            j = int(k.get_value())
            q = dict(OSC); q["p"] = float(Ps[j])
            ce, ci = nullcline_curves(ax, q, n=300, width=3)
            return m.VGroup(ce, ci, curve(ax, paths[j], color=MAGENTA, width=2.5))
        sc = m.always_redraw(scene)
        lab = m.always_redraw(lambda: prose(f"$P = {Ps[int(k.get_value())]:.2f}$", font_size=34).move_to(pt(3.6, 1.8)))
        self.add(sc, lab)
        self.next_slide("above Hopf: spiral in")
        self.play(k.animate.set_value(len(Ps) - 1), run_time=9, rate_func=m.linear)
        t = prose("above $1.88$: trace $< 0$, spiral in (ringing)\nbelow: trace $> 0$, spiral out onto a cycle\nthat grows from zero amplitude:\na supercritical Hopf bifurcation", font_size=24, color=YELLOW).move_to(pt(3.6, -0.6))
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("hopf")
        self.clear()
