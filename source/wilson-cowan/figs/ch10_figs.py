"""Chapter 10 figures: before Wilson and Cowan (McCulloch-Pitts, Shimbel-Rapoport, Beurle, Griffith).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch10_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import wc_lib as W
import figkit as K

MILESTONES = [
    (1943, "McCulloch & Pitts", "threshold neurons compute logic"),
    (1948, "Shimbel & Rapoport", "statistical theory\nof the nervous system"),
    (1956, "Beurle", "first neural field\n(excitatory only)"),
    (1963, "Griffith", "inhibition stabilises activity;\nreaction–diffusion field"),
    (1966, "Grossberg", "continuous memory\nmodels (STM)"),
    (1972, "Wilson & Cowan", "E and I populations"),
    (1973, "Wilson & Cowan", "the spatial version"),
    (1975, "Feldman & Cowan", "derivation under\nquasi-stationarity"),
    (1977, "Amari", "local excitation,\nlateral inhibition"),
    (1983, "Cohen & Grossberg", "Lyapunov function"),
    (1995, "Gerstner", "spike-response formalism"),
    (2007, "Buice, Chow, Cowan", "beyond mean field:\nfluctuations"),
]


def timeline():
    fig, ax = plt.subplots(figsize=(12.6, 5.6))
    ax.axhline(0, color=K.INK, lw=2)
    levels = {1943: 1.0, 1948: -1.0, 1956: 1.0, 1963: -1.0, 1966: 1.9, 1972: -1.9, 1973: 2.8, 1975: -2.8,
              1977: 1.0, 1983: -1.0, 1995: 1.0, 2007: -1.0}
    for k, (yr, who, what) in enumerate(MILESTONES):
        h = levels[yr]; up = 1 if h > 0 else -1
        xt = yr + {1972: -4.5, 1975: 2.0}.get(yr, 0)
        col = K.ACC2 if "Wilson" in who else (K.BLUE if yr < 1972 else K.ORANGE)
        ax.plot([yr, yr], [0, h - 0.08 * up], color=col, lw=1.2)
        ax.plot(yr, 0, "o", color=col, ms=7, zorder=5)
        ax.text(xt, h, f"{yr}  {who}\n{what}", ha="center", va="bottom" if up > 0 else "top", fontsize=8.6, color=col)
    ax.set_xlim(1936, 2014); ax.set_ylim(-3.9, 3.9); ax.axis("off")
    ax.set_title("milestones on the way to (and beyond) the activity equations (after the review's Table 1)")
    K.save(fig, "ch10_timeline", wide=True)


def mcculloch_pitts():
    """Threshold units as logic gates: output 1 if  sum w_i x_i >= h."""
    fig, axs = plt.subplots(1, 3, figsize=(12.0, 3.8))
    gates = [("AND", [1, 1], 2), ("OR", [1, 1], 1), ("NOT", [-1], 0)]
    for ax, (name, w, h) in zip(axs, gates):
        ax.add_patch(Circle((2.2, 1.0), 0.45, fc=K.ACC2, alpha=0.15, ec=K.ACC2, lw=2))
        ax.text(2.2, 1.0, f"$h={h}$", ha="center", va="center", fontsize=12)
        ys = [1.6, 0.4] if len(w) == 2 else [1.0]
        for y, wi, lab in zip(ys, w, ["$x_1$", "$x_2$"]):
            ax.add_patch(FancyArrowPatch((0.5, y), (1.75, 1.0 + (y - 1.0) * 0.3), arrowstyle="-|>" if wi > 0 else "-[",
                                         mutation_scale=14, lw=1.8, color=K.ACC2 if wi > 0 else K.BLUE))
            ax.text(0.35, y, lab, ha="right", va="center", fontsize=13)
            ax.text(1.05, y + (0.12 if y >= 1 else -0.18), f"$w={wi:+d}$", fontsize=10, color=K.GREY)
        ax.add_patch(FancyArrowPatch((2.65, 1.0), (3.4, 1.0), arrowstyle="-|>", mutation_scale=14, lw=1.8, color=K.INK))
        ax.text(3.5, 1.0, "$y$", va="center", fontsize=13)
        # truth table
        rows = [(a, b) for a in (0, 1) for b in (0, 1)] if len(w) == 2 else [(0,), (1,)]
        txt = ("$x_1\\ x_2\\ |\\ y$\n" if len(w) == 2 else "$x\\ |\\ y$\n")
        for r in rows:
            y = int(sum(wi * xi for wi, xi in zip(w, r)) >= h)
            txt += "  ".join(str(v) for v in r) + f"  |  {y}\n"
        ax.text(4.2, 1.0, txt, va="center", fontsize=10.5, family="monospace")
        ax.set_xlim(0, 5.6); ax.set_ylim(0, 2.1); ax.axis("off"); ax.set_title(name)
    fig.suptitle("McCulloch–Pitts units: fire ($y = 1$) when $\\sum_i w_i x_i \\geq h$", fontsize=12.5)
    fig.tight_layout()
    K.save(fig, "ch10_mcp", wide=True)


BEURLE = """# Beurle: purely excitatory, a cell needs q coincident inputs (Hill-type accelerating gain), refractory factor
g(a)=(k*a)^q/(1+(k*a)^q)
a'=-a+(1-a)*g(a)
par k=4,q=4
init a=0.1
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.02,total=15
done
"""
GRIFFITH = """# Griffith: a sigmoidal gain with a spontaneous level; stable low activity is possible
g(a)=1/(1+exp(-b*(w*a-th)))
a'=-a+(1-a)*g(a)
par b=8,w=1.6,th=0.45
init a=0.1
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.02,total=15
done
"""


def beurle_griffith():
    fig, axs = plt.subplots(2, 2, figsize=(11.4, 7.6))
    aa = np.linspace(0, 0.6, 600)
    for col, (txt, name, gfun) in enumerate([
            (BEURLE, "Beurle (1956): excitation only", lambda a: (4 * a) ** 4 / (1 + (4 * a) ** 4)),
            (GRIFFITH, "Griffith (1963): a stable spontaneous state", lambda a: 1 / (1 + np.exp(-8 * (1.6 * a - 0.45))))]):
        ax = axs[0, col]
        rhs = -aa + (1 - aa) * gfun(aa)
        ax.plot(aa, rhs, color=K.INK, lw=2.2)
        ax.axhline(0, color=K.GREY, lw=0.8)
        z = np.where(np.diff(np.sign(rhs)) != 0)[0]
        pts = [aa[j] for j in z]
        if rhs[0] == 0 or abs(rhs[0]) < 1e-9:
            pts = [0.0] + pts
        for p in pts:
            j = min(int(np.searchsorted(aa, p)) + 1, len(aa) - 2)
            slope = (rhs[j + 1] - rhs[j - 1]) / (aa[j + 1] - aa[j - 1]) if p > 0 else -1
            ax.plot(p, 0, "o", ms=10, mfc=K.ACC if slope < 0 else "white", mec=K.INK, mew=1.6, zorder=6)
        # flow arrows on the axis
        for xa in np.linspace(0.03, 0.57, 10):
            v = np.interp(xa, aa, rhs)
            ax.annotate("", (xa + 0.025 * np.sign(v), 0), (xa, 0), arrowprops=dict(arrowstyle="-|>", color=K.ORANGE, lw=1.4))
        ax.set_xlabel("activity $A$"); ax.set_ylabel("$\\dot A = -A + (1 - A)\\,g(A)$"); ax.set_title(name)
        m = W.load_text(txt)
        ax = axs[1, col]
        for a0 in np.linspace(0.0, 0.5, 11):
            m.set(a=float(a0)); tr = m.run(total=15, dt=0.02)
            ax.plot(tr.t, tr["a"], color=plt.cm.viridis(a0 / 0.5), lw=1.4)
        ax.set_xlabel("time"); ax.set_ylabel("$A(t)$")
        ax.set_title("activity dies or saturates" if col == 0 else "small activity settles at a low level")
        print(name, "fixed points", np.round(pts, 4))
    fig.tight_layout()
    K.save(fig, "ch10_beurle", wide=True)


def griffith_front():
    """Griffith's reaction-diffusion field  s_t = s_xx - mu s + f(s)  (bistable f): a travelling front."""
    N, L = 200, 100.0
    dx = L / N
    txt = f"""# Griffith reaction-diffusion field
f(s)=2/(1+exp(-6*(s-0.7)))
par mu=1,d={1 / dx ** 2}
s0'=d*(s1-s0)-mu*s0+f(s0)
s[1..{N - 2}]'=d*(s[j+1]-2*s[j]+s[j-1])-mu*s[j]+f(s[j])
s{N - 1}'=d*(s{N - 2}-s{N - 1})-mu*s{N - 1}+f(s{N - 1})
init s[0..15]=2
@ meth=rk4,dt=0.02,total=60,maxstor=10000
done
"""
    m = W.load_text(txt)
    tr = m.run(total=60, dt=0.02)
    t = np.asarray(tr.t)[::10]
    S = np.array([np.asarray(tr[f"s{j}"])[::10] for j in range(N)])
    xs = np.arange(N) * dx
    K.savedata("ch10_griffith", t=t, x=xs, s=S)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axs[0]
    im = ax.pcolormesh(t, xs, S, cmap="magma", shading="auto", rasterized=True)
    fig.colorbar(im, ax=ax, label="$s(x, t)$", pad=0.02)
    ax.set_xlabel("time"); ax.set_ylabel("position $x$"); ax.set_title("Griffith's field: excitation spreads as a front")
    ax = axs[1]
    for k, col in zip([0, len(t) // 4, len(t) // 2, 3 * len(t) // 4, len(t) - 1], plt.cm.viridis(np.linspace(0, 0.9, 5))):
        ax.plot(xs, S[:, k], color=col, lw=2, label=f"$t = {t[k]:.0f}$")
    ax.set_xlabel("position $x$"); ax.set_ylabel("$s$"); ax.legend(fontsize=9); ax.set_title("snapshots: a profile of fixed shape moving right")
    fig.tight_layout()
    K.save(fig, "ch10_griffith", wide=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["timeline", "mcculloch_pitts", "beurle_griffith", "griffith_front"]
    for w in which:
        globals()[w]()
