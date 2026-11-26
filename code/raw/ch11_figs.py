"""Chapter 11 figures: STM models, the Cohen-Grossberg/Hopfield energy, and associative memory.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch11_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

# two-unit STM network  u' = -u + W f(u) + I,  f logistic, W symmetric (mutual inhibition)
B = 1.0
W2 = np.array([[0.0, -8.0], [-8.0, 0.0]])
I2 = np.array([4.0, 4.0])


def f(u):
    return 1 / (1 + np.exp(-B * u))


def energy2(u1, u2):
    a1, a2 = f(u1), f(u2)
    ent = lambda a: (a * np.log(a) + (1 - a) * np.log(1 - a)) / B   # int_0^a f^{-1}, up to a constant
    return -0.5 * (W2[0, 1] * a1 * a2 * 2) - I2[0] * a1 - I2[1] * a2 + ent(a1) + ent(a2)


TWO = f"""# two-unit STM network with symmetric mutual inhibition
f(u)=1/(1+exp(-b*u))
u1'=-u1+w12*f(u2)+i1
u2'=-u2+w21*f(u1)+i2
par b={B},w12={W2[0, 1]},w21={W2[1, 0]},i1={I2[0]},i2={I2[1]}
init u1=0.1,u2=0
@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.02,total=20
done
"""


def energy_fig():
    m = W.load_text(TWO)
    g = np.linspace(-6, 6, 300)
    U1, U2 = np.meshgrid(g, g)
    E = energy2(U1, U2)
    starts = [(-4, -3), (-3, -4.5), (5, 4.5), (4.5, 5.5), (0.5, -5), (-5, 0.4), (2, 2.3), (-1, -1.2), (5.5, -1), (-1, 5.5)]
    paths = []
    for u0 in starts:
        m.set(u1=float(u0[0]), u2=float(u0[1]), w12=W2[0, 1], w21=W2[1, 0])
        tr = m.run(total=20, dt=0.02)
        paths.append(np.column_stack([tr.t, tr["u1"], tr["u2"]]))
    K.savedata("ch11_energy", g=g, E=E, paths=np.array([p for p in paths]))
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.8), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axs[0]
    cs = ax.contourf(g, g, E, levels=30, cmap="Blues_r", alpha=0.85)
    ax.contour(g, g, E, levels=30, colors="w", linewidths=0.3)
    fig.colorbar(cs, ax=ax, label="energy $L(\\vec u)$", pad=0.02)
    for p, col in zip(paths, plt.cm.autumn(np.linspace(0, 0.9, len(paths)))):
        ax.plot(p[:, 1], p[:, 2], color=col, lw=1.8)
        ax.plot(p[0, 1], p[0, 2], "o", ms=4, color=col)
    ax.set_xlabel("$u_1$"); ax.set_ylabel("$u_2$"); ax.set_title("symmetric weights: trajectories run downhill")
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6)
    ax = axs[1]
    for p, col in zip(paths, plt.cm.autumn(np.linspace(0, 0.9, len(paths)))):
        ax.plot(p[:, 0], energy2(p[:, 1], p[:, 2]), color=col, lw=1.8)
    ax.set_xlabel("time"); ax.set_ylabel("$L(\\vec u(t))$"); ax.set_title("the energy never increases")
    fig.tight_layout()
    K.save(fig, "ch11_energy", wide=True)


def asymmetric():
    """The E-I oscillator in STM form: weights are not symmetric (E excites I, I inhibits E). The same energy
    formula is not a Lyapunov function: it oscillates along the limit cycle."""
    pars = dict(c1=16, c2=12, c3=15, c4=3, ae=1.3, the=4, ai=2, thi=3.7, p=1.25, q=0)
    m = W.load("stm", **pars)
    m.set(ue=0.5, ui=0.2)
    tr = m.run(total=60, dt=0.01)
    t = np.asarray(tr.t); ue = np.asarray(tr["ue"]); ui = np.asarray(tr["ui"])

    def S(x, a, th):
        return 1 / (1 + np.exp(-a * (x - th))) - 1 / (1 + np.exp(a * th))
    fe, fi = S(ue, 1.3, 4), S(ui, 2, 3.7)
    # symmetrised energy  -1/2 a^T W_sym a - I.a  (entropy terms omitted: they don't change the picture)
    Wm = np.array([[16, -12], [15, -3]], float)
    Ws = 0.5 * (Wm + Wm.T)
    a = np.vstack([fe, fi])
    Lsym = -0.5 * np.einsum("it,ij,jt->t", a, Ws, a) - 1.25 * fe
    K.savedata("ch11_asym", t=t, ue=ue, ui=ui, L=Lsym)
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.2))
    axs[0].plot(ue, ui, color=K.ACC2, lw=1.6)
    axs[0].set_xlabel("$s_E$"); axs[0].set_ylabel("$s_I$"); axs[0].set_title("E–I network (STM form): $w_{EI} \\neq w_{IE}$, a limit cycle")
    axs[1].plot(t, Lsym, color=K.BLUE, lw=1.8)
    axs[1].set_xlabel("time"); axs[1].set_ylabel("symmetric-weight ‘energy’")
    axs[1].set_title("no Lyapunov function: the ‘energy’ goes up and down")
    fig.tight_layout()
    K.save(fig, "ch11_asym", wide=True)


# ---------------- Hopfield network ----------------
def patterns():
    P = np.zeros((3, 8, 8))
    P[0][3:5, :] = 1; P[0][:, 3:5] = 1                      # plus
    P[1][[0, 7], :] = 1; P[1][:, [0, 7]] = 1                 # square
    for i in range(8):                                       # diagonal cross
        P[2][i, i] = 1; P[2][i, 7 - i] = 1
        if i < 7:
            P[2][i, i + 1] = 1; P[2][i + 1, i] = 1
    return 2 * P.reshape(3, 64) - 1                          # +-1 patterns


def hopfield():
    xi = patterns()
    N = xi.shape[1]
    Wm = (xi.T @ xi) / N
    np.fill_diagonal(Wm, 0)
    tab = K.DATA / "ch11_hopfield_w.tab"
    with open(tab, "w") as fh:
        fh.write(f"{N * N}\n0\n{N * N - 1}\n" + "\n".join(f"{v:.8g}" for v in Wm.ravel()) + "\n")
    txt = f"""# continuous Hopfield network: u_i' = -u_i + sum_j W_ij tanh(b u_j)
