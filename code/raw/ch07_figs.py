"""Chapter 7 figures: multistability and hysteresis (Wilson & Cowan 1972, Figs. 5-8) and two-parameter maps.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch07_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

EG = np.linspace(0.0005, 0.49, 1500)


def turning(P):
    """indices where the finite sequence P turns around (folds), ignoring NaNs"""
    dP = np.diff(P)
    sg = np.sign(dP)
    ok = np.isfinite(dP[:-1]) & np.isfinite(dP[1:])
    return np.where((sg[:-1] * sg[1:] < 0) & ok)[0] + 1


def crossings(x, mask):
    ok = np.isfinite(x[:-1]) & np.isfinite(x[1:])
    return np.where((np.sign(x[:-1]) * np.sign(x[1:]) < 0) & ok & mask[:-1])[0]


def branch(pars, emax=0.49, n=5000):
    eg = np.linspace(-0.02, min(emax, W.wc_emax(pars) - 1e-4), n)
    P, I, tr, det = W.wc_branch_in_P(pars, eg)
    stab = (tr < 0) & (det > 0)
    folds = [(eg[j], P[j]) for j in turning(P)]
    hopf = [(eg[j], P[j]) for j in crossings(tr, det > 0)]
    return eg, P, I, stab, folds, hopf


def plot_branch(ax, pars, xlim, title, emax=0.49):
    eg, P, I, stab, folds, hopf = branch(pars, emax)
    ax.plot(np.where(stab, P, np.nan), eg, color=K.INK, lw=2.4, label="stable")
    ax.plot(np.where(~stab, P, np.nan), eg, "--", color=K.INK, lw=1.3, label="unstable")
    for e, p in folds:
        ax.plot(p, e, "D", color=K.BLUE, ms=6, zorder=6)
    for e, p in hopf:
        ax.plot(p, e, "s", color=K.ORANGE, ms=7, zorder=6)
    ax.set_xlim(*xlim); ax.set_ylim(-0.02, emax); ax.set_xlabel("input $P$"); ax.set_ylabel("steady-state $E$")
    ax.set_title(title)
    return folds, hopf


def nullslide():
    """Raising P lifts the E-nullcline by P/c2: the number of crossings goes 1 -> 3 -> 1."""
    pars = dict(W.WC_HYST)
    Ps = [-0.6, 0.0, 0.6]
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.3), sharey=True)
    for ax, P in zip(axs, Ps):
        q = dict(pars); q["p"] = P
        F, ke, ki = W.wc_rhs(q)
        eg = EG[EG < ke]
        ie, ii = W.wc_nullclines(q, eg)
        q0 = dict(pars); ie0, _ = W.wc_nullclines(q0, eg)
        if P != 0:
            ax.plot(eg, ie0, color=K.NULL_X, lw=1.2, alpha=0.35, ls="--")
        ax.plot(eg, ie, color=K.NULL_X, lw=2.4, label="$\\dot E = 0$")
        ax.plot(eg, ii, color=K.NULL_Y, lw=2.4, label="$\\dot I = 0$")
        for e, i, tr, det, st in W.wc_steady_states_fast(q):
            ax.plot(e, i, "o", ms=10, mfc=K.ACC if st else "white", mec=K.INK, mew=1.6, zorder=6)
        ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$")
        n = len(W.wc_steady_states_fast(q))
        ax.set_title(f"$P = {P:+.1f}$: {n} steady state{'s' if n > 1 else ''}")
    axs[0].set_ylabel("$I$"); axs[0].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch07_nullslide", wide=True)


def nullslide_gif():
    pars = dict(W.WC_HYST)
    Ps = np.r_[np.linspace(-0.8, 0.8, 40), np.linspace(0.8, -0.8, 40)]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    F, ke, ki = W.wc_rhs(pars)
    eg = EG[EG < ke]
    _, ii = W.wc_nullclines(pars, eg)
    ax.plot(eg, ii, color=K.NULL_Y, lw=2.2)
    ln, = ax.plot([], [], color=K.NULL_X, lw=2.2)
    dots = []
    lab = ax.text(0.03, 0.96, "", transform=ax.transAxes, va="top", fontsize=12, bbox=K.BOX)
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$"); ax.set_ylabel("$I$")
    ax.set_title("input $P$ slides the $E$-nullcline up and down")

    def upd(k):
        for d in dots:
            d.remove()
        dots.clear()
        q = dict(pars); q["p"] = float(Ps[k])
        ie, _ = W.wc_nullclines(q, eg)
        ln.set_data(eg, ie)
        for e, i, tr, det, st in W.wc_steady_states_fast(q, n=1500):
            dots.append(ax.plot(e, i, "o", ms=10, mfc=K.ACC if st else "white", mec=K.INK, mew=1.6, zorder=6)[0])
        lab.set_text(f"$P = {Ps[k]:+.2f}$")
    K.save_gif(fig, upd, len(Ps), "ch07_slidegif", fps=10)


def ramp(pars, p0, p1, Tr=400.0):
    """Slow triangular ramp of P from p0 to p1 and back; returns t, P(t), E(t)."""
    q = dict(W.WC_OSC); q.update(pars)
    txt = W.LOGISTIC + f"""ke=1-1/(1+exp(ae*the))
