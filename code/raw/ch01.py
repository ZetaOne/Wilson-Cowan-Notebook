"""Deck for Chapter 1: Why populations?"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck01(GeoDeck):
    chapter = "Chapter 1"
    title = "Why Populations?"
    subtitle = "Coarse-graining, mean fields, and the population rate"

    def construct(self):
        self.title_card()
        self.raster()
        self.coarse()
        self.gain()
        self.equation()
        self.relax()
        self.show_figure("ch01_raster", "The same network, as in the book",
                         "Top: three neurons. Middle: the raster. Bottom: the coarse-grained population rate.")
        self.recap(["A population's state can be summarised by one number: its activity (rate)",
                    "Coarse-graining: count spikes over many neurons and a short window",
                    "Mean field: each neuron feels only the average of the others",
                    "Activity equation: $\\tau\\dot a = -a + f(\\sum_j w a_j + I)$, relax towards the gain of the input"])

    def raster(self):
        d = data("ch01_net")
        sp = d["spikes"]
        sp = sp[sp[:, 0] < 100]
        h = heading("200 spiking neurons: each tick is one spike")
        ax = plane((0, 100, 20), (0, 200, 50), width=11.0, height=4.6, at=pt(0, -0.6), xlabel="t", ylabel="\\text{neuron}")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        stim = m.Rectangle(width=ax.c2p(70, 0)[0] - ax.c2p(30, 0)[0], height=ax.c2p(0, 200)[1] - ax.c2p(0, 0)[1],
                           fill_color=ORANGE, fill_opacity=0.12, stroke_width=0).move_to(ax.c2p(50, 100))
        lab = prose("input on", font_size=22, color=ORANGE).next_to(stim, m.UP, buff=0.1)
        self.play(m.FadeIn(stim), m.FadeIn(lab))
        k = m.ValueTracker(0.0)
        def ticks():
            sel = sp[sp[:, 0] <= k.get_value()]
            g = m.VGroup(*[m.Line(ax.c2p(t, j), ax.c2p(t, j + 3), color=INK, stroke_width=1.2) for t, j in sel[::2]])
            return g
        tk = m.always_redraw(ticks)
        self.add(tk)
        self.play(k.animate.set_value(100), run_time=7, rate_func=m.linear)
        self.remove(tk); tk = ticks(); self.add(tk)
        msg = prose("Individually: irregular. Together: the input clearly raises the activity.", font_size=26, color=YELLOW).to_edge(m.DOWN, buff=0.2)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("raster")
        self.clear()

    def coarse(self):
        d = data("ch01_net")
        sp = d["spikes"]
        h = heading("Coarse-graining: slide a window, count spikes")
        ax = plane((0, 100, 20), (0, 200, 50), width=11.0, height=3.0, at=pt(0, 1.0), xlabel="t", ylabel="\\text{neuron}", ticks=False)
        ticks = m.VGroup(*[m.Line(ax.c2p(t, j), ax.c2p(t, j + 3), color=m.GREY_B, stroke_width=1) for t, j in sp[::2] if t < 100])
        ax2 = plane((0, 100, 20), (0, 0.5, 0.25), width=11.0, height=2.2, at=pt(0, -2.3), xlabel="t", ylabel="a(t)")
        self.play(m.FadeIn(h), m.FadeIn(ax), m.FadeIn(ticks), m.Create(ax2), run_time=1.0)
        win = 2.0
        edges = np.arange(0, 100 - win, 0.5)
        rate = np.array([np.sum((sp[:, 0] >= e) & (sp[:, 0] < e + win)) / (200 * win) for e in edges])
        k = m.ValueTracker(0)
        box = m.always_redraw(lambda: m.Rectangle(width=ax.c2p(win, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, 200)[1] - ax.c2p(0, 0)[1],
                                                  stroke_color=MAGENTA, stroke_width=3).move_to(ax.c2p(edges[int(k.get_value())] + win / 2, 100)))
        line = m.always_redraw(lambda: curve(ax2, np.column_stack([edges + win / 2, rate])[: max(2, int(k.get_value()) + 1)], color=MAGENTA, width=3))
        self.add(box, line)
        self.play(k.animate.set_value(len(edges) - 1), run_time=7, rate_func=m.linear)
        msg = prose("spikes in the window $\\div$ (neurons $\\times$ window) = the population rate $a(t)$", font_size=24, color=YELLOW).next_to(ax2, m.UP, buff=0.05)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("coarse graining")
        self.clear()

    def gain(self):
        d = data("ch01_fi")
        h = heading("From input to rate: one neuron vs a population")
        ax = plane((-0.6, 1.0, 0.2), (0, 0.35, 0.1), width=8.0, height=4.6, at=pt(-1.4, -0.5), xlabel="I", ylabel="\\text{rate}")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        one = curve(ax, np.column_stack([d["Is"], d["one"]]), color=TEAL, width=4)
        pop = curve(ax, np.column_stack([d["xx"], d["pop"]]), color=MAGENTA, width=4)
        t1 = prose("one neuron: silent, then\nfiring rate $\\sqrt{I}/\\pi$\n(a sharp corner)", font_size=24, color=TEAL).move_to(pt(4.6, 1.2))
        self.play(m.Create(one), m.FadeIn(t1), run_time=1.6)
        self.next_slide("single")
        t2 = prose("many different neurons:\nthe corners are spread out,\nthe average is smooth: a sigmoid", font_size=24, color=MAGENTA).move_to(pt(4.6, -1.0))
        self.play(m.Create(pop), m.FadeIn(t2), run_time=1.6)
        self.wait(HOLD)
        self.next_slide("population")
        self.clear()

    def equation(self):
        self.steps("The activity equation, read piece by piece", [
            (r"\tau\,\dot a_i = -a_i + f\Big(\sum_j w_{ij}a_j + I_i\Big)", "the whole equation"),
            (r"\sum_j w_{ij}a_j + I_i", "input: weighted sum of other populations' activity plus outside drive"),
            (r"f(\,\cdot\,)", "gain: turns input into the rate it would sustain"),
            (r"-a_i + f(\dots)", "relax: $a$ moves towards that target"),
            (r"\tau", "how fast: the time constant"),
        ], eq_size=38)

    def relax(self):
        h = heading("Geometry of $\\dot a = (-a + \\text{target})/\\tau$: always head for the target")
        ax = plane((0, 8, 2), (0, 1, 0.5), width=9.0, height=4.4, at=pt(-0.8, -0.6), xlabel="t", ylabel="a")
        self.play(m.FadeIn(h), m.Create(ax), run_time=1.0)
        t = np.linspace(0, 8, 400)
        tgt = np.where(t < 4, 0.8, 0.2)
        a = np.empty_like(t); a[0] = 0.1
        for k in range(1, len(t)):
            a[k] = a[k - 1] + (t[k] - t[k - 1]) * (-a[k - 1] + tgt[k - 1])
        tl = curve(ax, np.column_stack([t, tgt]), color=ORANGE, width=3)
        lab = prose("target $f(\\text{input})$", font_size=24, color=ORANGE).next_to(ax.c2p(4, 0.8), m.UP, buff=0.1)
        self.play(m.Create(tl), m.FadeIn(lab))
        self.trace(ax, np.column_stack([t, a]), color=MAGENTA, run_time=4)
        msg = prose("exponential approach with time constant $\\tau$: no overshoot, no ringing", font_size=24, color=YELLOW).to_edge(m.DOWN, buff=0.25)
        self.play(m.FadeIn(msg))
        self.wait(HOLD)
        self.next_slide("relaxation")
        self.clear()
