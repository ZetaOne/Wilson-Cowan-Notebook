"""Build the study kit: copy the .ode files and write + execute five Jupyter notebooks (pyauto-xpp).
Output: rendered-anims/wilson-cowan/study/{ode/*.ode, *.ipynb, *.py}
Run:  .venv/bin/python scripts/wilson-cowan/study/make_notebooks.py"""
import shutil
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "rendered-anims" / "wilson-cowan" / "study"
(OUT / "ode").mkdir(parents=True, exist_ok=True)
for f in (HERE / "ode").glob("*.ode"):
    shutil.copy(f, OUT / "ode" / f.name)

SETUP = """import numpy as np, matplotlib.pyplot as plt, pyxpp
plt.rcParams.update({"figure.figsize": (7, 4.2), "axes.spines.top": False, "axes.spines.right": False})
def load(name, **pars):
    m = pyxpp.load(text=open(f"ode/{name}.ode").read())
    if pars: m.set(**pars)
    return m"""

NB = {}

NB["01_one_population"] = [
    ("md", """# 1. One population: a flow on a line (Chapters 1–2)
Model: $\\dot a = -a + f(wa + I)$ with $f(x) = 1/(1+e^{-\\beta(x-\\theta)})$, $w = 10$, $\\beta = 1$, $\\theta = 5$.

**Picture first.** Steady states are where the S-curve $f(wa+I)$ meets the diagonal $a$. Above the diagonal $a$ grows, below it shrinks."""),
    ("code", SETUP),
    ("code", """w, beta, th = 10, 1, 5
f = lambda x: 1/(1+np.exp(-beta*(x-th)))
a = np.linspace(0, 1, 400)
for I, c in [(-3, 'C0'), (0, 'C1'), (3, 'C2')]:
    plt.plot(a, f(w*a+I), c, label=f'$f(wa+I)$, I={I}')
plt.plot(a, a, 'k--', label='diagonal $a$'); plt.xlabel('a'); plt.legend(); plt.title('crossings = steady states');"""),
    ("md", """**The S-curve exactly.** Solve $a = f(wa+I)$ for $I$: $I = \\theta - \\ln(1/a - 1)/\\beta - wa$. Stable where $w\\beta a(1-a) < 1$."""),
    ("code", """aa = np.linspace(1e-4, 1-1e-4, 3000)
I = th - np.log(1/aa - 1)/beta - w*aa
st = w*beta*aa*(1-aa) < 1
plt.plot(np.where(st, I, np.nan), aa, 'k', lw=2.5, label='stable')
plt.plot(np.where(~st, I, np.nan), aa, 'k--', label='unstable')
plt.xlabel('input I'); plt.ylabel('steady a'); plt.xlim(-4, 4); plt.legend(); plt.title('S-curve: folds at I = ±1.80');"""),
    ("md", "**Hysteresis with XPPAUT.** Ramp $I$ slowly up and down by restarting from the last state at each step."),
    ("code", """m = load('one_population')
up, dn = [], []
Is = np.linspace(-4, 4, 81)
m.set(i=-4, a=0.0); m.run(total=50)
for I in Is:
    m.set(i=float(I)); m.run_last(total=30); up.append(m.last_point()['A'])
for I in Is[::-1]:
    m.set(i=float(I)); m.run_last(total=30); dn.append(m.last_point()['A'])
plt.plot(Is, up, 'C3o-', ms=3, label='ramp up'); plt.plot(Is[::-1], dn, 'C0o-', ms=3, label='ramp down')
plt.xlabel('I'); plt.ylabel('a'); plt.legend(); plt.title('a memory of past input');"""),
    ("md", "**AUTO** finds the folds directly (continuation of steady states in $I$)."),
    ("code", """m = load('one_population'); m.set(i=-4, a=0.0); m.run(total=50); m.run_last(total=20)
br = m.auto.run('i', start='steady', ds=0.02, dsmax=0.05, parmin=-4, parmax=4, nmax=2000)
# in one dimension AUTO may label a fold 'BP' instead of 'LP'
pts = sorted({round(p.x, 1) for p in br.special('LP') + br.special('BP') if abs(p.x) < 3.9})
print('folds at I =', pts)"""),
    ("md", "**Try:** change `w` to 3 (below the cusp $w = 4/\\beta$) and rerun. What happens to the S-curve and the hysteresis?"),
]

