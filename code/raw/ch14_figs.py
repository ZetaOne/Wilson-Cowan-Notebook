"""Chapter 14 figures: fluctuations and finite size in a stochastic population (Buice-Cowan style two-state
neurons).  Each of N neurons is active or quiescent: active -> quiescent at rate 1, quiescent -> active at rate
f(w a + I) with a the fraction active.  Mean field: a' = -a + (1 - a) f(w a + I), a Wilson-Cowan equation.
Exact simulations: Gillespie (numpy).  Diffusion (Langevin) approximation: XPPAUT with a Wiener process.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch14_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

MONO = dict(w=4.0, I=0.0, b=2.0, th=1.5)
BI = dict(w=14.0, I=0.0, b=1.0, th=4.0)


def f(x, p):
    return 1 / (1 + np.exp(-p["b"] * (x - p["th"])))


def Fmf(a, p):
    return -a + (1 - a) * f(p["w"] * a + p["I"], p)


def Gd(a, p):
    return a + (1 - a) * f(p["w"] * a + p["I"], p)


def roots(p):
    a = np.linspace(0, 1, 200001); F = Fmf(a, p)
    return a[np.where(np.diff(np.sign(F)) != 0)[0]]


def gillespie(N, p, T, a0, seed=0, dt_out=0.1):
    rng = np.random.default_rng(seed)
    n = int(round(a0 * N)); t = 0.0
    tout = np.arange(0, T, dt_out); out = np.empty_like(tout); k = 0
    while k < len(tout):
        up = (N - n) * f(p["w"] * n / N + p["I"], p); dn = float(n)
        tot = up + dn
        tau = rng.exponential(1 / tot)
        while k < len(tout) and tout[k] < t + tau:
            out[k] = n / N; k += 1
        t += tau
        n += 1 if rng.random() * tot < up else -1
    return tout, out


def langevin_text(p, N):
    return f"""# diffusion approximation of the two-state population (linear noise / Langevin)
