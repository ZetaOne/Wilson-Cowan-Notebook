"""Chapter 9 figures: Turing instability of a neural field, patterns, and Ermentrout-Cowan hallucinations.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch09_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K
from ch08_figs import field_text, run_field

A, C = 1.5, 0.6                      # same Mexican hat as chapter 8 (1-D)


def what(k):
    """Fourier transform of w(x) = A exp(-x^2) - C exp(-(x/3)^2)."""
    return np.sqrt(np.pi) * (A * np.exp(-k ** 2 / 4) - 3 * C * np.exp(-9 * k ** 2 / 4))


KG = np.linspace(0, 4, 2000)
KC = KG[np.argmax(what(KG))]
GC = 1 / what(KG).max()              # critical gain f'(u0)


def dispersion():
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2))
    ax = axs[0]
    ax.plot(KG, what(KG), color=K.INK, lw=2.2)
    ax.axhline(0, color=K.GREY, lw=0.8)
    ax.axvline(KC, color=K.ORANGE, ls="--", lw=1.2)
    ax.text(KC + 0.12, what(KC) * 0.98, f"$k_c = {KC:.2f}$", color=K.ORANGE, fontsize=11)
    ax.set_xlabel("wavenumber $k$"); ax.set_ylabel("$\\hat w(k)$"); ax.set_title("the kernel in Fourier space peaks away from $k = 0$")
    ax = axs[1]
    for g, col in [(0.6 * GC, K.BLUE), (GC, K.ORANGE), (1.3 * GC, K.ACC2)]:
        ax.plot(KG, -1 + g * what(KG), color=col, lw=2.2, label=f"gain $= {g / GC:.1f}\\,\\gamma_c$")
    ax.axhline(0, color=K.GREY, lw=0.8)
    lam = -1 + 1.3 * GC * what(KG)
    ax.fill_between(KG, 0, lam, where=lam > 0, color=K.ACC2, alpha=0.2)
    ax.set_xlabel("wavenumber $k$"); ax.set_ylabel("growth rate $\\lambda(k) = -1 + \\gamma\\,\\hat w(k)$")
    ax.set_title("raising the gain: a band of wavelengths grows"); ax.legend(fontsize=9, loc="lower right")
    ax.set_ylim(-2.2, 0.6)
    fig.tight_layout()
    K.save(fig, "ch09_dispersion", wide=True)
    print("k_c", KC, "wavelength", 2 * np.pi / KC, "critical gain", GC)


def ring():
    """A ring of N populations, uniform state at threshold with gain 1.3 gamma_c: noise grows into a periodic
    pattern with wavelength near 2 pi / k_c."""
    N, L = 256, 64.0
    dx = L / N; M = int(9 / dx)
    gain = 1.3 * GC
    b = 4 * gain                       # f'(th) = b/4 for the logistic
    th = 0.0
    I0 = th - what(0.0) * 0.5          # makes u = th a uniform steady state
    rng = np.random.default_rng(3)
    init = "\n".join(f"init u{j}={th + 0.01 * rng.standard_normal():.5f}" for j in range(N))
    txt = field_text(N, dx, M, f"({A}*exp(-x^2)-{C}*exp(-(x/3)^2))", "-u[j]+k([j])+i0",
                     extra=f"par b={b},th={th},i0={I0}", init=init, total=60, dt=0.02)
    t, o = run_field(txt, N, total=60, dt=0.02, nout=10)
    u = o["u"]
    xs = np.arange(N) * dx
    spec = np.abs(np.fft.rfft(u[:, -1] - u[:, -1].mean()))
    kk = 2 * np.pi * np.fft.rfftfreq(N, d=dx)
    kmeas = kk[np.argmax(spec)]
    K.savedata("ch09_ring", t=t, x=xs, u=u, kc=KC, kmeas=kmeas)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axs[0]
    im = ax.pcolormesh(t, xs, u, cmap="RdBu_r", shading="auto", rasterized=True)
    ax.set_xlabel("time"); ax.set_ylabel("position on the ring $x$"); ax.set_title("noise grows into a periodic pattern")
    fig.colorbar(im, ax=ax, label="$u - \\theta$", pad=0.02)
    ax = axs[1]
    ax.plot(xs, u[:, -1], color=K.ACC2, lw=2)
    ax.set_xlabel("position $x$"); ax.set_ylabel("$u$ at the end")
    ax.set_title(f"wavelength {2 * np.pi / kmeas:.2f} (theory $2\\pi/k_c = {2 * np.pi / KC:.2f}$)")
    fig.tight_layout()
    K.save(fig, "ch09_ring", wide=True)
    print("measured k", kmeas, "theory", KC)


def sheet(bias, n=128, L=64.0, T=80.0, dt=0.1, seed=1):
    """2-D Amari field on a torus, integrated with FFT convolution (XPP's conv() is 1-D only).
    Kernel: radially symmetric difference of Gaussians with the same 1-D shape."""
    x = (np.arange(n) - n // 2) * (L / n)
    X, Y = np.meshgrid(x, x)
    R2 = X ** 2 + Y ** 2
    w = (A * np.exp(-R2) / np.sqrt(np.pi) - C * np.exp(-R2 / 9) / (3 * np.sqrt(np.pi))) * (L / n) ** 2
    wf = np.fft.fft2(np.fft.ifftshift(w))
    w0 = wf[0, 0].real
    kmax = np.abs(wf).real.max()
    gain = 1.3 / np.real(wf).max()
    b = 4 * gain
    f = lambda u: 1 / (1 + np.exp(-b * (u - bias)))
    I0 = 0.0 - w0 * f(0.0)
    rng = np.random.default_rng(seed)
    u = 0.01 * rng.standard_normal((n, n))
    for _ in range(int(T / dt)):
        conv = np.real(np.fft.ifft2(wf * np.fft.fft2(f(u))))
        u = u + dt * (-u + conv + I0)
    return x, u


def patterns2d():
    x, us = sheet(0.0, n=96, L=40.0, T=150.0)
    _, uh = sheet(0.25, n=96, L=40.0, T=150.0)
    _, uo = sheet(-0.25, n=96, L=40.0, T=150.0)
    K.savedata("ch09_2d", x=x, stripes=us, spots=uh, holes=uo)
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.4))
    for ax, u, ttl in [(axs[0], us, "symmetric gain: stripes"), (axs[1], uh, "threshold above rest: spots"),
                       (axs[2], uo, "threshold below rest: holes")]:
        ax.imshow(u, cmap="RdBu_r", extent=[x[0], x[-1], x[0], x[-1]], origin="lower")
        ax.set_title(ttl); ax.set_xlabel("cortical position $x_1$")
    axs[0].set_ylabel("$x_2$")
    fig.tight_layout()
    K.save(fig, "ch09_2d", wide=True)


def logpolar_maps():
    """Ermentrout-Cowan: the retino-cortical map is (approximately) complex log, z_cortex = log(z_retina).
    Stripes in cortex map to funnels, tunnels and spirals in the visual field."""
    fig, axs = plt.subplots(2, 4, figsize=(14.4, 7.4))
    n = 500
    # cortex coordinates (x1, x2) = (log r, phi)
    x1 = np.linspace(-1.5, 2.2, n); x2 = np.linspace(-np.pi, np.pi, n)
    X1, X2 = np.meshgrid(x1, x2)
    cases = [("vertical stripes", lambda a, b: np.cos(6 * a), "tunnel (rings)"),
             ("horizontal stripes", lambda a, b: np.cos(8 * b), "funnel (rays)"),
             ("oblique stripes", lambda a, b: np.cos(5 * a + 6 * b), "spiral")]
    xr = np.linspace(-1, 1, n)
    XR, YR = np.meshgrid(xr, xr)
    r = np.hypot(XR, YR) * np.exp(2.2); ph = np.arctan2(YR, XR)
    LR = np.log(np.maximum(r, 1e-6))
    for j, (ttl, pat, name) in enumerate(cases):
        ax = axs[0, j]
        ax.imshow(pat(X1, X2) > 0, cmap="Greys", origin="lower", extent=[x1[0], x1[-1], x2[0], x2[-1]], aspect="auto")
        ax.set_title(f"in cortex: {ttl}"); ax.set_xlabel("$x_1 = \\log r$"); ax.set_ylabel("$x_2 = \\varphi$")
        ax = axs[1, j]
        img = pat(LR, ph) > 0
        img = np.where(np.hypot(XR, YR) <= 1, img, np.nan)
        ax.imshow(img, cmap="Greys", origin="lower", extent=[-1, 1, -1, 1])
        ax.set_title(f"seen: a {name}"); ax.axis("off")
    kx = 6 * np.sqrt(3) / 2
    def spots(a, b):          # hexagonal lattice: three plane waves at 120 degrees, periodic in phi
        return np.cos(6 * b) + np.cos(kx * a - 3 * b) + np.cos(kx * a + 3 * b) - 1.2
    ax = axs[0, 3]
    ax.imshow(spots(X1, X2) > 0, cmap="Greys", origin="lower", extent=[x1[0], x1[-1], x2[0], x2[-1]], aspect="auto")
    ax.set_title("in cortex: hexagonal spots"); ax.set_xlabel("$x_1 = \\log r$")
    ax = axs[1, 3]
    img = np.where(np.hypot(XR, YR) <= 1, spots(LR, ph) > 0, np.nan)
    ax.imshow(img, cmap="Greys", origin="lower", extent=[-1, 1, -1, 1]); ax.set_title("seen: a lattice of blobs"); ax.axis("off")
    fig.tight_layout()
    K.save(fig, "ch09_logpolar", wide=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["dispersion", "ring", "patterns2d", "logpolar_maps"]
    for w in which:
        globals()[w]()