NB["02_wc_phase_plane"] = [
    ("md", """# 2. The Wilson–Cowan pair: phase plane, oscillations, Hopf (Chapters 5–7)
$\\dot E = -E + (k_E - E)\\mathcal S_E(c_1E - c_2I + P)$, $\\dot I = -I + (k_I - I)\\mathcal S_I(c_3E - c_4I + Q)$.

**Picture first:** draw both nullclines; their crossings are the steady states; the $E$-nullcline has a hump because of self-excitation."""),
    ("code", SETUP),
    ("code", """def S(x, a, th): return 1/(1+np.exp(-a*(x-th))) - 1/(1+np.exp(a*th))
def Sinv(y, a, th): return th - np.log(1/(y + 1/(1+np.exp(a*th))) - 1)/a
def nullclines(p, e):
    ke = 1 - 1/(1+np.exp(p['ae']*p['the'])); ki = 1 - 1/(1+np.exp(p['ai']*p['thi']))
    IE = (p['c1']*e + p['p'] - Sinv(e/(ke - e), p['ae'], p['the']))/p['c2']
    II = []
    for x in e:
        lo, hi = -0.1, ki - 1e-9
        g = lambda I: (ki - I)*S(p['c3']*x - p['c4']*I + p['q'], p['ai'], p['thi']) - I
        for _ in range(60):
            mid = (lo+hi)/2
            lo, hi = (lo, mid) if g(lo)*g(mid) <= 0 else (mid, hi)
        II.append((lo+hi)/2)
    return IE, np.array(II)
OSC = dict(c1=16, c2=12, c3=15, c4=3, ae=1.3, the=4, ai=2, thi=3.7, p=1.25, q=0)
HYS = dict(c1=12, c2=4, c3=13, c4=11, ae=1.2, the=2.8, ai=1, thi=4, p=0, q=0)"""),
    ("code", """fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
e = np.linspace(0.001, 0.47, 600)
for ax, (name, p, starts) in zip(axs, [('wc_hysteresis', HYS, [(0.08, .02), (0.12, .02), (0.45, .05)]),
                                       ('wc_oscillator', OSC, [(0.2, 0.11), (0.45, 0.45)])]):
    IE, II = nullclines(p, e)
    ax.plot(e, IE, 'g', lw=2, label='$\\\\dot E=0$'); ax.plot(e, II, 'r', lw=2, label='$\\\\dot I=0$')
    m = load(name)
    for x0 in starts:
        m.set(e=x0[0], i=x0[1]); tr = m.run(total=60)
        ax.plot(tr['e'], tr['i'], lw=1.3)
    ax.set_xlim(0, .5); ax.set_ylim(0, .5); ax.set_xlabel('E'); ax.set_ylabel('I'); ax.set_title(name); ax.legend()"""),
    ("md", "Left: three crossings (rest, saddle, active). Right: one crossing on the rising branch of the hump, so trajectories spiral out onto a limit cycle."),
    ("code", """m = load('wc_oscillator'); m.set(p=3.0, e=0.3, i=0.2); m.run(total=200); m.run_last(total=20)
eq = m.auto.run('p', start='steady', ds=-0.02, dsmax=0.05, parmin=1.15, parmax=4.0, nmax=300)
hb = eq.special('HB'); print('Hopf at P =', [round(h.x, 4) for h in hb])
po = m.auto.run(grab=hb[0].label, choice='periodic', ntst=80, dsmax=0.03, nmax=800, parmin=0.9, parmax=4.0)
d = po.to_pandas('e'); d = d[d.period < 1e3]
plt.plot(d.par, 1/d.period, 'C3'); plt.xlabel('P'); plt.ylabel('frequency 1/T'); plt.title('frequency rises with input');"""),
    ("md", "**Try:** in the hysteresis model, ramp `p` from −0.8 to 0.8 and back (as in notebook 1) and find the two folds."),
]

NB["03_neural_fields"] = [
    ("md", """# 3. Neural fields: bumps and fronts (Chapter 8)
Amari's equation $\\partial_t u = -u + \\int w(x-y)f(u(y))\\,dy + I$ on a ring of 240 points, using XPP's `conv` special.

**Picture first:** a bump of width $a$ survives if the input at its edge, $W(a) = \\int_0^a w$, equals the threshold."""),
    ("code", SETUP),
    ("code", """from scipy.integrate import quad
w = lambda x: 1.5*np.exp(-x**2) - 0.6*np.exp(-(x/3)**2)
d = np.linspace(0.01, 6, 300); W = [quad(w, 0, x)[0] for x in d]
plt.plot(d, W, 'k'); plt.axhline(0.3, color='C1', ls='--'); plt.xlabel('width a'); plt.ylabel('W(a)'); plt.title('bump widths: W(a) = θ');"""),
    ("code", """m = load('amari_bump')
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
for ax, s in zip(axs, [0.12, 1.0]):
    m.set(s=s); tr = m.run(total=40)
    U = np.array([tr[f'u{j}'] for j in range(240)])
    ax.imshow(U, aspect='auto', origin='lower', extent=[0, 40, -15, 15], cmap='magma'); ax.set_title(f'stimulus strength {s}')
    ax.set_xlabel('time'); ax.set_ylabel('x')"""),
    ("md", "Weak stimulus: the field returns to rest. Strong: a bump persists after the stimulus stops at $t = 5$ (a memory of position).\n\n**Try:** raise `th` towards the maximum of $W$; when does the bump stop existing?"),
]

