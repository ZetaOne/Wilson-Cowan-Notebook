"""Chapter 5 figures: the E–I phase plane (Wilson & Cowan 1972, Figs. 4, 9, 10).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch05_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

EG = np.linspace(0.0005, 0.49, 1500)


def phase_plane(ax, pars, lim=(0, 0.5, 0, 0.5), trajs=(), stream=True, label=True):
    F, ke, ki = W.wc_rhs(pars)
    if stream:
        xs = np.linspace(lim[0], lim[1], 30); ys = np.linspace(lim[2], lim[3], 30)
        XX, YY = np.meshgrid(xs, ys)
        U, V = F(np.array([XX, YY]))
        ax.streamplot(xs, ys, U, V, color="#d5dade", density=1.1, linewidth=0.7, arrowsize=0.8)
    eg = EG[EG < ke]
    ie, ii = W.wc_nullclines(pars, eg)
    ax.plot(eg, ie, color=K.NULL_X, lw=2.2, label="$\\dot E = 0$" if label else None)
    ax.plot(eg, ii, color=K.NULL_Y, lw=2.2, label="$\\dot I = 0$" if label else None)
    m = W.load("wc", **pars)
    found = []
    # fixed points: intersections of the two nullclines, refined by XPP's Newton
    d = ie - ii
    e0 = m.equilibrium({"e": 0.0, "i": 0.0})              # the origin (S(0) = 0) is always a steady state
    found.append(((e0.x["E"], e0.x["I"]), e0.stable, e0.eigenvalues))
    for k in np.where(np.diff(np.sign(d)) != 0)[0]:
        e = m.equilibrium({"e": float(eg[k]), "i": float(ii[k])})
        p = (e.x["E"], e.x["I"])
        if not any(abs(p[0] - q[0]) < 1e-4 for q, _, _ in found):
            found.append((p, e.stable, e.eigenvalues))
    for (pe, pi), st, ev in found:
        ax.plot(pe, pi, "o", ms=10, mfc=K.ACC if st else "white", mec=K.INK, mew=1.6, zorder=6)
    for x0, col in trajs:
        t, X = W.traj(m, x0, 60, dt=0.02)
        ax.plot(X[:, 0], X[:, 1], color=col, lw=1.4)
        ax.plot(*x0, "o", ms=4, color=col)
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_xlabel("$E$"); ax.set_ylabel("$I$")
    m.close()
    return found


def fig4():
    fig, ax = plt.subplots(figsize=(6.8, 5.6))
    fp = phase_plane(ax, W.WC_HYST, lim=(0, 0.5, 0, 0.5),
                     trajs=[((0.08, 0.02), K.ACC2), ((0.12, 0.02), K.BLUE), ((0.45, 0.05), K.ORANGE), ((0.05, 0.4), K.GREY)])
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("Wilson & Cowan's Figure 4: three steady states")
    K.save(fig, "ch05_fig4")
    for (pe, pi), st, ev in fp:
        print(f"fixed point E={pe:.4f} I={pi:.4f} stable={st} eig={np.round(ev, 3)}")
    K.savedata("ch05_fig4", fp=np.array([[p[0][0], p[0][1], p[1]] for p in fp]))


def nullcline_geometry():
    """Where the E-nullcline's N shape comes from: for fixed I, dE/dt as a function of E is the
    one-population picture of chapter 2 (self-excitation c1)."""
    pars = W.WC_HYST
    F, ke, ki = W.wc_rhs(pars)
    fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.4))
    ax = axs[0]
    e = np.linspace(0, 0.48, 400)
    for Ifix, col in [(0.05, K.ACC), (0.15, K.BLUE), (0.3, K.ACC2)]:
        de = F(np.array([e, np.full_like(e, Ifix)]))[0]
        ax.plot(e, de, color=col, lw=2, label=f"$I = {Ifix}$")
    ax.axhline(0, color=K.GREY, lw=0.8)
    ax.set_xlabel("$E$"); ax.set_ylabel("$\\dot E$ (with $I$ frozen)"); ax.legend(fontsize=9)
    ax.set_title("$E$ alone at fixed $I$: one or three zeros")
    ax = axs[1]
    eg = EG[EG < ke]
    ie, ii = W.wc_nullclines(pars, eg)
    ax.plot(eg, ie, color=K.NULL_X, lw=2.4, label="$\\dot E = 0$")
    for Ifix, col in [(0.05, K.ACC), (0.15, K.BLUE), (0.3, K.ACC2)]:
        ax.axhline(Ifix, color=col, lw=1.2, ls="--")
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.5); ax.set_xlabel("$E$"); ax.set_ylabel("$I$"); ax.legend(fontsize=9, loc="upper left")
    ax.set_title("stack the zeros for every $I$: the $E$-nullcline")
    fig.tight_layout()
    K.save(fig, "ch05_nullgeom", wide=True)


def strength_duration():
    """Wilson & Cowan Fig. 9: the smallest pulse intensity P that switches the network from the lower to the
    upper steady state, as a function of the pulse duration."""
    pars = dict(W.WC_HYST)
    m = W.load_text(W.LOGISTIC + """ke=1-1/(1+exp(ae*the))
