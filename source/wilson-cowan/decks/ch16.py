"""Deck for Chapter 16: What it means and what came next."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import manimgx as m
from deckkit import *  # noqa: F401,F403


class Deck16(GeoDeck):
    chapter = "Chapter 16"
    title = "What It Means and What Came Next"
    subtitle = "The legacy of the Wilson–Cowan equations"

    def construct(self):
        self.title_card()
        self.show_figure("ch16_family", "Many roads to the same equation",
                         "A gain function, a linear sum of inputs, first-order dynamics: from every starting point.")
        self.pictures()
        self.bullets("What the equations leave out, and the remedies", [
            "quasi-stationarity: volleys and fast transients $\\to$ spike response, exact MPR mean field",
            "mean field factorisation: correlations ignored, no dissipation $\\to$ moment hierarchies",
            "infinite size: fluctuations $\\propto 1/N$, metastability $\\to$ loop expansion, effective action"], font_size=28)
        self.quote()

    def pictures(self):
        h = heading("The geometric habit: draw the picture first")
        rows = [("one population", "a flow on a line: where does the curve cross zero?"),
                ("two populations", "a flow in a plane: how do the nullclines cross?"),
                ("a field", "Fourier modes: where does $\\lambda(k)$ first cross zero?"),
                ("spiking neurons", "a density on a circle: where does it pile up?"),
                ("a finite network", "a cloud in a landscape: how deep are the wells?")]
        self.play(m.FadeIn(h), run_time=0.6)
        g = m.VGroup()
        for k, (a, b) in enumerate(rows):
            r = m.VGroup(prose(a, font_size=28, color=TEAL), prose(b, font_size=26)).arrange(m.RIGHT, buff=0.5)
            g.add(r)
        g.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.45).move_to(pt(0, -0.4))
        for r in g:
            self.play(m.FadeIn(r, shift=m.RIGHT * 0.2), run_time=0.7)
            self.wait(0.8)
        self.wait(HOLD)
        self.next_slide("habit")
        self.clear()

    def quote(self):
        h = heading("The review's last words")
        q = prose("“Correlations are deliberately ignored to make the equations tractable,\nbut given that they are omnipresent in the brain, there has been ongoing\neffort to account for them. Nonetheless, we predict that forty-seven years\nfrom now, the Wilson–Cowan equations will still have great utility.”", font_size=28, width=12.4).move_to(pt(0, 0.2))
        c = prose("— C. C. Chow and Y. Karimipanah (2020)", font_size=24, color=MUTED).next_to(q, m.DOWN, buff=0.4).align_to(q, m.RIGHT)
        self.play(m.FadeIn(h), m.FadeIn(q), run_time=1.6)
        self.play(m.FadeIn(c))
        self.wait(LONG)
        self.next_slide("quote")
        self.clear()
