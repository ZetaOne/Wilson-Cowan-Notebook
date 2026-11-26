"""Chapter 8 figures: neural fields (Wilson-Cowan 1973, Amari 1977): bumps, fronts, travelling pulses.
All fields are simulated in XPPAUT (arrays + the conv() special for the spatial integral).
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch08_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import wc_lib as W
import figkit as K

# Mexican-hat kernel for bumps: w(x) = A exp(-x^2) - C exp(-(x/3)^2)
A_MH, C_MH = 1.5, 0.6
THETA_B = 0.3


def w_mh(x):
    return A_MH * np.exp(-x ** 2) - C_MH * np.exp(-(x / 3) ** 2)


def field_text(N, dx, M, kernel, rhs_u, extra="", init="", total=60, dt=0.02, boundary="periodic"):
    """XPP text for a 1-D field u[0..N-1] with  k_j = sum_m w(m dx) dx f(u_{j+m}),  i.e. the convolution of the
    kernel with the firing rate.  `kernel` is an expression in the distance x; `rhs_u` uses k([j]), u[j], x=[j]*dx."""
    return f"""# 1-D neural field
f(z)=1/(1+exp(-b*(z-th)))
table w % {2 * M + 1} {-M} {M} ({dx})*{re.sub(r'\bx\b', f'(t*{dx})', kernel)}
fu[0..{N - 1}]=f(u[j])
special k=conv({boundary},{N},{M},w,fu0)
u[0..{N - 1}]'={rhs_u}
{extra}
{init}
@ meth=rk4,dt={dt},total={total},maxstor=20000,bound=1e6
done
"""


def run_field(text, N, names=("u",), total=60, dt=0.02, nout=1, **pars):
    m = W.load_text(text)
    if pars:
        m.set(**pars)
    tr = m.run(total=total, dt=dt)
    t = np.asarray(tr.t)[::nout]
    out = {nm: np.array([np.asarray(tr[f"{nm}{j}"])[::nout] for j in range(N)]) for nm in names}
    return t, out


def bump_width_curve():
    d = np.linspace(0.005, 6, 600)
    Wd = np.array([quad(w_mh, 0, x)[0] for x in d])
    return d, Wd


def kernel_fig():
    """Amari's construction: a bump of width a exists where W(a) = int_0^a w = theta (the input at its edge)."""
    x = np.linspace(-8, 8, 800)
    d, Wd = bump_width_curve()
    k = np.where(np.diff(np.sign(Wd - THETA_B)) != 0)[0]
    roots = d[k]
    K.savedata("ch08_kernel", x=x, w=w_mh(x), d=d, Wd=Wd, roots=roots)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2))
    ax = axs[0]
    ax.fill_between(x, 0, w_mh(x), where=w_mh(x) > 0, color=K.ACC2, alpha=0.25)
    ax.fill_between(x, 0, w_mh(x), where=w_mh(x) < 0, color=K.BLUE, alpha=0.25)
    ax.plot(x, w_mh(x), color=K.INK, lw=2.2)
    ax.axhline(0, color=K.GREY, lw=0.8)
    ax.text(0, 0.55, "near: excite", ha="center", color=K.ACC2, fontsize=11)
    ax.text(4.2, -0.32, "far: inhibit", ha="center", color=K.BLUE, fontsize=11)
    ax.set_xlabel("distance $x - y$"); ax.set_ylabel("$w(x - y)$"); ax.set_title("a ‘Mexican hat’ connectivity")
    ax = axs[1]
    ax.plot(d, Wd, color=K.INK, lw=2.2, label="$W(a) = \\int_0^{a} w(x)\\,dx$")
    ax.axhline(THETA_B, color=K.ORANGE, lw=1.6, ls="--", label=f"threshold $\\theta = {THETA_B}$")
    for r, lab, col in zip(roots, ["unstable (too narrow)", "stable bump"], [K.GREY, K.ACC2]):
        ax.plot(r, THETA_B, "o", ms=10, mfc="white" if col == K.GREY else col, mec=K.INK, zorder=6)
        ax.annotate(f"{lab}\n$a = {r:.2f}$", (r, THETA_B), (r + 0.35, THETA_B - 0.27), fontsize=9.5, color=col,
                    arrowprops=dict(arrowstyle="-", color=col))
    ax.axhline(0, color=K.GREY, lw=0.8)
    ax.set_xlabel("width of the active region $a$"); ax.set_ylabel("input at the edge of the bump")
    ax.set_title("Amari's condition: $W(a) = \\theta$"); ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    K.save(fig, "ch08_kernel", wide=True)
    print("bump widths", roots)
    return roots


