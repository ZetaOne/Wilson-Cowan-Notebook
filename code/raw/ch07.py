"""Deck for Chapter 7: Multistability and two-parameter maps."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403

Wl = wc()
HY = dict(Wl.WC_HYST)


class Deck07(GeoDeck):
    chapter = "Chapter 7"
    title = "Multistability and Two-Parameter Maps"
    subtitle = "Hysteresis loops, cusps and Bogdanov–Takens points"

    def construct(self):
        self.title_card()
        self.lift()
        self.slide()
        self.loop()
        self.show_figure("ch07_fig67", "Wilson & Cowan's Figures 6 and 7: more folds",
                         "Left: two separate loops. Right: overlapping loops, three stable states at once (shaded).")
        self.show_figure("ch07_twopar", "Two inputs at once: the $(P, Q)$ map",
                         "Blue: folds (crossings born or lost). Orange: Hopf (spiral turns outward). They meet at a cusp and Bogdanov–Takens points.")
        self.recap(["Input $P$ lifts the $E$-nullcline by $P/c_2$; the $I$-nullcline stays put",
                    "Crossings appear and vanish in pairs at tangencies: folds",
                    "S-shaped steady-state curve: hysteresis, a memory of recent input",
                    "Two-parameter maps: fold and Hopf curves divide the input plane into regions"])

    def lift(self):
        self.steps("The one geometric move: $P$ lifts the $E$-nullcline", [
            (r"E = (k_E - r_EE)\,\mathcal S_E(c_1E - c_2I + P)", "steady state of the $E$ equation"),
            (r"c_1E - c_2I + P = \mathcal S_E^{-1}\!\Big(\frac{E}{k_E - r_EE}\Big)", "invert the sigmoid"),
            (r"I = \frac{c_1E - \mathcal S_E^{-1}(\dots)}{c_2} + \frac{P}{c_2}", "$P$ only adds a constant: a vertical shift"),
        ], eq_size=36)

    def slide(self):
        h = heading("Raise and lower $P$: crossings appear and vanish in pairs")
        ax = plane((0, 0.5, 0.25), (0, 0.5, 0.25), width=5.8, height=5.8, at=pt(-2.8, -0.5), xlabel="E", ylabel="I")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        P = m.ValueTracker(-0.8)
        def scene():
            q = dict(HY); q["p"] = P.get_value()
            ce, ci = nullcline_curves(ax, q, n=300, width=4)
            return m.VGroup(ce, ci, fp_dots(ax, q, n=700))
        sc = m.always_redraw(scene)
        lab = m.always_redraw(lambda: prose(f"$P = {P.get_value():+.2f}$", font_size=34).move_to(pt(3.6, 1.8)))
        self.add(sc, lab)
        self.next_slide("low P")
        self.play(P.animate.set_value(0.8), run_time=7, rate_func=m.linear)
        t = prose("at each tangency two crossings\ncollide and vanish: a fold\n(saddle-node), exactly as\nfor one population", font_size=26, color=YELLOW).move_to(pt(3.6, -0.6))
        self.play(m.FadeIn(t))
        self.play(P.animate.set_value(-0.8), run_time=7, rate_func=m.linear)
        self.wait(BEAT)
        self.next_slide("folds")
        self.clear()

    def loop(self):
        d = data("ch07_fig5")
        h = heading("Wilson & Cowan's Figure 5: a hysteresis loop")
        ax = plane((-0.8, 0.8, 0.4), (0, 0.5, 0.25), width=8.4, height=4.4, at=pt(-1.4, -0.2), xlabel="P", ylabel="E^*")
        eg = np.linspace(-0.02, Wl.wc_emax(HY) - 1e-3, 3000)
        Pb, Ib, tr, det = Wl.wc_branch_in_P(HY, eg)
        stab = (tr < 0) & (det > 0)
        segs = m.VGroup()
        cur = []
        for k in range(len(eg)):
            if stab[k] and np.isfinite(Pb[k]):
                cur.append((Pb[k], eg[k]))
            elif cur:
                segs.add(curve(ax, np.array(cur), color=INK, width=4)); cur = []
        if cur:
            segs.add(curve(ax, np.array(cur), color=INK, width=4))
        un = ~stab & np.isfinite(Pb)
        dash = m.DashedVMobject(curve(ax, np.column_stack([Pb[un], eg[un]]), color=INK, width=2.5), num_dashes=30)
        self.play(m.FadeIn(h), m.Create(ax), m.Create(segs), m.Create(dash), run_time=1.6)
        self.next_slide("S curve")
        X = np.column_stack([d["P"], d["E"]])[::20]
        self.trace(ax, X, color=MAGENTA, run_time=8, width=3)
        t = prose("up: stay at rest until rest is destroyed (fold at $P = 0.30$), then jump.\ndown: stay active until the active state is destroyed ($P = -0.40$).", font_size=22, color=YELLOW).to_edge(m.DOWN, buff=0.12)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("hysteresis")
        self.clear()
