"""Chapter 1 figures: why populations? A spiking network, its raster and its population rate.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch01_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

N = 200


def run_network(J=0.3, stim="0.4*heav(t-30)*heav(70-t)", total=100, dt=0.02, eta0=-0.2, delta=0.1):
    txt, etas = W.theta_network(N=N, J=J, tau=2.0, eta0=eta0, delta=delta, stim=stim)
    m = W.load_text(txt)
    tr = m.run(total=total, dt=dt)
    t = np.asarray(tr.t, float)
    th = np.column_stack([np.asarray(tr[f"th{k}"], float) for k in range(1, N + 1)])
    s = np.asarray(tr["s"], float)
    k = np.floor((th + np.pi) / (2 * np.pi))
    idx = np.argwhere(np.diff(k, axis=0) > 0)
    spikes = [(t[i + 1], j) for i, j in idx]
    return t, th, s, np.array(spikes), etas


def rate(spikes, t, width=1.0):
    edges = np.arange(t[0], t[-1] + width, width)
    h, _ = np.histogram(spikes[:, 0], edges)
    return 0.5 * (edges[1:] + edges[:-1]), h / (N * width)


def raster_figure():
    t, th, s, sp, etas = run_network()
    K.savedata("ch01_net", t=t, s=s, spikes=sp, etas=etas, th=th[:, :6])
    tc, r = rate(sp, t, width=1.0)
    tc2, r2 = rate(sp, t, width=0.25)
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, gridspec_kw={"height_ratios": [1, 2.2, 1.3]})
    ax = axs[0]
    for j, col in zip([40, 100, 160], [K.ACC, K.BLUE, K.ACC2]):
        ax.plot(t, 1 - np.cos(th[:, j]), color=col, lw=1, label=f"neuron {j + 1}")
    ax.set_ylabel("$1-\\cos\\theta$"); ax.set_title("three single neurons: each spike is a pulse")
    ax.legend(fontsize=8.5, loc="upper left", ncol=3)
    ax = axs[1]
    ax.plot(sp[:, 0], sp[:, 1] + 1, "|", ms=2.2, color=K.INK, mew=0.6)
    ax.axvspan(30, 70, color=K.ORANGE, alpha=0.08)
    ax.set_ylabel("neuron"); ax.set_ylim(0, N + 1); ax.set_title(f"raster of all {N} neurons (stimulus on between $t = 30$ and $70$)")
    ax = axs[2]
    ax.plot(tc2, r2, color=K.GREY, lw=0.8, label="bins of 0.25: noisy")
    ax.plot(tc, r, color=K.ACC2, lw=2, label="bins of 1: the population rate $a(t)$")
    ax.set_ylabel("spikes per neuron\nper unit time"); ax.set_xlabel("time $t$"); ax.legend(fontsize=9, loc="upper left")
    ax.set_title("coarse-graining: count spikes in the whole population over a short window")
    fig.tight_layout()
    K.save(fig, "ch01_raster", wide=True)
    print("spikes:", len(sp), " mean rate before/during stimulus:", r[(tc > 10) & (tc < 30)].mean(), r[(tc > 40) & (tc < 70)].mean())


def raster_gif():
    d = K.loaddata("ch01_net")
    t, sp = d["t"], d["spikes"]
    tc, r = rate(sp, t, width=1.0)
    fig, axs = plt.subplots(2, 1, figsize=(8.4, 5.2), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axs[0].set_xlim(0, 100); axs[0].set_ylim(0, N + 1); axs[0].set_ylabel("neuron")
    axs[1].set_ylim(0, max(r) * 1.15); axs[1].set_ylabel("rate $a(t)$"); axs[1].set_xlabel("time $t$")
    axs[0].set_title("from spikes to a population rate")
    pts, = axs[0].plot([], [], "|", ms=2.2, color=K.INK, mew=0.6)
    win = axs[0].axvspan(0, 1, color=K.ACC2, alpha=0.2)
    line, = axs[1].plot([], [], color=K.ACC2, lw=2)
    frames = 100

    def upd(f):
        tt = f + 1
        m = sp[:, 0] <= tt
        pts.set_data(sp[m, 0], sp[m, 1] + 1)
        win.set_x(tt - 1)
        k = tc <= tt
        line.set_data(tc[k], r[k])

    def still():
        pts.set_data(sp[:, 0], sp[:, 1] + 1); line.set_data(tc, r)
    K.save_gif(fig, upd, frames, "ch01_coarse", fps=12, still_draw=still)


def fi_curves():
    """f–I curve of one theta-neuron (rate = sqrt(I)/pi for I > 0, measured in XPP) and the average over a
    heterogeneous population, which is smooth: the first appearance of a sigmoid-like gain function."""
    Is = np.linspace(-0.6, 1.0, 33)
    one = []
    m = W.load_text("""th'=1-cos(th)+(1+cos(th))*i
par i=0.1
init th=0
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.01,total=200,maxstor=100000,bound=1e8
done""")
    for I in Is:
        m.set(i=float(I), th=0.0)
        tr = m.run(total=200, dt=0.02)
        th = np.asarray(tr["th"], float)
        n = np.floor((th[-1] + np.pi) / (2 * np.pi)) - np.floor((th[len(th) // 2] + np.pi) / (2 * np.pi))
        one.append(n / 100)
    one = np.array(one)
    rng = np.random.default_rng(3)
    thr = rng.normal(0.0, 0.25, 4000)                   # heterogeneous excitability: shift each neuron's threshold
    xx = np.linspace(-0.6, 1.0, 300)
    pop = np.array([np.mean(np.sqrt(np.clip(x - thr, 0, None)) / np.pi) for x in xx])
    K.savedata("ch01_fi", Is=Is, one=one, xx=xx, pop=pop)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(Is, one, "o", color=K.ACC, ms=5, label="one neuron, measured in XPP")
    ax.plot(xx, np.sqrt(np.clip(xx, 0, None)) / np.pi, color=K.ACC, lw=1.2, label="one neuron: $\\sqrt{I}/\\pi$")
    ax.plot(xx, pop, color=K.ACC2, lw=2.4, label="average over 4000 neurons with\nthresholds spread (s.d. 0.25)")
    ax.axvline(0, color=K.GREY, lw=0.8, ls=":")
    ax.set_xlabel("input $I$"); ax.set_ylabel("firing rate"); ax.legend(fontsize=9, loc="upper left")
    ax.set_title("a sharp single-neuron threshold, a smooth population gain")
    K.save(fig, "ch01_fi")


if __name__ == "__main__":
    raster_figure()
    raster_gif()
    fi_curves()
