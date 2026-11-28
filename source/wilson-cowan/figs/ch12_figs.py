"""Chapter 12 figures: Gerstner's spike-response formalism and where rate models fail (fast transients).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch12_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

N = 300
ETA0, STEP, T0, TOT = -0.3, 1.0, 10.0, 40.0


def F_lor(eta, delta):
    """Steady firing rate of a population of uncoupled theta-neurons with Lorentzian excitabilities."""
    return np.sqrt(eta + np.sqrt(eta ** 2 + delta ** 2)) / (np.pi * np.sqrt(2))


def run_pop(delta, seed=2):
    txt, etas = W.theta_network(N=N, J=0.0, tau=1.0, eta0=ETA0, delta=delta, seed=seed,
                                stim=f"{STEP}*heav(t-{T0})")
    m = W.load_text(txt)
    tr = m.run(total=TOT, dt=0.01)
    t = np.asarray(tr.t, float)
    th = np.column_stack([np.asarray(tr[f"th{k}"], float) for k in range(1, N + 1)])
    k = np.floor((th + np.pi) / (2 * np.pi))
    idx = np.argwhere(np.diff(k, axis=0) > 0)
    sp = np.array([(t[i + 1], j) for i, j in idx])
    return t, sp


def rate(sp, width=0.2):
    edges = np.arange(0, TOT + width, width)
    h, _ = np.histogram(sp[:, 0], edges)
    return 0.5 * (edges[1:] + edges[:-1]), h / (N * width)


def rate_model(delta, tau=1.0):
    """first-order rate model  tau r' = -r + F(input)"""
    t = np.linspace(0, TOT, 4001)
    r = np.empty_like(t); r[0] = F_lor(ETA0, delta)
    dt = t[1] - t[0]
    for k in range(1, len(t)):
        drive = ETA0 + (STEP if t[k - 1] >= T0 else 0.0)
        r[k] = r[k - 1] + dt / tau * (-r[k - 1] + F_lor(drive, delta))
    return t, r


def transient():
    fig, axs = plt.subplots(2, 2, figsize=(12.0, 6.8), gridspec_kw={"height_ratios": [1, 1.1]}, sharex=True)
    out = {}
    for col, delta in enumerate([0.01, 0.2]):
        t, sp = run_pop(delta)
        tc, r = rate(sp)
        tm, rm = rate_model(delta)
        out[f"sp{col}"] = sp; out[f"r{col}"] = r; out[f"rm{col}"] = rm
        ax = axs[0, col]
        ax.plot(sp[:, 0], sp[:, 1], "|", ms=1.6, color=K.INK, mew=0.5)
        ax.axvline(T0, color=K.ORANGE, lw=1, ls="--")
        ax.set_ylim(0, N); ax.set_ylabel("neuron")
        ax.set_title(("nearly identical neurons ($\\Delta = 0.01$)" if col == 0 else "heterogeneous neurons ($\\Delta = 0.2$)"))
        ax = axs[1, col]
        ax.plot(tc, r, color=K.ACC2, lw=1.6, label="spiking population (XPPAUT, 300 θ-neurons)")
        ax.plot(tm, rm, color=K.BLUE, lw=2, ls="--", label="rate model $\\dot r = -r + F(\\eta)$")
        ax.axhline(F_lor(ETA0 + STEP, delta), color=K.GREY, lw=0.8, ls=":")
        ax.set_xlabel("time"); ax.set_ylabel("population rate $A(t)$"); ax.legend(fontsize=8.5, loc="upper right")
        ax.set_ylim(0, 3.5 if col == 0 else 0.8)
        print("delta", delta, "late rate", r[tc > 30].mean(), "theory", F_lor(ETA0 + STEP, delta), "peak", r.max())
    out["tc"] = tc; out["tm"] = tm
    K.savedata("ch12_transient", **out)
    fig.tight_layout()
    K.save(fig, "ch12_transient", wide=True)


def kernels():
    """Schematic of the spike-response model: u(t) = eta(t - t_hat) + sum_j w_j kappa(t - t_j); escape noise."""
    t = np.linspace(0, 60, 3000)
    eta = lambda s: np.where(s > 0, -6 * np.exp(-s / 4), 0)
    kap = lambda s: np.where(s > 0, (s / 2) * np.exp(1 - s / 2), 0)
    rng = np.random.default_rng(5)
    tin = np.sort(rng.uniform(2, 58, 40))
    u = np.zeros_like(t); spikes = []
    th = 4.0
    last = -1e9
    for k, tk in enumerate(t):
        val = eta(tk - last) + sum(1.1 * kap(tk - tj) for tj in tin if tj < tk)
        u[k] = val
        if val > th and tk - last > 2:
            spikes.append(tk); last = tk
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 3.9), gridspec_kw={"width_ratios": [1, 1, 2.2]})
    s = np.linspace(-2, 20, 400)
    axs[0].plot(s, eta(s), color=K.BLUE, lw=2.2); axs[0].axhline(0, color=K.GREY, lw=0.8)
    axs[0].set_title("refractory kernel $\\eta(s)$"); axs[0].set_xlabel("time since own spike $s$")
    axs[1].plot(s, kap(s), color=K.ACC2, lw=2.2); axs[1].axhline(0, color=K.GREY, lw=0.8)
    axs[1].set_title("response kernel $\\kappa(s)$"); axs[1].set_xlabel("time since input spike $s$")
    ax = axs[2]
    ax.plot(t, u, color=K.INK, lw=1.4, label="$u(t) = \\eta(t - \\hat t) + \\sum_j w\\,\\kappa(t - t_j)$")
    ax.axhline(th, color=K.ORANGE, ls="--", lw=1.2, label="threshold")
    for tj in tin:
        ax.plot([tj, tj], [-7.6, -7.0], color=K.ACC2, lw=1)
    for ts in spikes:
        ax.plot([ts, ts], [th, th + 2.5], color=K.INK, lw=1.6)
    ax.set_ylim(-8, 7); ax.set_xlabel("time"); ax.set_title("input spikes (bottom ticks) build $u$; crossing threshold fires and resets")
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    K.save(fig, "ch12_srm", wide=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["kernels", "transient"]
    for w in which:
        globals()[w]()
