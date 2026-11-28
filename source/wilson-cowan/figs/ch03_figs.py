"""Chapter 3 figures: where the sigmoid comes from.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch03_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from math import erf
import wc_lib as W
import figkit as K

x = np.linspace(0, 10, 800)


def gauss(z, m, s):
    return np.exp(-0.5 * ((z - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))


def thresholds():
    """f(x) = integral_0^x p(theta) dtheta: the fraction of cells whose threshold is below the input."""
    uni = gauss(x, 5, 1.2)
    bi = 0.5 * gauss(x, 3.2, 0.7) + 0.5 * gauss(x, 6.8, 0.7)
    fig, axs = plt.subplots(2, 2, figsize=(11, 6.4), sharex=True)
    for col, (p, name) in enumerate([(uni, "one group of cells (unimodal)"), (bi, "two groups of cells (bimodal)")]):
        cdf = np.cumsum(p) * (x[1] - x[0])
        ax = axs[0, col]
        ax.plot(x, p, color=K.INK, lw=2)
        k = x <= 4.2
        ax.fill_between(x[k], 0, p[k], color=K.ACC, alpha=0.35)
        ax.axvline(4.2, color=K.ACC2, lw=1.4)
        ax.text(4.3, p.max() * 0.85, "input $x$", color=K.ACC2, fontsize=11)
        ax.set_title(name); ax.set_ylabel("threshold density $p(\\theta)$")
        ax = axs[1, col]
        ax.plot(x, cdf, color=K.ACC2, lw=2.4)
        ax.plot(4.2, cdf[np.searchsorted(x, 4.2)], "o", color=K.ACC, ms=9, zorder=5)
        ax.set_xlabel("input $x$ (or threshold $\\theta$)"); ax.set_ylabel("$f(x)$ = shaded area")
        if col == 1:
            for xi in (3.2, 6.8):
                ax.plot(xi, cdf[np.searchsorted(x, xi)], "s", color=K.ORANGE, ms=7)
            ax.text(7.2, 0.45, "two inflection\npoints", color=K.ORANGE, fontsize=10)
    fig.tight_layout()
    K.save(fig, "ch03_thresholds", wide=True)


def area_gif():
    p = gauss(x, 5, 1.2); cdf = np.cumsum(p) * (x[1] - x[0])
    fig, axs = plt.subplots(2, 1, figsize=(6.6, 5.6), sharex=True)
    axs[0].plot(x, p, color=K.INK, lw=2); axs[0].set_ylabel("$p(\\theta)$")
    axs[0].set_title("the shaded area is the fraction of cells that fire")
    axs[1].plot(x, cdf, color=K.GREY, lw=1, ls=":")
    tr, = axs[1].plot([], [], color=K.ACC2, lw=2.4)
    dt, = axs[1].plot([], [], "o", color=K.ACC, ms=8)
    vl = axs[0].axvline(0, color=K.ACC2)
    axs[1].set_xlabel("input $x$"); axs[1].set_ylabel("$f(x)$"); axs[1].set_ylim(-0.03, 1.05)
    fills = []
    frames = 90

    def upd(i):
        xx = 10 * i / (frames - 1)
        for fobj in fills:
            fobj.remove()
        fills.clear()
        k = x <= xx
        fills.append(axs[0].fill_between(x[k], 0, p[k], color=K.ACC, alpha=0.35))
        vl.set_xdata([xx, xx])
        tr.set_data(x[k], cdf[k]); dt.set_data([xx], [cdf[k][-1] if k.any() else 0])
    K.save_gif(fig, upd, frames, "ch03_area", fps=15, still_frame=40)


def measured_gain():
    """An uncoupled population of theta-neurons with Gaussian-spread thresholds, driven by a common input x;
    the population rate against x, measured in XPPAUT, against the threshold-average formula."""
    N = 150
    rng = np.random.default_rng(5)
    shifts = np.sort(rng.normal(0.0, 0.3, N))
    lines = [f"par x=0"] + [f"par d{k+1}={shifts[k]:.6f}" for k in range(N)]
    lines += [f"th[1..{N}]'=1-cos(th[j])+(1+cos(th[j]))*(x-d[j])", f"init th[1..{N}]=0",
              "@ meth=cvode,tol=1e-8,atol=1e-8,dt=0.05,total=200,maxstor=100000,bound=1e8", "done"]
    m = W.load_text("\n".join(lines))
    xs = np.linspace(-0.8, 1.0, 25)
    rates = []
    for xv in xs:
        m.set(x=float(xv), **{f"th{k+1}": 0.0 for k in range(N)})
        tr = m.run(total=200, dt=0.05)
        th = np.column_stack([np.asarray(tr[f"th{k+1}"], float) for k in range(N)])
        half = len(th) // 2
        n = (np.floor((th[-1] + np.pi) / (2 * np.pi)) - np.floor((th[half] + np.pi) / (2 * np.pi))).sum()
        rates.append(n / N / 100)
    rates = np.array(rates)
    xx = np.linspace(-0.8, 1.0, 400)
    theory = np.array([np.mean(np.sqrt(np.clip(v - shifts, 0, None)) / np.pi) for v in xx])
    frac = np.array([np.mean(v > shifts) for v in xx])
    K.savedata("ch03_gain", xs=xs, rates=rates, xx=xx, theory=theory)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    axs[0].plot(xs, rates, "o", color=K.ACC, ms=6, label=f"{N} θ-neurons, measured in XPP")
    axs[0].plot(xx, theory, color=K.ACC2, lw=2, label="average of $\\sqrt{x-\\theta_i}/\\pi$")
    axs[0].set_xlabel("common input $x$"); axs[0].set_ylabel("population rate"); axs[0].legend(fontsize=9, loc="upper left")
    axs[0].set_title("population gain = average of single-cell f–I curves")
    axs[1].plot(xx, frac, color=K.INK, lw=2, label="fraction of cells above threshold")
    axs[1].plot(xx, 0.5 * (1 + np.vectorize(erf)(xx / (0.3 * np.sqrt(2)))), "--", color=K.ORANGE, lw=1.5, label="Gaussian CDF (erf)")
    axs[1].set_xlabel("common input $x$"); axs[1].set_ylabel("fraction"); axs[1].legend(fontsize=9, loc="upper left")
    axs[1].set_title("Wilson–Cowan's sigmoid: the fraction that fires")
    fig.tight_layout()
    K.save(fig, "ch03_gain", wide=True)


def refractory():
    """Wilson & Cowan (1972) Fig. 3: the integral equation with an explicit refractory period r
       E(t + tau) = [1 - int_{t-r}^{t} E dt'] S(x(t))      (their eq. 9, discretised)
    against the time-coarse-grained ODE  tau dE/dt = -E + (1 - r E) S(x)  (their eq. 10).
    The map is iterated in numpy (it is a discrete-time recursion, not an ODE)."""
    tau, r, dt = 1.0, 3.0, 0.01
    Sx = 0.3                                      # constant drive S(x) after a step at t = 0
    n_tau, n_r = int(tau / dt), int(r / dt)
    T = 30.0; n = int(T / dt)
    E = np.zeros(n)
    for k in range(n_tau, n):
        R = E[max(0, k - n_tau - n_r):k - n_tau].sum() * dt
        E[k] = (1 - R) * Sx
    t = np.arange(n) * dt
    # coarse-grained ODE, with XPPAUT
    m = W.load_text(f"""e'=(-e+(1-r*e)*sx)/tau
par r={r},sx={Sx},tau={tau}
init e=0
@ meth=cvode,tol=1e-10,atol=1e-10,dt=0.01,total=30
done""")
    tr = m.run(total=T, dt=0.01)
    K.savedata("ch03_refr", t=t, E=E, t2=np.asarray(tr.t), e2=np.asarray(tr["e"]))
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.plot(t, E, color=K.GREY, lw=1.6, label="integral equation with refractory period $r=3$ (eq. 9)")
    ax.plot(tr.t, tr["e"], color=K.ACC2, lw=2.4, label="coarse-grained ODE $\\tau\\dot E = -E + (1-rE)S$ (eq. 10)")
    ax.axhline(Sx / (1 + r * Sx), color=K.ACC, ls=":", lw=1.2, label="common steady state $S/(1+rS)$")
    ax.set_xlabel("time $t$ (units of $\\tau$)"); ax.set_ylabel("active fraction $E$"); ax.legend(fontsize=9, loc="lower right")
    ax.set_title("Wilson & Cowan's Figure 3: same steady state, smoother approach")
    K.save(fig, "ch03_refractory")
    print("steady states:", E[-1], tr["e"][-1], Sx / (1 + r * Sx))


if __name__ == "__main__":
    thresholds()
    area_gif()
    measured_gain()
    refractory()