ki=1-1/(1+exp(ai*thi))
pp(t)=amp*heav(t)*heav(dur-t)
e'=(-e+(ke-re*e)*S(c1*e-c2*i+p+pp(t),ae,the))/taue
i'=(-i+(ki-ri*i)*S(c3*e-c4*i+q,ai,thi))/taui
par c1=12,c2=4,c3=13,c4=11,ae=1.2,the=2.8,ai=1,thi=4,re=1,ri=1,p=0,q=0,taue=1,taui=1,amp=1,dur=1
init e=0,i=0
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.05,total=80,maxstor=100000
done""")
    durs = np.r_[np.linspace(0.3, 2, 9), np.linspace(2.5, 12, 12)]
    thr = []
    for dur in durs:
        lo, hi = 0.0, 20.0
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            m.set(amp=mid, dur=float(dur), e=0.0, i=0.0)
            tr = m.run(total=80, dt=0.05)
            if tr["e"][-1] > 0.2:
                hi = mid
            else:
                lo = mid
        thr.append(hi)
    thr = np.array(thr)
    K.savedata("ch05_sd", durs=durs, thr=thr)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(durs, thr, "o-", color=K.ACC2, lw=2, ms=5)
    ax.axhline(thr[-1], color=K.GREY, ls="--", lw=1.2)
    ax.text(durs[-1], thr[-1] + 0.12, "minimum intensity for long pulses", ha="right", fontsize=10, color=K.GREY)
    ax.set_xlabel("pulse duration (units of $\\tau$)"); ax.set_ylabel("threshold intensity $P$")
    ax.set_title("Wilson & Cowan's Figure 9: strength–duration curve"); ax.set_ylim(0, None)
    K.save(fig, "ch05_strength")
    print("strength-duration: shortest", durs[0], thr[0], " longest", durs[-1], thr[-1])


def evoked():
    """Wilson & Cowan Fig. 10: damped oscillation of E - I after a brief impulse (an 'evoked potential')."""
    pars = dict(W.WC_FIG10)
    m = W.load_text(W.LOGISTIC + """ke=1-1/(1+exp(ae*the))
ki=1-1/(1+exp(ai*thi))
pp(t)=amp*heav(t-5)*heav(5+dur-t)
e'=(-e+(ke-re*e)*S(c1*e-c2*i+p+pp(t),ae,the))/taue
i'=(-i+(ki-ri*i)*S(c3*e-c4*i+q,ai,thi))/taui
par c1=15,c2=15,c3=15,c4=3,ae=1,the=2,ai=2,thi=2.5,re=1,ri=1,p=0,q=0,taue=1,taui=1,amp=0.5,dur=0.5
init e=0.05,i=0.02
@ meth=rk4,dt=0.005,total=40,maxstor=100000
done""")
    m.set(amp=0.0); m.run(total=80); m.run_last(total=5); m.set(amp=0.5)   # settle to the resting state first
    rest = m.last_point()
    m.set(e=rest["E"], i=rest["I"])
    tr = m.run(total=40, dt=0.005)
    t, e, i = np.asarray(tr.t), np.asarray(tr["e"]), np.asarray(tr["i"])
    K.savedata("ch05_evoked", t=t, e=e, i=i)
    eq = m.equilibrium({"e": rest["E"], "i": rest["I"]})
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.4, 1]})
    axs[0].plot(t, e - i, color=K.ACC2, lw=2, label="$E(t) - I(t)$")
    axs[0].axvspan(5, 5.5, color=K.ORANGE, alpha=0.25, label="brief impulse")
    axs[0].set_xlabel("time (units of $\\tau$)"); axs[0].legend(fontsize=9); axs[0].set_title("Wilson & Cowan's Figure 10: a damped response")
    axs[1].plot(e, i, color=K.ACC2, lw=1.6); axs[1].plot(rest["E"], rest["I"], "o", color=K.ACC, ms=8)
    axs[1].set_xlabel("$E$"); axs[1].set_ylabel("$I$"); axs[1].set_title("the same in the phase plane: a spiral back to rest")
    fig.tight_layout()
    K.save(fig, "ch05_evoked", wide=True)
    print("rest", rest, "eigenvalues", eq.eigenvalues)


def kicks_gif():
    """Kicks of increasing size from the lower steady state of Fig. 4: small ones decay, large ones switch on."""
    pars = W.WC_HYST
    m = W.load("wc", **pars)
    kicks = np.linspace(0.02, 0.2, 10)
    paths = []
    for kk in kicks:
        t, X = W.traj(m, (kk, 0.0), 40, dt=0.05)
        paths.append(X)
    paths = np.array(paths)
    K.savedata("ch05_kicks", kicks=kicks, paths=paths)
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    phase_plane(ax, pars, lim=(0, 0.5, 0, 0.5), stream=True)
    lines = [ax.plot([], [], lw=1.6, color=plt.cm.viridis(j / len(kicks)))[0] for j in range(len(kicks))]
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("kicks of growing size in $E$: decay, or switch on")
    n = paths.shape[1]

    def upd(f):
        k = int(f / 60 * (n - 1)) + 1
        for j, ln in enumerate(lines):
            ln.set_data(paths[j, :k, 0], paths[j, :k, 1])
    K.save_gif(fig, upd, 61, "ch05_kicks", fps=15)


if __name__ == "__main__":
    fig4()
    nullcline_geometry()
    strength_duration()
    evoked()
    kicks_gif()