f(x)=1/(1+exp(-b*(x-th)))
wiener xi
a'=-a+(1-a)*f(w*a+i0)+sqrt(max(a+(1-a)*f(w*a+i0),0)/nn)*xi
par w={p['w']},i0={p['I']},b={p['b']},th={p['th']},nn={N}
init a=0.03
@ meth=euler,dt=0.005,total=400,maxstor=200000,bound=100
done
"""


def finite_size():
    p = MONO
    ast = roots(p)[0]
    h = 1e-6
    Fp = (Fmf(ast + h, p) - Fmf(ast - h, p)) / (2 * h)
    var_lna = Gd(ast, p) / (2 * abs(Fp))                     # N * Var(a)
    Ns = [25, 50, 100, 200, 400, 800]
    vars_ = []; traces = {}
    for N in Ns:
        t, a = gillespie(N, p, 400, ast, seed=N)
        vars_.append(a[t > 20].var())
        if N in (25, 200, 800):
            traces[N] = (t, a)
    vars_ = np.array(vars_)
    K.savedata("ch14_finite", Ns=np.array(Ns), var=vars_, var_lna=var_lna, ast=ast)
    fig, axs = plt.subplots(1, 3, figsize=(13.0, 4.1), gridspec_kw={"width_ratios": [1.5, 1, 1]})
    ax = axs[0]
    for N, col in zip((25, 200, 800), (K.ORANGE, K.BLUE, K.ACC2)):
        t, a = traces[N]
        ax.plot(t, a, color=col, lw=0.9, label=f"$N = {N}$")
    ax.axhline(ast, color=K.INK, lw=1.8, ls="--", label="mean field $a^*$")
    ax.set_xlim(0, 100); ax.set_xlabel("time"); ax.set_ylabel("fraction active $a$"); ax.legend(fontsize=8.5, ncol=2)
    ax.set_title("finite populations fluctuate around mean field")
    ax = axs[1]
    t, a = traces[200]
    x = np.linspace(ast - 0.15, ast + 0.15, 300)
    s2 = var_lna / 200
    ax.hist(a[t > 20], bins=np.arange(0, 1, 1 / 200) - 0.5 / 200, density=True, color=K.BLUE, alpha=0.45, label="Gillespie, $N = 200$")
    ax.plot(x, np.exp(-(x - ast) ** 2 / (2 * s2)) / np.sqrt(2 * np.pi * s2), color=K.INK, lw=2, label="linear noise (Gaussian)")
    ax.set_xlim(ast - 0.15, ast + 0.15); ax.set_xlabel("$a$"); ax.legend(fontsize=8.5); ax.set_title("distribution at $N = 200$")
    ax = axs[2]
    ax.loglog(Ns, vars_, "o", color=K.ACC2, ms=8, mec="k", label="Gillespie")
    nn = np.array([20, 1000])
    ax.loglog(nn, var_lna / nn, color=K.INK, lw=1.8, label="LNA: $G(a^*)/(2|F'(a^*)|\\,N)$")
    ax.set_xlabel("population size $N$"); ax.set_ylabel("variance of $a$"); ax.legend(fontsize=8.5); ax.set_title("variance $\\propto 1/N$")
    fig.tight_layout()
    K.save(fig, "ch14_finite", wide=True)
    print("a*", ast, "N*var LNA", var_lna, "measured N*var", vars_ * np.array(Ns))


def switching():
    p = BI
    r = roots(p)
    a = np.linspace(1e-4, 0.6, 6000)
    Phi = -2 * np.cumsum(Fmf(a, p) / Gd(a, p)) * (a[1] - a[0])
    Phi -= Phi.min()
    # XPP Langevin traces
    trs = {}
    for N in (40, 80):
        m = W.load_text(langevin_text(p, N))
        m.set(a=float(r[0]))
        tr = m.run(total=400, dt=0.005)
        trs[N] = (np.asarray(tr.t)[::20], np.asarray(tr["a"])[::20])
    # mean switching time low -> high from Gillespie (exact)
    Ns = [20, 30, 40, 50, 60]
    mts = []
    thr = r[1]
    for N in Ns:
        times = []
        for rep in range(16):
            t, x = gillespie(N, p, 8000, r[0], seed=1000 * N + rep, dt_out=0.2)
            k = np.argmax(x > r[2] - 0.05)
            if x[k] > r[2] - 0.05:
                times.append(t[k])
        mts.append(np.mean(times) if times else np.nan)
        print("N", N, "switch times", len(times), np.mean(times) if times else None)
    mts = np.array(mts)
    dPhi = Phi[np.argmin(abs(a - r[1]))] - Phi[np.argmin(abs(a - r[0]))]
    K.savedata("ch14_switch", a=a, Phi=Phi, roots=r, Ns=np.array(Ns), mts=mts, dPhi=dPhi,
               t40=trs[40][0], a40=trs[40][1], t80=trs[80][0], a80=trs[80][1])
    fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.1), gridspec_kw={"width_ratios": [1, 1.5, 1]})
    ax = axs[0]
    ax.plot(a, Phi, color=K.INK, lw=2.2)
    for x0, st in zip(r, [True, False, True]):
        ax.plot(x0, Phi[np.argmin(abs(a - x0))], "o", ms=9, mfc=K.ACC if st else "white", mec=K.INK, zorder=5)
    ax.set_xlabel("fraction active $a$"); ax.set_ylabel("quasi-potential $\\Phi(a)$")
    ax.set_title("$p(a) \\propto e^{-N\\Phi(a)}$: two wells")
    ax = axs[1]
    for N, col in [(40, K.ORANGE), (80, K.ACC2)]:
        ax.plot(*trs[N], color=col, lw=0.8, label=f"$N = {N}$")
    for x0 in (r[0], r[2]):
        ax.axhline(x0, color=K.INK, lw=1, ls="--")
    ax.set_xlabel("time"); ax.set_ylabel("$a$"); ax.legend(fontsize=9, loc="center right")
    ax.set_title("noise-driven switching (XPPAUT, Langevin)")
    ax = axs[2]
    ax.semilogy(Ns, mts, "o", color=K.ACC2, ms=8, mec="k", label="Gillespie")
    ok = np.isfinite(mts)
    c = np.polyfit(np.array(Ns)[ok], np.log(mts[ok]), 1)
    nn = np.linspace(15, 65, 50)
    ax.semilogy(nn, np.exp(np.polyval(c, nn)), color=K.INK, lw=1.4, label=f"slope {c[0]:.3f} (barrier $\\Delta\\Phi = {dPhi:.3f}$)")
    ax.set_xlabel("population size $N$"); ax.set_ylabel("mean time to switch on"); ax.legend(fontsize=8.5)
    ax.set_title("switching time grows like $e^{N\\Delta\\Phi}$")
    fig.tight_layout()
    K.save(fig, "ch14_switch", wide=True)
    print("roots", r, "barrier", dPhi, "fit slope", c[0])


if __name__ == "__main__":
    which = sys.argv[1:] or ["finite_size", "switching"]
    for w in which:
        globals()[w]()
