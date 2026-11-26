"""Chapter 6 figures: oscillations of the Wilson–Cowan pair (their Fig. 11), Hopf bifurcations with AUTO,
frequency against input, isochrons and the phase response curve.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch06_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K
import iso_lib as IL

EG = np.linspace(0.0005, 0.49, 1500)


def nullclines(ax, pars):
    F, ke, ki = W.wc_rhs(pars)
    eg = EG[EG < ke]
    ie, ii = W.wc_nullclines(pars, eg)
    ax.plot(eg, ie, color=K.NULL_X, lw=2, label="$\\dot E = 0$")
    ax.plot(eg, ii, color=K.NULL_Y, lw=2, label="$\\dot I = 0$")


def fig11():
    pars = dict(W.WC_OSC)
    m = W.load("wc", **pars)
    t, X, T = W.periodic_orbit(m, (0.1, 0.05), settle=200, dt=0.005)
    fps = W.wc_fixed_points(pars)
    print("period", T, "fixed points", fps)
    eE, eI = fps[-1][0], fps[-1][1]
    tr, Y = W.traj(m, (0.02, 0.02), 40, dt=0.02)
    K.savedata("ch06_cycle", t=t, X=X, T=T, eq=np.array([eE, eI]), Y=Y)
    F, ke, ki = W.wc_rhs(pars)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.5), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]
    xs = np.linspace(0, 0.5, 30); ys = np.linspace(0, 0.5, 30)
    XX, YY = np.meshgrid(xs, ys); U, V = F(np.array([XX, YY]))
    ax.streamplot(xs, ys, U, V, color="#d5dade", density=1.0, linewidth=0.7, arrowsize=0.8)
    nullclines(ax, pars)
    ax.plot(Y[:, 0], Y[:, 1], color=K.BLUE, lw=1.1, label="trajectory from near the origin")
    ax.plot(X[:, 0], X[:, 1], color=K.ACC2, lw=2.6, label="limit cycle")
    for fE, fI, st, ev in fps:
        ax.plot(fE, fI, "o", mfc=K.ACC if st else "white", mec="k", ms=8, zorder=6)
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$"); ax.set_ylabel("$I$"); ax.legend(fontsize=8.5, loc="upper left")
    ax.set_title("Wilson & Cowan's Figure 11a ($P = 1.25$)")
    ax = axs[1]
    tt = np.r_[t, t + T, t + 2 * T, t + 3 * T]
    ax.plot(tt, np.tile(X[:, 0], 4), color=K.ACC2, lw=2, label="$E(t)$")
    ax.plot(tt, np.tile(X[:, 1], 4), color=K.BLUE, lw=2, label="$I(t)$")
    ax.set_xlabel("time (units of $\\tau$)"); ax.legend(fontsize=9); ax.set_title(f"Figure 11b: period $T = {T:.3f}\\,\\tau$")
    fig.tight_layout()
    K.save(fig, "ch06_fig11", wide=True)


def auto_P():
    """Bifurcation diagram in the input P.  Steady states: exact curve P(E) (wc_branch_in_P), stability from the
    Jacobian.  Cycles: AUTO from the upper Hopf point (AUTO stalls at the folds near P = 1, so the steady-state
    branch is started above them)."""
    pars = dict(W.WC_OSC)
    eg = np.linspace(0.0005, 0.42, 5000)
    P, Ib, tr, det = W.wc_branch_in_P(pars, eg)
    stab = (tr < 0) & (det > 0)
    folds = [(eg[j], P[j]) for j in np.where(np.diff(np.sign(np.diff(P))) != 0)[0]]
    hopf = [(eg[j], P[j]) for j in np.where((np.diff(np.sign(tr)) != 0) & (det[:-1] > 0))[0]]
    m = W.load("wc", **pars); m.set(p=3.0, e=0.3, i=0.2); m.run(total=200); m.run_last(total=20)
    eq = m.auto.run("p", start="steady", ds=-0.02, dsmax=0.05, parmin=1.15, parmax=4.0, nmax=300)
    hb = eq.special("HB")
    po = m.auto.run(grab=hb[0].label, choice="periodic", ntst=120, dsmax=0.02, nmax=1500, parmin=0.9, parmax=4.0)
    dpo = po.to_pandas("e")
    dpo = dpo[dpo.period < 1e3]
    Phom = float(dpo.par.min())
    print("folds", folds, "hopf", hopf, "homoclinic near P =", Phom)
    K.savedata("ch06_auto", E=eg, P=P, I=Ib, tr=tr, det=det, po=dpo[["par", "ymax", "ymin", "stable", "period"]].to_numpy(float),
               folds=np.array(folds), hopf=np.array(hopf), Phom=Phom)
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.5))
    ax = axs[0]
    ax.plot(np.where(stab, P, np.nan), eg, color=K.INK, lw=2.2, label="steady state, stable")
    ax.plot(np.where(~stab, P, np.nan), eg, "--", color=K.INK, lw=1.3, label="steady state, unstable")
    s = dpo[dpo.stable == True]
    ax.plot(s.par, s.ymax, color=K.ACC2, lw=2.4, label="limit cycle: max and min of $E$")
    ax.plot(s.par, s.ymin, color=K.ACC2, lw=2.4)
    for e, pp in hopf:
        if pp > 1.5:
            ax.plot(pp, e, "s", color=K.ORANGE, ms=8, zorder=6)
            ax.annotate("Hopf", (pp, e), (pp + 0.25, e - 0.06), fontsize=10, color=K.ORANGE, arrowprops=dict(arrowstyle="-", color=K.ORANGE))
    for e, pp in folds:
        ax.plot(pp, e, "D", color=K.BLUE, ms=6, zorder=6)
    ax.annotate("folds (saddle-node)", (folds[0][1], folds[0][0]), (1.35, 0.02), fontsize=10, color=K.BLUE,
                arrowprops=dict(arrowstyle="-", color=K.BLUE))
    ax.axvline(Phom, color=K.GREY, lw=0.8, ls=":")
    ax.text(Phom - 0.03, 0.41, "homoclinic", rotation=90, fontsize=9.5, color=K.GREY, ha="right", va="top")
    ax.set_xlabel("input to excitatory cells $P$"); ax.set_ylabel("$E$"); ax.legend(fontsize=8.5, loc="lower right")
    ax.set_title("where oscillations live: $%.2f < P < %.2f$" % (Phom, hopf[-1][1])); ax.set_xlim(0.5, 3.0); ax.set_ylim(0, 0.42)
    ax = axs[1]
    sf = s.sort_values("par")
    ax.plot(sf.par, 1 / sf.period, color=K.ACC2, lw=2.4)
    ax.set_xlabel("input $P$"); ax.set_ylabel("frequency $1/T$ (cycles per $\\tau$)")
    ax.set_title("frequency rises from zero as input grows"); ax.set_ylim(0, None)
    ax.axvline(Phom, color=K.GREY, lw=0.8, ls=":")
    fig.tight_layout()
    K.save(fig, "ch06_auto", wide=True)
    print("frequency range", (1 / sf.period).min(), (1 / sf.period).max())


def hopf_gif():
    pars = dict(W.WC_OSC)
    Ps = np.r_[np.linspace(2.6, 1.3, 45), np.full(8, 1.3)]
    m = W.load("wc", **pars)
    paths = []
    for P in Ps:
        m.set(p=float(P))
        t, X = W.traj(m, (0.33, 0.27), 60, dt=0.05)
        paths.append(X)
    K.savedata("ch06_hopfgif", Ps=Ps, paths=np.array(paths))
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ln, = ax.plot([], [], color=K.ACC2, lw=1.4)
    nl = []
    lab = ax.text(0.03, 0.96, "", transform=ax.transAxes, va="top", fontsize=12, bbox=K.BOX)
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$"); ax.set_ylabel("$I$")
    ax.set_title("lowering $P$ through the Hopf point ($P = 1.88$)")

    def upd(k):
        for l in nl:
            l.remove()
        nl.clear()
        q = dict(pars); q["p"] = float(Ps[k])
        F, ke, ki = W.wc_rhs(q)
        eg = EG[EG < ke]; ie, ii = W.wc_nullclines(q, eg)
        nl.append(ax.plot(eg, ie, color=K.NULL_X, lw=1.5)[0]); nl.append(ax.plot(eg, ii, color=K.NULL_Y, lw=1.5)[0])
        ln.set_data(paths[k][:, 0], paths[k][:, 1])
        lab.set_text(f"$P = {Ps[k]:.2f}$")
    K.save_gif(fig, upd, len(Ps), "ch06_hopf", fps=10)


def phase_and_prc(recompute=False):
    pars = dict(W.WC_OSC)
    if recompute:
        m = W.load("wc", **pars)
        t, X, T = W.periodic_orbit(m, (0.1, 0.05), settle=200, dt=0.002)
        kap, nu, adj = W.floquet(m)
        tz = np.asarray(adj.t, float) / T
        ZE = np.asarray(adj[adj.names[1]], float) / T
        ZI = np.asarray(adj[adj.names[2]], float) / T
        xs = np.linspace(0.0, 0.5, 161); ys = np.linspace(0.0, 0.5, 161)
        th, _ = IL.phase_map("wc", pars, X, T, xs, ys, tol=1e-6, maxper=200, procs=7)
        K.savedata("ch06_phase", xs=xs, ys=ys, th=th, X=X, T=T, tz=tz, ZE=ZE, ZI=ZI, kappa=kap if kap is not None else np.nan)
        print("Floquet exponent", kap, " multiplier", nu)
    d = K.loaddata("ch06_phase")
    xs, ys, th, X, T, tz, ZE, ZI = (d[k] for k in ["xs", "ys", "th", "X", "T", "tz", "ZE", "ZI"])
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.7))
    ax = axs[0]
    ax.pcolormesh(xs, ys, th, cmap=K.CYCLIC, shading="auto", alpha=0.55, rasterized=True)
    lev = np.arange(8) / 8
    curves = IL.isochron_curves(xs, ys, th, lev)
    for c, segs in curves.items():
        for sg in segs:
            ax.plot(sg[:, 0], sg[:, 1], color=K.PHASE_CMAP(c), lw=1.5)
    ax.plot(X[:, 0], X[:, 1], color="k", lw=2.4)
    n = len(X)
    for c in lev:
        j = int(c * n) % n
        ax.plot(X[j, 0], X[j, 1], "o", ms=7, mfc=K.PHASE_CMAP(c), mec="k", zorder=6)
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$"); ax.set_ylabel("$I$")
    ax.set_title("8 isochrons: they wind around the cycle")
    ax = axs[1]
    ax.plot(tz, ZE, color=K.ACC2, lw=2, label="kick to $E$")
    ax.plot(tz, ZI, color=K.BLUE, lw=2, label="kick to $I$")
    ax.axhline(0, color=K.GREY, lw=0.8)
    ax.set_xlabel("phase $\\vartheta$ (0 = start of the stored cycle)"); ax.set_ylabel("phase shift per unit kick")
    ax.legend(fontsize=9); ax.set_title("phase response curves (XPP adjoint)")
    fig.tight_layout()
    K.save(fig, "ch06_phase", wide=True)


if __name__ == "__main__":
    import sys as _s
    which = _s.argv[1:] or ["fig11", "auto_P", "hopf_gif", "phase_and_prc"]
    for w in which:
        globals()[w]()
    raise SystemExit
    fig11()
    auto_P()
    hopf_gif()
    phase_and_prc()