def bump():
    """A brief localised stimulus leaves a self-sustained bump (working memory); a weaker one dies away."""
    N, L = 240, 30.0
    dx = L / N; M = int(9 / dx)
    rhs = "-u[j]+k([j])+s*exp(-(([j]-120)*%g)^2)*heav(ton-t)" % dx
    txt = field_text(N, dx, M, f"({A_MH}*exp(-x^2)-{C_MH}*exp(-(x/3)^2))", rhs,
                     extra=f"par b=50,th={THETA_B},s=1,ton=5", total=40, dt=0.02)
    res = {}
    for s in (0.12, 1.0):
        t, o = run_field(txt, N, total=40, dt=0.02, nout=10, s=s)
        res[s] = o["u"]
    xs = (np.arange(N) - N // 2) * dx
    K.savedata("ch08_bump", t=t, x=xs, weak=res[0.12], strong=res[1.0])
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.2), gridspec_kw={"width_ratios": [1, 1, 1.05]})
    for ax, s, ttl in [(axs[0], 0.12, "weak stimulus: fades"), (axs[1], 1.0, "strong stimulus: a bump persists")]:
        im = ax.pcolormesh(t, xs, res[s], cmap="magma", shading="auto", vmin=-0.3, vmax=0.6, rasterized=True)
        ax.axvline(5, color="w", lw=1, ls="--")
        ax.set_xlabel("time"); ax.set_title(ttl); ax.set_ylim(-8, 8)
    axs[0].set_ylabel("position $x$")
    fig.colorbar(im, ax=axs[1], label="$u(x, t)$", pad=0.02)
    ax = axs[2]
    u = res[1.0][:, -1]
    ax.plot(xs, u, color=K.ACC2, lw=2.4, label="$u(x)$ at $t = 40$")
    ax.axhline(THETA_B, color=K.ORANGE, ls="--", lw=1.4, label="threshold $\\theta$")
    act = xs[u > THETA_B]
    if len(act):
        ax.axvspan(act.min(), act.max(), color=K.ACC2, alpha=0.12)
        print("simulated bump width", act.max() - act.min() + (x_dx := xs[1] - xs[0]))
    ax.set_xlim(-8, 8); ax.set_xlabel("position $x$"); ax.set_title("the bump: active where $u > \\theta$"); ax.legend(fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch08_bump", wide=True)


def front():
    """Purely excitatory exponential kernel w = exp(-|x|)/2: a bistable field supports a travelling front with
    speed c = (1 - 2 theta)/(2 theta) (Heaviside limit)."""
    N, L = 400, 80.0
    dx = L / N; M = int(12 / dx)
    rhs = "-u[j]+k([j])"
    txt = field_text(N, dx, M, "0.5*exp(-abs(x))", rhs, extra="par b=200,th=0.3\ninit u[0..40]=1",
                     total=30, dt=0.01, boundary="even")
    thetas = [0.2, 0.25, 0.3, 0.35, 0.4]
    speeds = []
    xs = np.arange(N) * dx
    keep = None
    for th in thetas:
        t, o = run_field(txt, N, total=30, dt=0.01, nout=10, th=th)
        u = o["u"]
        pos = np.array([xs[np.where(u[:, k] > th)[0].max()] if (u[:, k] > th).any() else np.nan for k in range(len(t))])
        sel = (t > 8) & (pos < L - 10)
        c = np.polyfit(t[sel], pos[sel], 1)[0]
        speeds.append(c)
        if th == 0.3:
            keep = (t, u, pos)
    speeds = np.array(speeds)
    K.savedata("ch08_front", thetas=np.array(thetas), speeds=speeds, t=keep[0], x=xs, u=keep[1])
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axs[0]
    ax.pcolormesh(keep[0], xs, keep[1], cmap="magma", shading="auto", rasterized=True)
    ax.set_xlabel("time"); ax.set_ylabel("position $x$"); ax.set_title("a front invades the resting field ($\\theta = 0.3$)")
    ax = axs[1]
    th = np.linspace(0.15, 0.45, 100)
    ax.plot(th, (1 - 2 * th) / (2 * th), color=K.INK, lw=2, label="theory $c = (1 - 2\\theta)/2\\theta$")
    ax.plot(thetas, speeds, "o", ms=9, color=K.ACC2, mec="k", label="XPPAUT simulation")
    ax.set_xlabel("threshold $\\theta$"); ax.set_ylabel("front speed $c$"); ax.legend(fontsize=9)
    ax.set_title("front speed: theory and simulation")
    fig.tight_layout()
    K.save(fig, "ch08_front", wide=True)
    print("front speeds", dict(zip(thetas, speeds.round(3))), "theory", [(1 - 2 * a) / (2 * a) for a in thetas])


def pulse():
    """Add slow negative feedback (adaptation) v: the front's back is pulled up and a travelling pulse forms
    (Pinto & Ermentrout 2001)."""
    N, L = 400, 100.0
    dx = L / N; M = int(12 / dx)
    rhs = "-u[j]+k([j])-v[j]"
    extra = f"v[0..{N - 1}]'=eps*(bet*u[j]-v[j])\npar b=100,th=0.2,eps=0.03,bet=5\ninit u[0..20]=1"
    txt = field_text(N, dx, M, "0.5*exp(-abs(x))", rhs, extra=extra, total=80, dt=0.02, boundary="even")
    t, o = run_field(txt, N, names=("u", "v"), total=80, dt=0.02, nout=10)
    xs = np.arange(N) * dx
    K.savedata("ch08_pulse", t=t, x=xs, u=o["u"], v=o["v"])
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axs[0]
    ax.pcolormesh(t, xs, o["u"], cmap="magma", shading="auto", rasterized=True)
    ax.set_xlabel("time"); ax.set_ylabel("position $x$"); ax.set_title("with adaptation: a travelling pulse")
    ax = axs[1]
    k = int(0.6 * len(t))
    ax.plot(xs, o["u"][:, k], color=K.ACC2, lw=2.2, label="activity $u$")
    ax.plot(xs, o["v"][:, k], color=K.BLUE, lw=2.2, label="adaptation $v$")
    ax.axhline(0.2, color=K.ORANGE, ls="--", lw=1.2, label="threshold")
    ax.set_xlabel("position $x$"); ax.set_title(f"snapshot at $t = {t[k]:.0f}$: the pulse moves right"); ax.legend(fontsize=9)
    fig.tight_layout()
    K.save(fig, "ch08_pulse", wide=True)
    act = (o["u"] > 0.2)
    print("pulse active at end:", act[:, -1].sum(), "cells; max u", o["u"][:, -1].max())


def bump_gif():
    d = K.loaddata("ch08_bump")
    t, x, U = d["t"], d["x"], d["strong"]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ln, = ax.plot([], [], color=K.ACC2, lw=2.4)
    ax.axhline(THETA_B, color=K.ORANGE, ls="--", lw=1.2)
    stim, = ax.plot([], [], color=K.BLUE, lw=1.4, ls=":")
    lab = ax.text(0.03, 0.95, "", transform=ax.transAxes, va="top", fontsize=11, bbox=K.BOX)
    ax.set_xlim(-8, 8); ax.set_ylim(-0.4, 1.3); ax.set_xlabel("position $x$"); ax.set_ylabel("$u(x, t)$")
    ax.set_title("a bump outlives its stimulus")
    idx = np.r_[np.arange(0, len(t), 2)]

    def upd(f):
        k = idx[f]
        ln.set_data(x, U[:, k])
        stim.set_data(x, np.exp(-x ** 2) if t[k] < 5 else np.full_like(x, np.nan))
        lab.set_text(f"$t = {t[k]:.1f}$" + ("  stimulus on" if t[k] < 5 else "  stimulus off"))
    K.save_gif(fig, upd, len(idx), "ch08_bumpgif", fps=12)


if __name__ == "__main__":
    which = sys.argv[1:] or ["kernel_fig", "bump", "front", "pulse", "bump_gif"]
    for w in which:
        globals()[w]()