table w {tab}
g[0..{N - 1}]=tanh(b*u[j])
special k=mmult({N},{N},w,g0)
u[0..{N - 1}]'=-u[j]+k([j])
par b=4
@ meth=rk4,dt=0.02,total=12,maxstor=5000
done
"""
    m = W.load_text(txt)
    rng = np.random.default_rng(4)
    cue = xi[0].copy()
    flip = rng.choice(N, 18, replace=False); cue[flip] *= -1   # 28% of pixels wrong
    m.set(**{f"u{j}": float(0.3 * cue[j]) for j in range(N)})
    tr = m.run(total=12, dt=0.02)
    t = np.asarray(tr.t)
    U = np.array([np.asarray(tr[f"u{j}"]) for j in range(N)])
    Gs = np.tanh(4 * U)
    overlaps = xi @ Gs / N
    En = -0.5 * np.einsum("it,ij,jt->t", Gs, Wm, Gs)
    K.savedata("ch11_hopfield", t=t, U=U, xi=xi, cue=cue, overlaps=overlaps, E=En)
    fig = plt.figure(figsize=(12.6, 5.6))
    gs = fig.add_gridspec(2, 6, height_ratios=[1, 1.15])
    for k in range(3):
        ax = fig.add_subplot(gs[0, k]); ax.imshow(xi[k].reshape(8, 8), cmap="Greys", vmin=-1, vmax=1)
        ax.set_title(f"stored pattern {k + 1}", fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    snaps = [0, np.searchsorted(t, 0.4), np.searchsorted(t, 1.0), len(t) - 1]
    for j, kk in enumerate(snaps[:3]):
        ax = fig.add_subplot(gs[0, 3 + j])
        img = cue if kk == 0 else Gs[:, kk]
        ax.imshow(img.reshape(8, 8), cmap="Greys", vmin=-1, vmax=1)
        ax.set_title("noisy cue" if kk == 0 else f"$t = {t[kk]:.1f}$", fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    ax = fig.add_subplot(gs[1, :3])
    for k, col in zip(range(3), [K.ACC2, K.BLUE, K.ORANGE]):
        ax.plot(t, overlaps[k], color=col, lw=2, label=f"overlap with pattern {k + 1}")
    ax.set_xlabel("time"); ax.set_ylabel("overlap $m_\\mu$"); ax.legend(fontsize=9); ax.set_title("recall: the overlap with pattern 1 goes to 1")
    ax = fig.add_subplot(gs[1, 3:])
    ax.plot(t, En, color=K.INK, lw=2)
    ax.set_xlabel("time"); ax.set_ylabel("energy $-\\frac{1}{2}\\sum W_{ij}g_ig_j$"); ax.set_title("while the energy falls into a valley")
    fig.tight_layout()
    K.save(fig, "ch11_hopfield", wide=True)
    print("final overlaps", overlaps[:, -1])


if __name__ == "__main__":
    which = sys.argv[1:] or ["energy_fig", "asymmetric", "hopfield"]
    for w in which:
        globals()[w]()
