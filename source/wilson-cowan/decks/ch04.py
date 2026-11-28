"""Deck for Chapter 4: Deriving the Wilson–Cowan equations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck04(GeoDeck):
    chapter = "Chapter 4"
    title = "Deriving the Equations"
    subtitle = "From sensitive fractions to two coupled ODEs (Wilson & Cowan 1972)"

    def construct(self):
        self.title_card()
        self.show_figure("ch04_circuit", "Two populations, four connections, two inputs",
                         "Arrows excite ($c_1$, $c_3$); bars inhibit ($c_2$, $c_4$). Dale's principle: each cell is E or I.")
        self.input_steps()
        self.integral_steps()
        self.result()
        self.equiv_steps()
        self.show_figure("ch04_equiv", "Activities or inputs: the same orbit",
                         "WC form integrated, its input computed (thick); STM form integrated (dashed).")
        self.recap(["Separate excitatory and inhibitory populations, connections $c_1\\dots c_4$, inputs $P, Q$",
                    "Fraction firing = sensitive fraction $\\times$ fraction above threshold",
                    "Coarse-grain in time (quasi-stationarity): two ODEs",
                    "The inputs $s = \\sum w a + I$ of a WC network obey the STM equations"])

    def input_steps(self):
        self.steps("Step 1: the input to an excitatory cell", [
            (r"c_1 E - c_2 I + P", "excitation from $E$, inhibition from $I$, outside drive"),
            (r"x_E(t) = \int_{-\infty}^{t}\alpha(t-t')\,\big[c_1E - c_2I + P\big](t')\,dt'", "PSPs linger: weight recent history by $\\alpha$"),
            (r"\mathcal S_E(x_E)", "fraction of sensitive cells pushed past threshold (Chapter 3)"),
        ], eq_size=36)

    def integral_steps(self):
        self.steps("Step 2: coarse-grain in time", [
            (r"E(t+\tau) = \Big[1 - \int_{t-r}^{t}E\Big]\,\mathcal S_E(x_E)", "exact under mean field, but an integral equation"),
            (r"\int_{t-r}^{t}E\,dt' \to r\,E(t)", "area $\\approx$ height $\\times$ width (slowly varying $E$)"),
            (r"\int_{-\infty}^{t}\alpha(t-t')E(t')\,dt' \to k\,E(t)", "same idea for the PSP memory"),
            (r"E(t+\tau) \approx E(t) + \tau\,\dot E(t)", "Taylor expand the delay"),
        ], eq_size=36)

    def result(self):
        h = heading("The Wilson–Cowan equations (1972)")
        e1 = tex(r"\tau_E\,\dot E = -E + (k_E - r_E E)\,\mathcal S_E(c_1E - c_2I + P)", font_size=40).move_to(pt(0, 1.3))
        e2 = tex(r"\tau_I\,\dot I = -I + (k_I - r_I I)\,\mathcal S_I(c_3E - c_4I + Q)", font_size=40).move_to(pt(0, 0.2))
        self.play(m.FadeIn(h), m.Write(e1), m.Write(e2), run_time=2.0)
        self.next_slide("equations")
        b1 = m.Brace(e1[0], m.DOWN, color=YELLOW)
        t = prose("each activity relaxes towards (sensitive fraction) $\\times$ (gain of its input)", font_size=28, color=YELLOW).move_to(pt(0, -1.6))
        self.play(m.FadeIn(t))
        t2 = prose("minus signs on $c_2$, $c_4$: inhibition subtracts from the input", font_size=26, color=MUTED).move_to(pt(0, -2.5))
        self.play(m.FadeIn(t2))
        self.wait(HOLD)
        self.next_slide("reading")
        self.clear()

    def equiv_steps(self):
        self.steps("Activities or inputs? Two forms of the same dynamics", [
            (r"\dot a_i = -a_i + f_i\Big(\sum_j w_{ij}a_j + I_i\Big)", "Wilson–Cowan form (with $r = 0$, $\\tau = 1$)"),
            (r"s_i := \sum_j w_{ij}a_j + I_i", "define the input of population $i$"),
            (r"\dot s_i = \sum_j w_{ij}\,\dot a_j", "differentiate; $I_i$ constant"),
            (r"= \sum_j w_{ij}\big[-a_j + f_j(s_j)\big]", "insert the WC equation for each $\\dot a_j$"),
            (r"\dot s_i = -s_i + \sum_j w_{ij}f_j(s_j) + I_i", "since $\\sum_j w_{ij}a_j = s_i - I_i$: the STM form"),
        ], eq_size=34, gap=0.95)
