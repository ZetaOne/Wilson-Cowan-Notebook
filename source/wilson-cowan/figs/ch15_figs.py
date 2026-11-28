"""Chapter 15 figures: Laplace's method / semiclassical (loop) expansion, tree vs loop diagrams, and the 1/N
correction to the mean: generalized activity equations (mean + covariance) for the stochastic population of Ch. 14.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch15_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import wc_lib as W
import figkit as K
from ch14_figs import Fmf, Gd, roots, gillespie

P15 = dict(w=4.0, I=0.0, b=2.0, th=1.0)       # steady state a* = 0.456, well inside (0, 1)


def S(x, g=1.0):
    return x ** 2 / 2 + g * x ** 4 / 4 - 0.6 * x ** 3 / 3


def laplace():
    xs = np.linspace(-2.5, 2.5, 800)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2))
    ax = axs[0]
    for eps, col in [(1.0, K.ORANGE), (0.3, K.BLUE), (0.08, K.ACC2)]:
        y = np.exp(-S(xs) / eps)
        Z = quad(lambda x: np.exp(-S(x) / eps), -np.inf, np.inf)[0]
        ax.plot(xs, y / Z, color=col, lw=2.2, label=f"$\\epsilon = {eps}$")
        ax.plot(xs, np.exp(-xs ** 2 / (2 * eps)) / np.sqrt(2 * np.pi * eps), color=col, lw=1, ls="--")
    ax.set_xlabel("$x$"); ax.set_ylabel("$e^{-S(x)/\\epsilon}$ (normalised)"); ax.legend(fontsize=9)
    ax.set_title("small $\\epsilon$: sharply peaked, nearly Gaussian (dashed)")
    ax = axs[1]
    eps = np.logspace(-2.3, 0, 25)
    mean = []
    for e in eps:
        Z = quad(lambda x: np.exp(-S(x) / e), -12, 12, points=[0], limit=200)[0]
        M = quad(lambda x: x * np.exp(-S(x) / e), -12, 12, points=[0], limit=200)[0]
        mean.append(M / Z)
    mean = np.array(mean)
    ax.loglog(eps, np.abs(mean), "o", color=K.ACC2, ms=6, mec="k", label="exact $|\\langle x\\rangle|$")
    ax.loglog(eps, 0.6 * eps, color=K.INK, lw=1.6, label="one-loop: $0.6\\,\\epsilon$")
    ax.set_xlabel("$\\epsilon$"); ax.set_ylabel("shift of the mean from the minimum")
    ax.set_title("mean field ($\\langle x\\rangle = 0$) is the $\\epsilon \\to 0$ limit"); ax.legend(fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch15_laplace", wide=True)


def diagrams():
    fig, axs = plt.subplots(1, 3, figsize=(12.4, 3.6))
    def prop(ax, p, q, **kw):
        ax.annotate("", q, p, arrowprops=dict(arrowstyle="-|>", lw=2, color=kw.get("color", K.INK), shrinkA=0, shrinkB=0))
    def vert(ax, p):
        ax.plot(*p, "o", ms=11, color=K.ACC2, zorder=5)
    ax = axs[0]
    prop(ax, (0, 0), (2, 0)); ax.text(1, 0.25, "$\\Delta(t, t')$", ha="center", fontsize=13)
    ax.set_title("propagator: response to a kick\n(a Green's function)")
    ax = axs[1]
    vert(ax, (1.2, 0)); prop(ax, (0, 0.8), (1.2, 0)); prop(ax, (0, -0.8), (1.2, 0)); prop(ax, (1.2, 0), (2.4, 0))
    vert(ax, (0, 0.8)); vert(ax, (0, -0.8))
    ax.set_title("tree diagram: mean field\n(no closed loops)")
    ax = axs[2]
    prop(ax, (0, 0), (0.9, 0)); vert(ax, (0.9, 0))
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(1.5 + 0.6 * np.cos(th), 0.6 * np.sin(th), color=K.BLUE, lw=2)
    ax.annotate("", (1.5, 0.6), (1.45, 0.6), arrowprops=dict(arrowstyle="-|>", color=K.BLUE, lw=2))
    vert(ax, (2.1, 0)); prop(ax, (2.1, 0), (3.0, 0))
    ax.text(1.5, -0.95, "a closed loop: fluctuations\nfeed back on the mean ($\\propto 1/N$)", ha="center", fontsize=10, color=K.BLUE)
    ax.set_title("one-loop diagram: first correction")
    for ax in axs:
        ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.4, 3.2); ax.set_ylim(-1.5, 1.4)
    fig.tight_layout()
    K.save(fig, "ch15_diagrams", wide=True)


def second_order_text(p, N):
    """Mean + variance (generalized activity) equations for the two-state population."""
    return f"""f(x)=1/(1+exp(-b*(x-th)))