ki=1-1/(1+exp(ai*thi))
pp(t)=p0+(p1-p0)*(1-abs(t/tr-1))
e'=-e+(ke-re*e)*S(c1*e-c2*i+pp(t),ae,the)
i'=-i+(ki-ri*i)*S(c3*e-c4*i+q,ai,thi)
aux pin=pp(t)
par c1={q['c1']},c2={q['c2']},c3={q['c3']},c4={q['c4']},ae={q['ae']},the={q['the']},ai={q['ai']},thi={q['thi']}
par re=1,ri=1,q={q['q']},p0={p0},p1={p1},tr={Tr}
init e=0,i=0
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.1,total={2 * Tr},maxstor=100000
done
"""
    m = W.load_text(txt)
    # start on the steady state at p0
    m.set(p1=p0); m.run(total=200); m.run_last(total=10); m.set(p1=p1)
    tr = m.run(total=2 * Tr, dt=0.1)
    return np.asarray(tr.t), np.asarray(tr["pin"]), np.asarray(tr["e"])


def fig5():
    """Wilson & Cowan Fig. 5: a hysteresis loop in E against P."""
    pars = dict(W.WC_HYST)
    t, P, E = ramp(pars, -0.8, 0.8)
    K.savedata("ch07_fig5", t=t, P=P, E=E)
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    folds, _ = plot_branch(ax, pars, (-0.8, 0.8), "Wilson & Cowan's Figure 5: a hysteresis loop", emax=0.47)
    up = slice(0, len(t) // 2); dn = slice(len(t) // 2, None)
    ax.plot(P[up], E[up], color=K.ACC2, lw=1.6, alpha=0.85, label="slow ramp up")
    ax.plot(P[dn], E[dn], color=K.BLUE, lw=1.6, alpha=0.85, label="slow ramp down")
    for e, p in folds:
        ax.annotate(f"fold $P={p:.2f}$", (p, e), (p + (0.08 if p > 0 else -0.05), e + (0.12 if p > 0 else -0.1)),
                    fontsize=9.5, color=K.BLUE, ha="left" if p > 0 else "right",
                    arrowprops=dict(arrowstyle="-", color=K.BLUE))
    ax.legend(fontsize=8.5, loc="lower right")
    ax = axs[1]
    ax.plot(t, E, color=K.ACC2, lw=2, label="$E(t)$")
    ax2 = ax.twinx()
    ax2.plot(t, P, color=K.ORANGE, lw=1.4, ls="--"); ax2.set_ylabel("input $P(t)$", color=K.ORANGE)
    ax2.spines["right"].set_visible(True)
    ax.set_xlabel("time (units of $\\tau$)"); ax.set_ylabel("$E$"); ax.set_title("the same ramp in time")
    fig.tight_layout()
    K.save(fig, "ch07_fig5", wide=True)
    print("fig5 folds", folds)


def fig67():
    """Wilson & Cowan Figs. 6-7: two hysteresis loops, and overlapping loops with three stable states."""
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.4))
    f6, h6 = plot_branch(axs[0], W.WC_FIG6, (-0.6, 1.6), "Figure 6: two separate loops", emax=0.49)
    f7, h7 = plot_branch(axs[1], W.WC_FIG7, (-0.7, 1.0), "Figure 7: three stable states at once", emax=0.49)
    axs[0].legend(fontsize=9, loc="lower right")
    eg, P, I, stab, _, _ = branch(W.WC_FIG7)
    grid = np.linspace(-0.7, 1.0, 341)
    counts = [sum(stab[j] for j in crossings(P - g, np.ones_like(P, bool))) for g in grid]
    good = grid[np.array(counts) == 3]
    print("P with three stable states:", good.min() if len(good) else None, good.max() if len(good) else None)
    P0 = float(good[len(good) // 2]) if len(good) else 0.0
    nst = 3 if len(good) else counts[len(grid) // 2]
    axs[1].axvspan(good.min(), good.max(), color=K.ACC, alpha=0.12) if len(good) else None
    axs[1].axvline(P0, color=K.GREY, lw=0.8, ls=":")
    axs[1].text(0.23, 0.36, f"{nst} stable states", fontsize=9.5, color=K.GREY, va="top")
    fig.tight_layout()
    K.save(fig, "ch07_fig67", wide=True)
    print("fig6 folds", f6, "hopf", h6); print("fig7 folds", f7, "hopf", h7, "stable at P=0", nst)
    K.savedata("ch07_fig67", f6=np.array(f6), f7=np.array(f7), h7=np.array(h7) if h7 else np.zeros((0, 2)))


def twopar():
    """Two-parameter map in (P, Q) for the oscillator parameters: fold curves (number of steady states changes)
    and the Hopf curve (a steady state changes stability with complex eigenvalues).  Computed exactly from the
    steady-state curve P(E) at each Q."""
    base = dict(W.WC_OSC)
    Qs = np.linspace(-3.0, 1.5, 181)
    eg = np.linspace(-0.02, min(0.48, W.wc_emax(base) - 1e-4), 3000)
    F1, H = [], []
    for Q in Qs:
        q = dict(base); q["q"] = float(Q)
        P, I, tr, det = W.wc_branch_in_P(q, eg)
        for j in turning(P):
            F1.append((P[j], Q, eg[j]))
        for j in crossings(tr, det > 0):
            H.append((P[j], Q, eg[j]))
    F1 = np.array(F1); H = np.array(H)
    K.savedata("ch07_twopar", folds=F1, hopf=H, Qs=Qs)
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.plot(F1[:, 0], F1[:, 1], ".", ms=2.5, color=K.BLUE, label="fold (saddle-node) curve")
    ax.plot(H[:, 0], H[:, 1], ".", ms=2.5, color=K.ORANGE, label="Hopf curve")
    ax.plot(1.25, 0, "*", ms=14, color=K.ACC2, mec="k", zorder=6, label="Figure 11 ($P = 1.25,\\ Q = 0$)")
    for (px, py, txt, col) in [(1.45, -0.35, "oscillations", K.ACC2), (-0.3, -1.6, "three\nsteady states", K.BLUE),
                               (2.8, -1.8, "one stable\nsteady state", K.INK), (-0.6, 0.6, "one stable\nsteady state (rest)", K.INK)]:
        ax.text(px, py, txt, fontsize=10.5, color=col, ha="center", va="center")
    ax.set_xlabel("input to excitatory cells $P$"); ax.set_ylabel("input to inhibitory cells $Q$")
    ax.set_title("a two-parameter map of the Wilson–Cowan oscillator")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_xlim(-1, 5); ax.set_ylim(Qs[0], Qs[-1])
    K.save(fig, "ch07_twopar")
    print("fold points", len(F1), "hopf points", len(H))
    print("hopf P range", H[:, 0].min() if len(H) else None, H[:, 0].max() if len(H) else None)
    print("fold Q range", F1[:, 1].min(), F1[:, 1].max())


if __name__ == "__main__":
    which = sys.argv[1:] or ["nullslide", "nullslide_gif", "fig5", "fig67", "twopar"]
    for w in which:
        globals()[w]()
