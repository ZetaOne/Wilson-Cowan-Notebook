"""Deck for Chapter 5: The E–I phase plane."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403

Wl = wc()
HY = dict(Wl.WC_HYST)


class Deck05(GeoDeck):
    chapter = "Chapter 5"
    title = "The E–I Phase Plane"
    subtitle = "Nullclines, fixed points and excitability"

    def construct(self):
        self.title_card()
        self.nullcline_rules()
        self.hump()
        self.fig4()
        self.kicks()
        self.show_figure("ch05_strength", "How strong, how long? Wilson and Cowan's Figure 9",
                         "Short pulses must be strong; long pulses level off at a minimum intensity.")
        self.evoked()
        self.recap(["$I$-nullcline rises; $E$-nullcline has a hump (self-excitation)",
                    "Crossings are steady states; three crossings: stable, saddle, stable",
                    "The saddle's stable manifold is the switching threshold",
                    "A stable focus rings after a kick: delayed inhibition, an evoked response"])

    def nullcline_rules(self):
        self.steps("Nullclines: where one arrow component vanishes", [
            (r"\dot E = 0", "flow is purely vertical on the green curve"),
            (r"\dot I = 0", "flow is purely horizontal on the red curve"),
            (r"\dot E = \dot I = 0", "where they cross: steady states"),
        ])

    def hump(self):
        F, ke, ki = Wl.wc_rhs(HY)
        h = heading("Why the $E$-nullcline has a hump: freeze $I$")
        left = plane((0, 0.5, 0.25), (-0.3, 0.15, 0.15), width=5.4, height=4.0, at=pt(-3.6, -0.3), xlabel="E", ylabel="\\dot E")
        right = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=4.6, height=4.6, at=pt(3.4, -0.4), xlabel="E", ylabel="I")
        self.play(m.FadeIn(h), m.Create(left), m.Create(right), run_time=1.0)
        e = np.linspace(0.0, 0.48, 300)
        Iv = m.ValueTracker(0.02)
        g = m.always_redraw(lambda: curve(left, np.column_stack([e, F(np.array([e, np.full_like(e, Iv.get_value())]))[0]]), color=TEAL, width=4))
        def zeros(I):
            v = F(np.array([e, np.full_like(e, I)]))[0]
            return [e[k] for k in np.where(np.diff(np.sign(v)) != 0)[0]]
        zd = m.always_redraw(lambda: m.VGroup(*[m.Dot(left.c2p(z, 0), radius=0.09, color=YELLOW) for z in zeros(Iv.get_value())]))
        lab = m.always_redraw(lambda: prose(f"$I = {Iv.get_value():.2f}$", font_size=28).move_to(pt(-3.6, 2.3)))
        hline = m.always_redraw(lambda: m.DashedLine(right.c2p(0, Iv.get_value()), right.c2p(0.5, Iv.get_value()), color=MUTED, stroke_width=2))
        self.add(g, zd, lab, hline)
        self.next_slide("frozen I")
        trail = m.VGroup()
        self.add(trail)
        for I in np.linspace(0.02, 0.4, 40):
            self.play(Iv.animate.set_value(I), run_time=0.12, rate_func=m.linear)
            for z in zeros(I):
                trail.add(m.Dot(right.c2p(z, I), radius=0.05, color=GREEN))
        t = prose("stack the zeros for every $I$:\nthey trace the $E$-nullcline", font_size=24, color=GREEN).next_to(right, m.UP, buff=0.05)
        self.play(m.FadeIn(t))
        ce, ci = nullcline_curves(right, HY)
        self.play(m.Create(ce), run_time=1.2)
        self.wait(HOLD)
        self.next_slide("hump traced")
        self.clear()

    def fig4(self):
        F, ke, ki = Wl.wc_rhs(HY)
        h = heading("Wilson & Cowan's Figure 4: three steady states")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        vf = vfield(ax, lambda x, y: tuple(F(np.array([x, y]))), (0.02, 0.48), (0.02, 0.48), n=12)
        ce, ci = nullcline_curves(ax, HY)
        self.play(m.FadeIn(h), m.Create(ax), m.FadeIn(vf), run_time=1.2)
        self.play(m.Create(ce), m.Create(ci), run_time=1.4)
        fps = fp_dots(ax, HY)
        self.play(m.FadeIn(fps))
        txt = prose("rest $(0, 0)$: stable\nmiddle: saddle\nactive $(0.44, 0.23)$: stable", font_size=26).move_to(pt(3.6, 1.6))
        self.play(m.FadeIn(txt))
        self.next_slide("three fixed points")
        for x0, col in [((0.08, 0.02), TEAL), ((0.12, 0.02), MAGENTA), ((0.45, 0.05), ORANGE), ((0.05, 0.4), BLUE)]:
            X = rk4(F, x0, 30, 0.02)
            self.trace(ax, X[::3], color=col, run_time=2.0)
        t2 = prose("two nearby starts, two different fates:\nthe saddle's stable manifold separates\nthe basin of rest from the basin of activity", font_size=24, color=YELLOW).move_to(pt(3.6, -1.4))
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("separatrix")
        self.clear()

    def kicks(self):
        d = data("ch05_kicks")
        P = d["paths"]
        h = heading("Kick $E$ from rest: small kicks decay, large ones switch on")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        ce, ci = nullcline_curves(ax, HY)
        self.play(m.FadeIn(h), m.Create(ax), m.FadeIn(ce), m.FadeIn(ci), m.FadeIn(fp_dots(ax, HY)), run_time=1.0)
        k = m.ValueTracker(2)
        cols = [m.interpolate_color(TEAL, MAGENTA, j / (len(P) - 1)) for j in range(len(P))]
        paths = m.always_redraw(lambda: m.VGroup(*[curve(ax, P[j, : max(2, int(k.get_value()))], color=cols[j], width=3) for j in range(len(P))]))
        self.add(paths)
        self.play(k.animate.set_value(P.shape[1] - 1), run_time=6, rate_func=m.linear)
        t = prose("a threshold, but not a single number:\nit is a curve in the plane", font_size=26, color=YELLOW).move_to(pt(3.6, 0.5))
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("kicks")
        self.clear()

    def evoked(self):
        d = data("ch05_evoked")
        t, e, i = d["t"], d["e"], d["i"]
        h = heading("A stable focus rings: the evoked response (Figure 10)")
        ax = plane((0, 40, 10), (-0.2, 0.4, 0.2), width=6.2, height=3.6, at=pt(-3.2, -0.6), xlabel="t", ylabel="E - I")
        ax2 = plane((0, 0.4, 0.2), (0, 0.3, 0.15), width=4.4, height=3.6, at=pt(3.6, -0.6), xlabel="E", ylabel="I")
        self.play(m.FadeIn(h), m.Create(ax), m.Create(ax2), run_time=1.0)
        s = slice(None, None, 20)
        k = m.ValueTracker(2)
        c1 = m.always_redraw(lambda: curve(ax, np.column_stack([t[s], (e - i)[s]])[: max(2, int(k.get_value()))], color=MAGENTA, width=3))
        c2 = m.always_redraw(lambda: curve(ax2, np.column_stack([e[s], i[s]])[: max(2, int(k.get_value()))], color=MAGENTA, width=3))
        self.add(c1, c2)
        self.play(k.animate.set_value(len(t[s]) - 1), run_time=6, rate_func=m.linear)
        msg = prose("pulse raises $E$; $I$ follows late and overshoots; $E$ dips below rest; repeat, smaller.\nDelayed negative feedback = a spiral into a stable focus ($-0.20 \\pm 0.53i$).", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("evoked")
        self.clear()