fp(x)=b*f(x)*(1-f(x))
fpp(x)=b*b*f(x)*(1-f(x))*(1-2*f(x))
drift(a)=-a+(1-a)*f(w*a+i0)
d1(a)=-1-f(w*a+i0)+(1-a)*w*fp(w*a+i0)
d2(a)=-2*w*fp(w*a+i0)+(1-a)*w*w*fpp(w*a+i0)
gg(a)=a+(1-a)*f(w*a+i0)
a'=drift(a)+0.5*d2(a)*c
c'=2*d1(a)*c+gg(a)/nn
m'=drift(m)
par w={p['w']},i0={p['I']},b={p['b']},th={p['th']},nn={N}
init a=0,c=0,m=0
@ meth=cvode,tol=1e-10,atol=1e-10,dt=0.02,total=12
done
"""


def one_loop():
    p = P15
    ast = roots(p)[-1]; h = 1e-5
    F1 = (Fmf(ast + h, p) - Fmf(ast - h, p)) / (2 * h)
    F2 = (Fmf(ast + h, p) - 2 * Fmf(ast, p) + Fmf(ast - h, p)) / h ** 2
    NV = Gd(ast, p) / (2 * abs(F1))
    shiftN = F2 * NV / (2 * abs(F1))                         # N * (<a> - a*)
    # transient: ensemble of exact simulations from a = 0, N = 10
    N = 10
    m = W.load_text(second_order_text(p, N))
    tr = m.run(total=12, dt=0.02)
    reps = 3000
    tt = None; acc = None
    for rep in range(reps):
        t, a = gillespie(N, p, 12, 0.0, seed=rep, dt_out=0.05)
        acc = a if acc is None else acc + a; tt = t
    ens = acc / reps
    # steady-state shift vs N
    Ns = [10, 20, 40, 80]
    shifts, errs = [], []
    for NN in Ns:
        vals = []
        for rep in range(8):
            t, a = gillespie(NN, p, 2000, ast, seed=50000 + 100 * NN + rep, dt_out=0.5)
            vals.append(a[t > 20].mean())
        shifts.append(NN * (np.mean(vals) - ast)); errs.append(NN * np.std(vals) / np.sqrt(len(vals)))
    K.savedata("ch15_oneloop", t=tt, ens=ens, ta=np.asarray(tr.t), a2=np.asarray(tr["a"]), mf=np.asarray(tr["m"]),
               Ns=np.array(Ns), shifts=np.array(shifts), errs=np.array(errs), shiftN=shiftN, ast=ast)
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.3))
    ax = axs[0]
    ax.plot(tt, ens, color=K.ACC2, lw=2.6, alpha=0.7, label=f"average of {reps} exact runs ($N = {N}$)")
    ax.plot(tr.t, tr["m"], color=K.BLUE, lw=1.8, ls="--", label="mean field (Wilson–Cowan)")
    ax.plot(tr.t, tr["a"], color=K.INK, lw=1.6, label="mean + covariance (one loop)")
    ax.set_xlabel("time"); ax.set_ylabel("mean fraction active"); ax.legend(fontsize=9, loc="lower right")
    ax.set_title("switching on: the correction from fluctuations")
    ax.set_ylim(0, None)
    ax = axs[1]
    ax.errorbar(Ns, shifts, yerr=errs, fmt="o", color=K.ACC2, ms=8, mec="k", capsize=3, label="Gillespie: $N(\\langle a\\rangle - a^*)$")
    ax.axhline(shiftN, color=K.INK, lw=1.8, label="one-loop prediction $F''\\,\\sigma^2 N/2|F'|$")
    ax.axhline(0, color=K.GREY, lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xlabel("population size $N$"); ax.set_ylabel("$N \\times$ (shift of the mean)")
    ax.set_title("the mean is shifted by $\\propto 1/N$"); ax.legend(fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch15_oneloop", wide=True)
    print("a*", ast, "F'", F1, "F''", F2, "pred N*shift", shiftN, "measured", shifts, errs)


def exact_shift(p, N):
    """Exact stationary mean of the birth-death chain (detailed balance), returned as N (<a> - a*)."""
    from ch14_figs import f
    ast = roots(p)[-1]
    n = np.arange(N + 1)
    up = (N - n) * f(p["w"] * n / N + p["I"], p); dn = n.astype(float)
    logp = np.zeros(N + 1)
    for k in range(N):
        logp[k + 1] = logp[k] + np.log(up[k]) - np.log(dn[k + 1])
    P = np.exp(logp - logp.max()); P /= P.sum()
    return N * ((P * n / N).sum() - ast)


def oneloop_plot():
    d = K.loaddata("ch15_oneloop")
    p = P15
    NN = np.unique(np.logspace(np.log10(5), np.log10(5000), 40).astype(int))
    ex = np.array([exact_shift(p, int(N)) for N in NN])
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.3))
    ax = axs[0]
    ax.plot(d["t"], d["ens"], color=K.ACC2, lw=2.6, alpha=0.7, label=f"average of 3000 exact runs ($N = {int(d.get('Ntr', 10))}$)")
    ax.plot(d["ta"], d["mf"], color=K.BLUE, lw=1.8, ls="--", label="mean field (Wilson–Cowan)")
    ax.plot(d["ta"], d["a2"], color=K.INK, lw=1.6, label="mean + covariance (one loop)")
    ax.set_xlabel("time"); ax.set_ylabel("mean fraction active"); ax.legend(fontsize=9, loc="lower right")
    ax.set_title("switching on: the correction from fluctuations"); ax.set_ylim(0, None)
    ax = axs[1]
    ax.plot(NN, ex, color=K.BLUE, lw=2, label="exact (stationary distribution)")
    ax.errorbar(d["Ns"], d["shifts"], yerr=d["errs"], fmt="o", color=K.ACC2, ms=8, mec="k", capsize=3, label="Gillespie simulations")
    ax.axhline(float(d["shiftN"]), color=K.INK, lw=1.8, ls="--", label="one-loop prediction (large $N$)")
    ax.set_xscale("log"); ax.set_xlabel("population size $N$"); ax.set_ylabel("$N \\times$ (shift of the mean)")
    ax.set_title("the mean is shifted by $\\propto 1/N$"); ax.legend(fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch15_oneloop", wide=True)
    print("exact N*shift at N=5000:", ex[-1], "pred", float(d["shiftN"]))


def transient(N=40, reps=3000):
    """Ensemble mean of exact runs switching on from a = 0, against mean field and the one-loop equations."""
    p = P15
    m = W.load_text(second_order_text(p, N))
    tr = m.run(total=12, dt=0.02)
    acc = None
    for rep in range(reps):
        t, a = gillespie(N, p, 12, 0.0, seed=7 * rep + 1, dt_out=0.05)
        acc = a if acc is None else acc + a
    d = K.loaddata("ch15_oneloop")
    d.update(t=t, ens=acc / reps, ta=np.asarray(tr.t), a2=np.asarray(tr["a"]), mf=np.asarray(tr["m"]), Ntr=N)
    K.savedata("ch15_oneloop", **d)
    print("N", N, "ensemble end", acc[-20:].mean() / reps, "one-loop end", float(tr["a"][-1]), "mf", float(tr["m"][-1]))


if __name__ == "__main__":
    which = sys.argv[1:] or ["laplace", "diagrams", "one_loop", "transient", "oneloop_plot"]
    for w in which:
        globals()[w]()


