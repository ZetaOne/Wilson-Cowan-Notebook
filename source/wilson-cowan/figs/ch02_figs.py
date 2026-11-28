"""Chapter 2 figures: one recurrent population, tau a' = -a + f(w a + I).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch02_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

W_, BETA, TH = 10.0, 1.0, 5.0
f = lambda x: 1 / (1 + np.exp(-BETA * (x - TH)))
aa = np.linspace(-0.02, 1.02, 600)


def s_curve(w=W_):
    """Exact curve of fixed points: a = f(w a + I)  <=>  I = f^{-1}(a) - w a, for 0 < a < 1.
    Stable where -1 + w f'(w a + I) < 0, i.e. w beta a (1 - a) < 1."""
    a = np.linspace(1e-5, 1 - 1e-5, 4000)
    I = TH - np.log(1 / a - 1) / BETA - w * a
    stable = w * BETA * a * (1 - a) < 1
    return I, a, stable


def plot_s(ax, w=W_, lw=2.4):
    I, a, st = s_curve(w)
    ax.plot(np.where(st, I, np.nan), a, color=K.INK, lw=lw, label="stable states")
    ax.plot(np.where(~st, I, np.nan), a, "--", color=K.INK, lw=lw * 0.65, label="unstable state")


def fixed_points(I):
    g = -aa + f(W_ * aa + I)
    idx = np.where(np.diff(np.sign(g)) != 0)[0]
    pts = []
    for k in idx:
        a0, a1 = aa[k], aa[k + 1]
        for _ in range(60):
            m = 0.5 * (a0 + a1)
            if np.sign(-a0 + f(W_ * a0 + I)) * np.sign(-m + f(W_ * m + I)) <= 0:
                a1 = m
            else:
                a0 = m
        a = 0.5 * (a0 + a1)
        slope = -1 + W_ * BETA * f(W_ * a + I) * (1 - f(W_ * a + I))
        pts.append((a, slope < 0))
    return pts


def graphical():
    """Fixed points are where the gain curve a -> f(w a + I) meets the diagonal; arrows on the line show the flow."""
    fig, axs = plt.subplots(1, 3, figsize=(12.4, 4.2), sharey=True)
    for ax, I, title in zip(axs, [-3.0, 0.0, 3.0], ["low input: one state (rest)", "middle input: three states", "high input: one state (active)"]):
        ax.plot(aa, aa, color=K.GREY, lw=1.4, ls="--", label="$a$")
        ax.plot(aa, f(W_ * aa + I), color=K.INK, lw=2.2, label="$f(wa + I)$")
        for a, st in fixed_points(I):
            ax.plot(a, a, "o", ms=10, color=K.ACC if st else "white", mec=K.INK, mew=1.6, zorder=6)
        # flow arrows along the bottom: sign of -a + f
        for a in np.linspace(0.05, 0.95, 10):
            g = -a + f(W_ * a + I)
            if abs(g) > 0.02:
                ax.annotate("", xy=(a + 0.035 * np.sign(g), -0.08), xytext=(a - 0.035 * np.sign(g), -0.08),
                            arrowprops=dict(arrowstyle="-|>", color=K.ACC2, lw=1.6))
        ax.axhline(-0.08, color=K.GREY, lw=0.6)
        ax.set_title(f"{title}\n$I = {I}$"); ax.set_xlabel("activity $a$")
        ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.14, 1.05)
    axs[0].set_ylabel("value"); axs[0].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch02_graphical", wide=True)


def slide_gif():
    """Raise I: the gain curve slides left past the diagonal; fixed points are born and die in pairs."""
    Is = np.r_[np.linspace(-4, 4, 70), np.linspace(4, -4, 70)]
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.3))
    ax = axs[0]
    ax.plot(aa, aa, color=K.GREY, lw=1.4, ls="--")
    curve, = ax.plot([], [], color=K.INK, lw=2.2)
    dots = ax.scatter([], [], s=80, zorder=6, edgecolor=K.INK, linewidths=1.5)
    lab = ax.text(0.03, 0.95, "", transform=ax.transAxes, va="top", fontsize=12, bbox=K.BOX)
    ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.05); ax.set_xlabel("activity $a$"); ax.set_title("$f(wa + I)$ against the diagonal")
    ax = axs[1]
    plot_s(ax, lw=2)
    marker = ax.axvline(-4, color=K.ACC2, lw=1.5)
    ax.set_xlim(-4.2, 4.2); ax.set_ylim(-0.03, 1.05); ax.set_xlabel("input $I$"); ax.set_ylabel("fixed points $a^*$")
    ax.set_title("all fixed points against $I$")

    def upd(k):
        I = Is[k]
        curve.set_data(aa, f(W_ * aa + I))
        fp = fixed_points(I)
        dots.set_offsets(np.array([[a, a] for a, _ in fp]))
        dots.set_facecolors([K.ACC if s else "white" for _, s in fp])
        lab.set_text(f"$I = {I:+.2f}$:  {len(fp)} fixed point{'s' if len(fp) > 1 else ''}")
        marker.set_xdata([I, I])
    K.save_gif(fig, upd, len(Is), "ch02_slide", fps=14, still_frame=50)


