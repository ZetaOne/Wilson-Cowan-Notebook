"""Figure helpers for the Wilson–Cowan book: one light, print-friendly style;
PNG figures and GIF animations registered in figs/manifest.json together
with the script that made them (the book links each figure to its code)."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BOOK = ROOT / "rendered-anims" / "wilson-cowan" / "book"
FIGS = BOOK / "figs"
FIGS.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "rendered-anims" / "wilson-cowan" / "data"
DATA.mkdir(parents=True, exist_ok=True)
MANIFEST = FIGS / "manifest.json"

# palette (shared with the decks)
INK = "#1d232b"
CYCLE = "#111111"
ACC = "#0e7c86"     # teal
ACC2 = "#b0306a"    # magenta
ORANGE = "#d9822b"
BLUE = "#2f6db5"
GREEN = "#3f8f3a"
GREY = "#9aa3ad"
NULL_X = "#2e9d57"  # x-nullcline (green, as in the paper)
NULL_Y = "#d23c3c"  # y-nullcline (red)
# cyan -> magenta, the paper's colouring of isochrons by phase
PHASE_CMAP = LinearSegmentedColormap.from_list("cm", ["#00b7c7", "#4a6fd6", "#9a3fc4", "#e0339a"])
CYCLIC = plt.get_cmap("twilight_shifted")

plt.rcParams.update({
    # publication style: STIX serif text and maths (matches the book's serif body), thin clean axes
    "figure.dpi": 100, "savefig.dpi": 220, "font.size": 11, "font.family": "STIXGeneral",
    "mathtext.fontset": "stix", "axes.labelsize": 12, "axes.titlesize": 12, "axes.titleweight": "normal",
    "axes.edgecolor": "#3d4650", "axes.labelcolor": INK, "axes.linewidth": 0.8,
    "xtick.color": "#3d4650", "ytick.color": "#3d4650", "xtick.labelsize": 10, "ytick.labelsize": 10,
    "xtick.direction": "out", "ytick.direction": "out", "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlepad": 7,
    "legend.frameon": True, "legend.framealpha": 0.92, "legend.edgecolor": "#d0d5da", "legend.fancybox": False, "legend.fontsize": 9.5, "legend.handlelength": 1.8,
    "lines.linewidth": 1.6, "svg.fonttype": "path", "image.interpolation": "nearest",
})


def panel_labels(fig):
    """(a), (b), ... at the top left of every data axes of a multi-panel figure."""
    axs = [a for a in fig.axes if a.get_label() != "<colorbar>" and a.get_visible()]
    for a in axs:                                   # sentence case for panel titles
        t = a.get_title()
        if t and t[0].islower():
            a.set_title(t[0].upper() + t[1:])
    if len(axs) < 2:
        return
    for k, a in enumerate(axs):
        a.text(-0.02, 1.02, f"({chr(97 + k)})", transform=a.transAxes, ha="right", va="bottom",
               fontsize=13, fontweight="bold", family="STIXGeneral")


def _script():
    for fr in inspect.stack():
        p = Path(fr.filename)
        if p.parent.name == "figs" and p.suffix == ".py":
            return p.name
    return None


def _register(name, entry):
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    entry.setdefault("script", _script())
    man[name] = entry
    MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))


def save(fig, name, wide=False, tight=True, labels=True):
    """Vector SVG for the book (crisp on screen and in the PDF) plus a 220-dpi PNG."""
    if labels:
        panel_labels(fig)
    kw = dict(bbox_inches="tight", pad_inches=0.04) if tight else {}
    fig.savefig(FIGS / f"{name}.svg", facecolor="white", **kw)
    fig.savefig(FIGS / f"{name}.png", facecolor="white", **kw)
    plt.close(fig)
    _register(name, {"file": f"{name}.svg", "png": f"{name}.png", "wide": wide})
    print("fig", name)


def save_gif(fig, update, frames, name, fps=20, still_frame=-1, wide=False, dpi=90, still_draw=None):
    """Animate with update(i) over range(frames); also save a still PNG for print."""
    anim = FuncAnimation(fig, update, frames=frames, blit=False)
    g = FIGS / f"{name}.gif"
    anim.save(g, writer=PillowWriter(fps=fps), dpi=dpi, savefig_kwargs={"facecolor": "white"})
    k = frames + still_frame if still_frame < 0 else still_frame
    update(k)
    if still_draw is not None:          # custom still for print (e.g. several snapshots at once)
        still_draw()
    s = FIGS / f"{name}_still.png"
    fig.savefig(s, facecolor="white", dpi=220, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    _register(name, {"file": s.name, "gif": g.name, "still": s.name, "wide": wide})
    print("gif", name)


def savedata(name, **arrays):
    np.savez_compressed(DATA / f"{name}.npz", **arrays)


def loaddata(name):
    return dict(np.load(DATA / f"{name}.npz", allow_pickle=True))


def arrow_on(ax, X, i, color, size=12, lw=0):
    """Small arrowhead on a polyline X at index i, pointing along the flow."""
    i = int(i) % (len(X) - 1)
    ax.annotate("", xy=X[i + 1], xytext=X[i],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=size))


def streams(ax, F, xlim, ylim, n=24, color="#c3c9d0", density=1.1, lw=0.7, scale=(1, 1)):
    xs = np.linspace(*xlim, n); ys = np.linspace(*ylim, n)
    XX, YY = np.meshgrid(xs, ys)
    U, V = F(np.array([XX, YY]))
    ax.streamplot(xs, ys, U * scale[0], V * scale[1], color=color, density=density, linewidth=lw, arrowsize=0.8)


BOX = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85)   # behind in-plot text
