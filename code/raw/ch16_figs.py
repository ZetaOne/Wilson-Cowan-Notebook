"""Chapter 16 figure: a family tree of activity equations (all the routes in the book).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch16_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import figkit as K

BOX = {
    "mp": (1.0, 6.0, "McCulloch–Pitts\nthreshold logic (1943)", K.BLUE),
    "sr": (1.0, 4.6, "Shimbel–Rapoport\nstatistics (1948)", K.BLUE),
    "be": (1.0, 3.2, "Beurle\nexcitatory field (1956)", K.BLUE),
    "gr": (1.0, 1.8, "Griffith\ngain + inhibition (1963)", K.BLUE),
    "gb": (4.2, 6.0, "Grossberg STM\n(1966–)", K.BLUE),
    "wc": (4.2, 3.6, "Wilson–Cowan\n$\\tau\\dot a = -a + (1-ra) f(Wa + I)$", K.ACC2),
    "fi": (4.2, 1.6, "neural fields\nWC 1973, Amari 1977", K.ACC2),
    "cg": (7.4, 6.0, "Cohen–Grossberg, Hopfield\nenergy, memory (1982–84)", K.ORANGE),
    "ge": (7.4, 4.6, "Gerstner\nspike response (1995)", K.ORANGE),
    "mf": (7.4, 3.2, "spiking mean field\nKlimontovich, MPR", K.ORANGE),
    "bm": (7.4, 1.8, "beyond mean field\n$1/N$ loops, effective action", K.ORANGE),
    "pat": (4.2, 0.2, "patterns, hallucinations\nErmentrout–Cowan 1979", K.ACC2),
}
EDGES = [("mp", "sr"), ("sr", "be"), ("be", "gr"), ("gr", "wc"), ("be", "wc"), ("gb", "wc"), ("gb", "cg"),
         ("wc", "fi"), ("fi", "pat"), ("wc", "ge"), ("wc", "mf"), ("mf", "bm"), ("wc", "cg"), ("gr", "gb")]


def family():
    fig, ax = plt.subplots(figsize=(12.6, 6.6))
    for k, (x, y, txt, col) in BOX.items():
        ax.add_patch(FancyBboxPatch((x - 1.25, y - 0.45), 2.5, 0.9, boxstyle="round,pad=0.04", fc=col, alpha=0.12, ec=col, lw=1.8))
        ax.text(x, y, txt, ha="center", va="center", fontsize=9.6, color=K.INK)
    for a, b in EDGES:
        xa, ya = BOX[a][:2]; xb, yb = BOX[b][:2]
        if abs(xa - xb) < 0.1:                       # same column: bottom edge -> top edge
            pa = (xa, ya - 0.5 * (1 if yb < ya else -1)); pb = (xb, yb + 0.5 * (1 if yb < ya else -1))
        else:                                        # neighbouring columns: side edge -> side edge
            sgn = 1 if xb > xa else -1
            pa = (xa + 1.3 * sgn, ya); pb = (xb - 1.3 * sgn, yb)
        ax.annotate("", pb, pa, arrowprops=dict(arrowstyle="-|>", color=K.GREY, lw=1.3, shrinkA=0, shrinkB=0))
    ax.text(1.0, 7.0, "before (Ch. 10)", ha="center", color=K.BLUE, fontsize=12)
    ax.text(4.2, 7.0, "the equations (Ch. 4–9, 11)", ha="center", color=K.ACC2, fontsize=12)
    ax.text(7.4, 7.0, "after and beyond (Ch. 11–15)", ha="center", color=K.ORANGE, fontsize=12)
    ax.set_xlim(-0.6, 9.0); ax.set_ylim(-0.6, 7.4); ax.axis("off")
    K.save(fig, "ch16_family", wide=True)


if __name__ == "__main__":
    family()