def auto_and_hysteresis():
    m = W.load("pop1", w=W_, beta=BETA, th=TH, i=-4.0, tau=1)
    m.set(a=0.0)
    m.run(total=60); m.run_last(total=20)
    eq = m.auto.run("i", start="steady", ds=0.02, dsmax=0.05, parmin=-4, parmax=4, nmax=2000)
    df = eq.to_pandas("a")
    # the folds (AUTO marks them LP, and sometimes BP in a one-variable system); keep one per fold
    cand = [p for p in eq.labeled() if p.type in ("LP", "BP")]
    lps = []
    for p in sorted(cand, key=lambda q: q.x):
        if not lps or abs(p.x - lps[-1].x) > 0.5:
            lps.append(p)
    lps = [p for p in lps if 0.02 < p.u0["a"] < 0.98]
    print("saddle-nodes at I =", [round(p.x, 4) for p in lps])
    K.savedata("ch02_auto", eq=df[["par", "ymax", "stable"]].to_numpy(float), lp=np.array([[p.x, p.u0["a"]] for p in lps]))
    # slow ramp of I up and down, simulated with XPP (I is a slow variable)
    r = W.load_text("""f(x)=1/(1+exp(-beta*(x-th)))
a'=(-a+f(w*a+i))/tau
i'=eps*sgn
sgn=if(t<tt)then(1)else(-1)
par w=10,beta=1,th=5,tau=1,eps=0.016,tt=500
init a=0.0,i=-4
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.1,total=1000,maxstor=200000
done""")
    tr = r.run(total=1000, dt=0.1)
    I_, A_ = np.asarray(tr["i"], float), np.asarray(tr["a"], float)
    t_ = np.asarray(tr.t, float)
    up = t_ < 500
    K.savedata("ch02_ramp", I=I_, A=A_, t=t_)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    plot_s(ax)
    for p in lps:
        ax.plot(p.x, p.u0["a"], "s", color=K.ORANGE, ms=9, zorder=6, label="saddle-node found by AUTO" if p is lps[0] else None)
    ax.plot(I_[up], A_[up], color=K.ACC2, lw=1.4, alpha=0.9, label="slow ramp up")
    ax.plot(I_[~up], A_[~up], color=K.ACC, lw=1.4, alpha=0.9, label="slow ramp down")
    ax.set_xlim(-4, 4); ax.set_ylim(-0.03, 1.05); ax.set_xlabel("input $I$"); ax.set_ylabel("activity $a$")
    ax.legend(fontsize=9, loc="center right"); ax.set_title("an S-shaped curve of states and a hysteresis loop")
    K.save(fig, "ch02_hysteresis")
    # cusp: continue both folds in (I, w)
    lp0 = [p for p in eq.special("LP")][0]
    up_ = m.auto.run(grab=lp0.label, param2="w", ds=0.02, nmax=600, parmin=-30, parmax=14)
    dn_ = m.auto.run(grab=lp0.label, ds=-0.02)
    pts = [(p.x, p.par["w"]) for c in (up_, dn_) for p in c]
    pts = np.array(sorted(pts, key=lambda z: z[1]))
    K.savedata("ch02_cusp", pts=pts)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(pts[:, 0], pts[:, 1], ".", color=K.ACC2, ms=3, label="saddle-nodes (AUTO, two parameters)")
    ax.axhline(W_, color=K.GREY, lw=0.8, ls=":")
    ax.text(-11, W_ + 0.2, "$w = 10$ (Figures 2.1–2.3)", fontsize=10, color=K.GREY)
    ax.text(-0.9, 9.0, "bistable", fontsize=12, color=K.ACC2)
    ax.text(-9, 3.0, "one state", fontsize=12, color=K.INK)
    ax.set_xlabel("input $I$"); ax.set_ylabel("recurrent weight $w$"); ax.set_title("the cusp: bistability needs strong recurrence")
    ax.set_xlim(-12, 6); ax.set_ylim(0, 13); ax.legend(fontsize=9, loc="upper right")
    K.save(fig, "ch02_cusp")
    wc = 4 / BETA
    print("cusp: w_min (analytic 4/beta) =", wc, " numerical min w on fold curve:", pts[:, 1].min())


def switch():
    """Working memory: a brief pulse switches the population on; a brief negative pulse switches it off."""
    r = W.load_text("""f(x)=1/(1+exp(-beta*(x-th)))
a'=(-a+f(w*a+i+pulse(t)))/tau
pulse(t)=3*heav(t-20)*heav(22-t)-3*heav(t-60)*heav(62-t)
par w=10,beta=1,th=5,tau=1,i=0
init a=0.0
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.05,total=90,maxstor=200000
done""")
    tr = r.run(total=90, dt=0.05)
    t, a = np.asarray(tr.t, float), np.asarray(tr["a"], float)
    K.savedata("ch02_switch", t=t, a=a)
    fig, axs = plt.subplots(2, 1, figsize=(8.4, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 2]})
    pulse = 3 * ((t > 20) & (t < 22)) - 3 * ((t > 60) & (t < 62))
    axs[0].plot(t, pulse, color=K.ORANGE, lw=1.8); axs[0].set_ylabel("extra input"); axs[0].set_title("a brief pulse is remembered")
    axs[1].plot(t, a, color=K.ACC2, lw=2); axs[1].set_ylabel("activity $a$"); axs[1].set_xlabel("time $t$")
    axs[1].set_ylim(-0.03, 1.05)
    fig.tight_layout()
    K.save(fig, "ch02_switch", wide=True)


if __name__ == "__main__":
    graphical()
    auto_and_hysteresis()
    slide_gif()
    switch()
