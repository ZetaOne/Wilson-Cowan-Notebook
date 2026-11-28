"""Chapter 13 figures: mean field theory for a spiking (theta-neuron) network: phase density, the Klimontovich
equation, where the gain function comes from, and the exact Montbrio-Pazo-Roxin mean field.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch13_figs.py [name ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import wc_lib as W
import figkit as K

TH = np.linspace(-np.pi, np.pi, 721)


def Fth(th, eta):
    return 1 - np.cos(th) + (1 + np.cos(th)) * eta


def identical_pop(eta, N, th0, total, dt=0.01):
    txt = f"""# {N} identical theta-neurons, no coupling
par eta={eta}
th[1..{N}]'=1-cos(th[j])+(1+cos(th[j]))*eta
""" + "\n".join(f"init th{k + 1}={th0[k]:.6f}" for k in range(N)) + f"""
@ meth=cvode,tol=1e-9,atol=1e-9,dt={dt},total={total},maxstor=200000,bound=1e9
done
"""
    m = W.load_text(txt)
    tr = m.run(total=total, dt=dt)
    t = np.asarray(tr.t)
    th = np.column_stack([np.asarray(tr[f"th{k}"]) for k in range(1, N + 1)])
    return t, th


def density():
    """Steady density of phases is C/F(theta): neurons pile up where they move slowly."""
    eta = 0.3
    T = np.pi / np.sqrt(eta)
    N = 200
    # stationary ('splay') state: neurons equally spaced in TIME along the orbit
    # theta(t) for a single neuron starting at -pi: tan(theta/2) = sqrt(eta) tan(sqrt(eta) t - pi/2)
    tt = (np.arange(N) + 0.5) / N * T
    th0 = 2 * np.arctan(np.sqrt(eta) * np.tan(np.sqrt(eta) * tt - np.pi / 2))
    t, th = identical_pop(eta, N, th0, total=3 * T)
    ph = np.mod(th[-1] + np.pi, 2 * np.pi) - np.pi
    C = 1 / np.trapezoid(1 / Fth(TH, eta), TH)
    # uniform start: no relaxation (dissipation-free)
    th0u = np.linspace(-np.pi, np.pi, N, endpoint=False)
    tu, thu = identical_pop(eta, N, th0u, total=6 * T)
    k = np.floor((thu + np.pi) / (2 * np.pi))
    idx = np.argwhere(np.diff(k, axis=0) > 0)
    spu = tu[idx[:, 0] + 1]
    edges = np.arange(0, tu[-1], 0.25)
    hu, _ = np.histogram(spu, edges)
    K.savedata("ch13_density", th=TH, F=Fth(TH, eta), C=C, phases=ph, tu=0.5 * (edges[1:] + edges[:-1]), ru=hu / (N * 0.25))
    fig, axs = plt.subplots(1, 3, figsize=(13.0, 4.1))
    ax = axs[0]
    ax.plot(TH, Fth(TH, eta), color=K.INK, lw=2.2)
    ax.set_xlabel("phase $\\theta$"); ax.set_ylabel("speed $F(\\theta) = \\dot\\theta$")
    ax.set_title(f"a θ-neuron's speed around its cycle ($\\eta = {eta}$)")
    ax.axvline(np.pi, color=K.ORANGE, lw=1, ls="--"); ax.text(np.pi - 0.1, 0.4, "spike", ha="right", color=K.ORANGE)
    ax = axs[1]
    ax.hist(ph, bins=36, range=(-np.pi, np.pi), density=True, color=K.ACC2, alpha=0.45, label=f"{N} neurons (XPPAUT)")
    ax.plot(TH, C / Fth(TH, eta), color=K.INK, lw=2.2, label="$C/F(\\theta)$")
    ax.set_xlabel("phase $\\theta$"); ax.set_ylabel("density $\\eta(\\theta)$"); ax.legend(fontsize=9)
    ax.set_title("steady state: crowded where neurons are slow")
    ax = axs[2]
    ax.plot(0.5 * (edges[1:] + edges[:-1]), hu / (N * 0.25), color=K.ACC2, lw=1.6, label="uniform start")
    ax.axhline(np.sqrt(eta) / np.pi, color=K.INK, lw=1.4, ls="--", label="steady rate $\\sqrt{\\eta}/\\pi$")
    ax.set_xlabel("time"); ax.set_ylabel("population rate"); ax.legend(fontsize=9)
    ax.set_title("identical neurons never relax (no dissipation)")
    fig.tight_layout()
    K.save(fig, "ch13_density", wide=True)


def gain():
    """The gain function from mean field: f(s) = C F(pi) = 1/T = sqrt(eta + s)/pi; Lorentzian average."""
    s = np.linspace(-1.5, 2.5, 400)
    single = np.where(s > 0, np.sqrt(np.clip(s, 0, None)) / np.pi, 0)
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.plot(s, single, color=K.INK, lw=2.2, label="identical neurons: $\\sqrt{s}/\\pi$")
    for d, col in [(0.1, K.BLUE), (0.4, K.ACC2), (1.0, K.ORANGE)]:
        ax.plot(s, np.sqrt(s + np.sqrt(s ** 2 + d ** 2)) / (np.pi * np.sqrt(2)), color=col, lw=2, label=f"Lorentzian spread $\\Delta = {d}$")
    # simulation check (Delta = 0.4) with XPPAUT
    ax.set_xlabel("mean input $\\eta_0 + s$"); ax.set_ylabel("population rate $f$")
    ax.set_title("gain functions derived from θ-neurons"); ax.legend(fontsize=9)
    K.save(fig, "ch13_gain")


MPR = """# Montbrio-Pazo-Roxin exact mean field for Lorentzian theta/QIF neurons
r'=delta/pi+2*r*v
v'=v^2+eta0+st*heav(t-t0)+j*r-(pi*r)^2
par delta=0.01,eta0=-0.3,st=1,t0=10,j=0
init r=0.1,v=-0.1
@ meth=cvode,tol=1e-10,atol=1e-10,dt=0.01,total=40,maxstor=100000
done
"""


def mpr():
    d12 = K.loaddata("ch12_transient")
    m = W.load_text(MPR)
    fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.2), gridspec_kw={"width_ratios": [1.15, 1.15, 1]})
    res = {}
    for col, delta in enumerate([0.01, 0.2]):
        r0 = np.sqrt(-0.3 + np.sqrt(0.09 + delta ** 2)) / (np.pi * np.sqrt(2))
        v0 = -delta / (2 * np.pi * r0)
        m.set(delta=delta, r=float(r0), v=float(v0))
        tr = m.run(total=40, dt=0.01)
        t, r, v = np.asarray(tr.t), np.asarray(tr["r"]), np.asarray(tr["v"])
        res[delta] = (t, r, v)
        ax = axs[col]
        ax.plot(d12["tc"], d12[f"r{col}"], color=K.ACC2, lw=1.4, alpha=0.8, label="300 θ-neurons (Ch. 12)")
        ax.plot(t, r, color=K.INK, lw=1.8, label="exact mean field (MPR)")
        ax.plot(d12["tm"], d12[f"rm{col}"], color=K.BLUE, lw=1.6, ls="--", label="first-order rate model")
        ax.set_xlabel("time"); ax.set_ylabel("population rate")
        ax.set_title(f"$\\Delta = {delta}$"); ax.set_xlim(5, 40)
        ax.legend(fontsize=8, loc="upper right")
    axs[0].set_ylim(0, 4.8); axs[1].set_ylim(0, 0.8)
    ax = axs[2]
    for delta, col in [(0.01, K.ACC2), (0.2, K.BLUE)]:
        t, r, v = res[delta]
        sel = t > 10
        ax.plot(v[sel], r[sel], color=col, lw=1.4, label=f"$\\Delta = {delta}$")
    ax.set_xlim(-3, 3); ax.set_ylim(0, 1.2)
    ax.set_xlabel("mean voltage $v$"); ax.set_ylabel("rate $r$"); ax.set_title("the same in the $(v, r)$ plane: spirals")
    ax.legend(fontsize=9)
    K.savedata("ch13_mpr", **{f"t{k}": res[d][0] for k, d in enumerate([0.01, 0.2])},
               **{f"r{k}": res[d][1] for k, d in enumerate([0.01, 0.2])}, **{f"v{k}": res[d][2] for k, d in enumerate([0.01, 0.2])})
    fig.tight_layout()
    K.save(fig, "ch13_mpr", wide=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["density", "gain", "mpr"]
    for w in which:
        globals()[w]()