NB["04_spiking_mean_field"] = [
    ("md", """# 4. Spiking neurons and their exact mean field (Chapters 12–13)
200 θ-neurons with Lorentzian excitabilities, against the Montbrió–Pazó–Roxin equations $\\dot r = \\Delta/\\pi + 2rv$, $\\dot v = v^2 + \\eta_0 + I - \\pi^2r^2$.

**Picture first:** each neuron is a point running round a circle; the population is a density on the circle, crowded where the neurons are slow."""),
    ("code", SETUP),
    ("code", """m = load('theta_network'); tr = m.run(total=100, dt=0.02)
t = np.asarray(tr.t); th = np.column_stack([tr[f'th{k}'] for k in range(1, 201)])
k = np.floor((th + np.pi)/(2*np.pi)); idx = np.argwhere(np.diff(k, axis=0) > 0)
sp = np.array([(t[i+1], j) for i, j in idx])
fig, axs = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
axs[0].plot(sp[:, 0], sp[:, 1], '|', ms=2, color='k'); axs[0].set_ylabel('neuron')
h, e = np.histogram(sp[:, 0], np.arange(0, 101, 1.0)); axs[1].plot(e[:-1]+0.5, h/200, 'C3')
axs[1].set_ylabel('rate'); axs[1].set_xlabel('time'); axs[0].set_title('raster and coarse-grained rate (input on 30–70)');"""),
    ("code", """mf = load('mpr_mean_field')
for delta, c in [(0.01, 'C3'), (0.2, 'C0')]:
    r0 = np.sqrt(-0.3 + np.sqrt(0.09 + delta**2))/(np.pi*np.sqrt(2)); v0 = -delta/(2*np.pi*r0)
    mf.set(delta=delta, r=float(r0), v=float(v0)); tr = mf.run(total=40)
    plt.plot(tr.t, tr['r'], c, label=f'Δ = {delta}')
plt.ylim(0, 4); plt.xlabel('time'); plt.ylabel('rate r'); plt.legend(); plt.title('MPR: volleys for similar neurons, smooth for diverse ones');"""),
    ("md", "**Try:** set `j=5` (recurrent excitation) in the MPR model and look for bistability between low and high rate."),
]

NB["05_finite_size"] = [
    ("md", """# 5. Finite size: fluctuations and switching (Chapters 14–15)
$N$ two-state neurons: off→on at rate $f(wa+I)$, on→off at rate 1. Mean field: $\\dot a = -a + (1-a)f(wa+I)$.

**Picture first:** a finite population is a cloud around the mean field state; with two wells, noise carries it over the ridge."""),
    ("code", SETUP),
    ("code", """def gillespie(N, w, b, th, T, a0, seed=0):
    rng = np.random.default_rng(seed); n = int(a0*N); t = 0; ts, ns = [0], [n]
    f = lambda x: 1/(1+np.exp(-b*(x-th)))
    while t < T:
        up = (N-n)*f(w*n/N); dn = n; tot = up + dn
        t += rng.exponential(1/tot); n += 1 if rng.random()*tot < up else -1
        ts.append(t); ns.append(n)
    return np.array(ts), np.array(ns)/N
for N, c in [(25, 'C1'), (200, 'C0'), (800, 'C3')]:
    t, a = gillespie(N, 4, 2, 1.5, 60, 0.08, seed=N); plt.step(t, a, c, lw=0.8, label=f'N = {N}')
plt.xlabel('time'); plt.ylabel('a'); plt.legend(); plt.title('fluctuations shrink like 1/sqrt(N)');"""),
    ("code", """m = load('langevin_population')
for N, c in [(40, 'C1'), (80, 'C3')]:
    m.set(nn=N, a=0.025); tr = m.run(total=400)
    plt.plot(tr.t, tr['a'], c, lw=0.6, label=f'N = {N}')
plt.xlabel('time'); plt.ylabel('a'); plt.legend(); plt.title('noise-driven switching (XPPAUT Langevin)');"""),
    ("md", "**Try:** double `nn` and measure how much longer the population waits before switching. Theory: about $e^{N\\Delta\\Phi}$ with $\\Delta\\Phi \\approx 0.059$."),
]

for name, cells in NB.items():
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src) for kind, src in cells]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    client = NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(OUT)}})
    client.execute()
    nbf.write(nb, OUT / f"{name}.ipynb")
    # plain script version
    code = "\n\n".join(src if kind == "code" else "# " + src.replace("\n", "\n# ") for kind, src in cells)
    (OUT / f"{name}.py").write_text(code + "\n")
    print("wrote", name)
