"""Deck for Chapter 11: Short-term memory models."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck11(GeoDeck):
    chapter = "Chapter 11"
    title = "Short-Term Memory Models"
    subtitle = "Grossberg, Cohen–Grossberg Lyapunov functions and Hopfield"

    def construct(self):
        self.title_card()
        self.steps("Grossberg's STM equations", [
            (r"\tau\dot s_i = -s_i + \sum_j w_{ij}f_j(s_j) + I_i", "additive STM: the input form of Wilson–Cowan"),
            (r"\dot x_i = -Ax_i + (B - x_i)[\text{exc}]_i - (x_i + C)[\text{inh}]_i", "shunting: activity bounded between $-C$ and $B$"),
        ], eq_size=34)
        self.landscape()
        self.derivation()
        self.asym()
        self.hopfield()
        self.recap(["Symmetric weights: an energy that never increases",
                    "Every trajectory rolls into a valley: steady states only",
                    "Hebbian weights put memories at valley bottoms",
                    "Asymmetric E–I coupling: no landscape, rhythms are possible"])

    def landscape(self):
        d = data("ch11_energy")
        g, E, P = d["g"], d["E"], d["paths"]
        h = heading("Symmetric weights: the state rolls downhill")
        im = image_from_array(E, cmap="Blues_r", height=5.4).move_to(pt(-2.6, -0.5))
        ax = plane((-6, 6, 3), (-6, 6, 3), width=im.width, height=im.height, at=im.get_center(), xlabel="u_1", ylabel="u_2")
        self.play(m.FadeIn(h), m.FadeIn(im), m.Create(ax), run_time=1.2)
        t = prose("colour = energy $L$\n(dark = low)\ntwo valleys:\nunit 1 on, unit 2 off,\nor the reverse", font_size=26).move_to(pt(4.2, 0.6))
        self.play(m.FadeIn(t))
        self.next_slide("landscape")
        cols = [ORANGE, YELLOW, MAGENTA, RED, TEAL, GREEN, BLUE, ORANGE, YELLOW, MAGENTA]
        k = m.ValueTracker(2)
        paths = m.always_redraw(lambda: m.VGroup(*[curve(ax, P[j, : max(2, int(k.get_value())), 1:3], color=cols[j], width=3) for j in range(len(P))]))
        self.add(paths)
        self.play(k.animate.set_value(P.shape[1] - 1), run_time=6, rate_func=m.linear)
        self.wait(HOLD)
        self.next_slide("roll down")
        self.clear()

    def derivation(self):
        self.steps("Why the energy never increases (needs $w_{ij} = w_{ji}$)", [
            (r"L = -\tfrac12\sum_{ij}w_{ij}a_ia_j - \sum_i I_ia_i + \sum_i\int_0^{a_i}f^{-1}", "the Cohen–Grossberg / Hopfield energy"),
            (r"\frac{\partial L}{\partial a_i} = -\sum_j w_{ij}a_j - I_i + u_i = -\tau\dot u_i", "symmetry joins the two halves of the double sum"),
            (r"\frac{dL}{dt} = \sum_i \frac{\partial L}{\partial a_i}\,f'(u_i)\,\dot u_i", "chain rule, $\\dot a_i = f'(u_i)\\dot u_i$"),
            (r"\frac{dL}{dt} = -\tau\sum_i f'(u_i)\,\dot u_i^{\,2} \le 0", "$f' > 0$ and squares are positive"),
        ], eq_size=34)

    def asym(self):
        d = data("ch11_asym")
        h = heading("Asymmetric E–I weights: no landscape, a cycle")
        ax = plane((0, 5, 1), (0, 5, 1), width=4.2, height=4.2, at=pt(-3.6, -0.1), xlabel="s_E", ylabel="s_I")
        ax2 = plane((0, 60, 20), (-5, 1, 2), width=5.4, height=3.4, at=pt(3.4, -0.1), xlabel="t", ylabel="L")
        self.play(m.FadeIn(h), m.Create(ax), m.Create(ax2), run_time=1.0)
        X = np.column_stack([d["ue"], d["ui"]])[::10]
        L = np.column_stack([d["t"], d["L"]])[::10]
        self.play(m.Create(curve(ax, X, color=MAGENTA, width=3)), m.Create(curve(ax2, L, color=BLUE, width=3)), run_time=4)
        t = prose("$E$ excites $I$ ($+c_3$) but $I$ inhibits $E$ ($-c_2$):\nthe ‘energy’ rises and falls, so the flow can circulate", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.15)
        self.play(m.FadeIn(t))
        self.wait(HOLD)
        self.next_slide("asymmetric")
        self.clear()

    def hopfield(self):
        d = data("ch11_hopfield")
        t, U, xi, cue, ov = d["t"], d["U"], d["xi"], d["cue"], d["overlaps"]
        h = heading("Hopfield: memories are valleys (64 units, XPPAUT)")
        mem = m.Group(*[image_from_array(xi[k].reshape(8, 8), cmap="Greys", vmin=-1, vmax=1, height=1.6, origin_lower=False) for k in range(3)]).arrange(m.RIGHT, buff=0.3).move_to(pt(-3.6, 1.6))
        lm = prose("stored patterns ($w_{ij} = \\frac1N\\sum_\\mu\\xi^\\mu_i\\xi^\\mu_j$)", font_size=22, color=MUTED).next_to(mem, m.DOWN, buff=0.15)
        self.play(m.FadeIn(h), m.FadeIn(mem), m.FadeIn(lm), run_time=1.0)
        k = m.ValueTracker(0)
        def state():
            j = int(k.get_value())
            img = cue if j == 0 else np.tanh(4 * U[:, j])
            return image_from_array(img.reshape(8, 8), cmap="Greys", vmin=-1, vmax=1, height=3.2, origin_lower=False).move_to(pt(3.6, 0.3))
        st = m.always_redraw(state)
        lab = m.always_redraw(lambda: prose(f"$t = {t[int(k.get_value())]:.1f}$" + ("  (noisy cue, 18 pixels wrong)" if int(k.get_value()) == 0 else ""), font_size=24).move_to(pt(3.6, 2.3)))
        ax = plane((0, 4, 1), (-0.4, 1, 0.5), width=5.4, height=2.4, at=pt(-3.4, -2.2), xlabel="t", ylabel="m_\\mu")
        cols = [MAGENTA, BLUE, ORANGE]
        ovc = m.always_redraw(lambda: m.VGroup(*[curve(ax, np.column_stack([t, ov[q]])[: max(2, int(k.get_value()) + 1)], color=cols[q], width=3) for q in range(3)]))
        self.add(st, lab)
        self.play(m.Create(ax))
        self.add(ovc)
        self.next_slide("cue")
        self.play(k.animate.set_value(np.searchsorted(t, 4.0)), run_time=6, rate_func=m.linear)
        msg = prose("the state rolls into the valley\nof pattern 1: overlap $\\to 1$", font_size=24, color=YELLOW).move_to(pt(3.6, -2.5))
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("recall")
        self.clear()
