"""Shared numerics for the Wilson–Cowan book.

Every simulation is run by XPPAUT 8.4 through pyauto-xpp (`import pyxpp`): integration,
equilibria, nullclines, periodic orbits, adjoints and AUTO bifurcation diagrams.
Large spatial (2-D) pattern simulations use numpy where an XPP array would be impractical;
those places say so.

Models (MODELS, as XPP .ode text):
  pop1    one population:          tau a' = -a + f(w a + I),  f logistic
  wc      Wilson–Cowan (1972) E–I:  E' = (-E + (kE - rE E) SE(c1 E - c2 I + P)) / tauE
                                     I' = (-I + (kI - rI I) SI(c3 E - c4 I + Q)) / tauI
          with Wilson & Cowan's shifted logistic S(x) = 1/(1+exp(-a(x-th))) - 1/(1+exp(a th))
  stm     the same E–I network in "STM"/voltage form (s = W a + I as the variable)
  pop1x   one purely excitatory population with refractoriness (Beurle's situation)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "isochron"))
import iso_lib as IL  # noqa: E402  (periodic_orbit, floquet, phase maps ... shared with the isochron book)
import pyxpp  # noqa: E402

NUM = "@ meth=cvode,tol=1e-9,atol=1e-9,dt=0.02,total=100,maxstor=500000,bound=100000\n"

LOGISTIC = "S(x,a,th)=1/(1+exp(-a*(x-th)))-1/(1+exp(a*th))\n"

MODELS = {
    "pop1": """# one population: tau a' = -a + f(w a + I)
f(x)=1/(1+exp(-beta*(x-th)))
a'=(-a+f(w*a+i))/tau
par w=10,i=0,beta=1,th=5,tau=1
init a=0.05
""",
    "pop1x": """# purely excitatory population with refractory factor (Beurle's case)
f(x)=1/(1+exp(-beta*(x-th)))
a'=(-a+(1-r*a)*f(w*a+i))/tau
par w=12,i=0,beta=1,th=4,tau=1,r=1
init a=0.05
""",
    "wc": """# Wilson-Cowan (1972) excitatory-inhibitory pair
""" + LOGISTIC + """ke=1-1/(1+exp(ae*the))
ki=1-1/(1+exp(ai*thi))
e'=(-e+(ke-re*e)*S(c1*e-c2*i+p,ae,the))/taue
i'=(-i+(ki-ri*i)*S(c3*e-c4*i+q,ai,thi))/taui
par c1=16,c2=12,c3=15,c4=3,ae=1.3,the=4,ai=2,thi=3.7,re=1,ri=1,p=1.25,q=0,taue=1,taui=1
init e=0.1,i=0.05
""",
    "stm": """# the same E-I network written for the inputs (STM / 'voltage' form)
""" + LOGISTIC + """fe(x)=(1-1/(1+exp(ae*the)))*0+S(x,ae,the)
fi(x)=S(x,ai,thi)
ue'=-ue+c1*fe(ue)-c2*fi(ui)+p
ui'=-ui+c3*fe(ue)-c4*fi(ui)+q
par c1=16,c2=12,c3=15,c4=3,ae=1.3,the=4,ai=2,thi=3.7,p=1.25,q=0
init ue=0.5,ui=0.2
""",
}

# Wilson & Cowan (1972) parameter sets
WC_OSC = dict(c1=16, c2=12, c3=15, c4=3, ae=1.3, the=4, ai=2, thi=3.7, re=1, ri=1, p=1.25, q=0)       # limit cycle (their Fig. 8-ish)
WC_HYST = dict(c1=12, c2=4, c3=13, c4=11, ae=1.2, the=2.8, ai=1, thi=4, re=1, ri=1, p=0, q=0)        # multiple steady states, hysteresis


def load(name, extra="", **pars):
    m = pyxpp.load(text=MODELS[name] + NUM + extra + "done\n")
    if pars:
        m.set(**pars)
    return m


def load_text(text, **pars):
    m = pyxpp.load(text=text if text.rstrip().endswith("done") else text + "\n" + NUM + "done\n")
    if pars:
        m.set(**pars)
    return m


traj = IL.traj
periodic_orbit = IL.periodic_orbit
floquet = IL.floquet
isochron_curves = IL.isochron_curves


def S(x, a, th):
    return 1 / (1 + np.exp(-a * (x - th))) - 1 / (1 + np.exp(a * th))


def wc_rhs(p=None):
    q = dict(WC_OSC, taue=1, taui=1); q.update(p or {})
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"])); ki = 1 - 1 / (1 + np.exp(q["ai"] * q["thi"]))

    def F(u):
        e, i = u[0], u[1]
        return np.array([(-e + (ke - q["re"] * e) * S(q["c1"] * e - q["c2"] * i + q["p"], q["ae"], q["the"])) / q["taue"],
                         (-i + (ki - q["ri"] * i) * S(q["c3"] * e - q["c4"] * i + q["q"], q["ai"], q["thi"])) / q["taui"]])
    return F, ke, ki


def wc_nullclines(p, egrid):
    """Analytic nullclines of the WC pair: the E-nullcline as I(E) and the I-nullcline as I(E).
    E' = 0:  c1 E - c2 I + P = S_E^{-1}(E / (kE - rE E))   ->  I = (c1 E + P - Sinv_E(...)) / c2
    I' = 0:  I = (kI - rI I) S_I(c3 E - c4 I + Q)  (solved for I by bisection for each E)"""
    q = dict(WC_OSC); q.update(p)
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"])); ki = 1 - 1 / (1 + np.exp(q["ai"] * q["thi"]))
    def Sinv(y, a, th):
        z = y + 1 / (1 + np.exp(a * th))
        with np.errstate(divide="ignore", invalid="ignore"):
            return th - np.log(1 / z - 1) / a
    y = egrid / (ke - q["re"] * egrid)
    Inull_E = (q["c1"] * egrid + q["p"] - Sinv(y, q["ae"], q["the"])) / q["c2"]
    Inull_I = []
    for e in egrid:
        lo, hi = -0.1, ki / (1 + q["ri"] * 0) - 1e-12
        g = lambda I: (ki - q["ri"] * I) * S(q["c3"] * e - q["c4"] * I + q["q"], q["ai"], q["thi"]) - I
        if g(lo) * g(hi) > 0:
            Inull_I.append(np.nan); continue
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if g(lo) * g(mid) <= 0:
                hi = mid
            else:
                lo = mid
        Inull_I.append(0.5 * (lo + hi))
    return Inull_E, np.array(Inull_I)

# more of Wilson & Cowan's (1972) parameter sets, by their figure number
WC_FIG6 = dict(c1=13, c2=4, c3=20, c4=2, ae=1.2, the=2.7, ai=5, thi=3.7, re=1, ri=1, p=0, q=0)    # two separate hysteresis loops
WC_FIG7 = dict(c1=13, c2=4, c3=22, c4=2, ae=1.5, the=2.5, ai=6, thi=4.3, re=1, ri=1, p=0, q=0)    # overlapping loops, 3 stable states
WC_FIG10 = dict(c1=15, c2=15, c3=15, c4=3, ae=1, the=2, ai=2, thi=2.5, re=1, ri=1, p=0, q=0)      # damped oscillation (evoked potential)


def traj1(m, x0, total, dt=0.01, **pars):
    """One trajectory of a one-variable model; returns (t, x)."""
    v = m.vars[0].lower()
    m.set(**{v: float(x0)}, total=total, dt=dt, trans=0, nout=1, **pars)
    tr = m.run()
    return np.asarray(tr.t, float), np.asarray(tr[v], float)


def theta_network(N=200, J=0.0, tau=2.0, eta0=0.2, delta=0.05, n=2, seed=1, stim=None, shuffle=True):
    """XPP text: N theta-neurons (quadratic integrate-and-fire in phase form) with heterogeneous
    excitabilities eta_i (Lorentzian, centre eta0, half-width delta) and one shared synaptic drive s:
        th_i' = 1 - cos th_i + (1 + cos th_i) (eta_i + I(t) + J s)
        tau s' = -s + (1/N) sum_j P(th_j),   P(th) = a_n (1 - cos th)^n  (a smooth pulse at th = pi, area 2pi*... normalised)
    A neuron 'spikes' when th passes pi (mod 2 pi).  I(t) = stim(t) given as an XPP expression in t."""
    rng = np.random.default_rng(seed)
    u = (np.arange(N) + 0.5) / N
    etas = eta0 + delta * np.tan(np.pi * (u - 0.5))            # deterministic Lorentzian quantiles
    etas = np.clip(etas, eta0 - 20 * delta, eta0 + 20 * delta)
    if shuffle:
        etas = rng.permutation(etas)
    th0 = rng.uniform(-np.pi, np.pi, N)
    # a_n so that the pulse integrates to 1 over one cycle in time at unit speed in theta: int P dth / (2 pi) = 1
    from math import comb
    an = 2 ** n / comb(2 * n, n)             # 1 / mean over a cycle of (1 - cos th)^n
    lines = [f"# {N} theta-neurons with shared synaptic drive", f"par J={J},tau={tau},n={n},an={an:.10g}"]
    stim_expr = stim or "0"
    lines.append(f"stim(t)={stim_expr}")
    lines += [f"par eta{k+1}={etas[k]:.8g}" for k in range(N)]
    lines.append(f"th[1..{N}]'=1-cos(th[j])+(1+cos(th[j]))*(eta[j]+stim(t)+J*s)")
    lines.append(f"s'=(-s+an*sum(0,{N - 1})of((1-cos(shift(th1,i')))^n)/{N})/tau")
    lines += [f"init th{k+1}={th0[k]:.6f}" for k in range(N)]
    lines.append("init s=0")
    lines.append("@ meth=cvode,tol=1e-8,atol=1e-8,dt=0.01,total=100,maxstor=200000,bound=1e8")
    lines.append("done")
    return "\n".join(lines), etas


def wc_fixed_points(pars, m=None):
    """All steady states of the WC pair: nullcline crossings (plus the origin when P = Q = 0), refined by XPP's
    Newton. Returns a list of (E, I, stable, eigenvalues)."""
    q = dict(WC_OSC); q.update(pars)
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"]))
    eg = np.linspace(0.0005, ke - 1e-6, 3000)
    ie, ii = wc_nullclines(q, eg)
    own = m is None
    m = m or load("wc", **q)
    out = []
    guesses = [(0.0, 0.0)] + [(eg[k], ii[k]) for k in np.where(np.diff(np.sign(ie - ii)) != 0)[0]]
    for g in guesses:
        try:
            e = m.equilibrium({"e": float(g[0]), "i": float(g[1])})
        except Exception:
            continue
        p = (e.x["E"], e.x["I"])
        if abs(p[0] - g[0]) > 0.05 or any(abs(p[0] - o[0]) < 1e-5 and abs(p[1] - o[1]) < 1e-5 for o in out):
            continue
        out.append((p[0], p[1], e.stable, e.eigenvalues))
    if own:
        m.close()
    return out


def wc_steady_states_fast(pars, n=4000):
    """Steady states of the WC pair without XPP (vectorised): crossings of the E-nullcline I_E(E) with the
    I-nullcline I_I(E), refined by bisection on E; stability from the Jacobian (finite differences).
    Returns list of (E, I, trace, det, stable)."""
    q = dict(WC_OSC); q.update(pars)
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"])); ki = 1 - 1 / (1 + np.exp(q["ai"] * q["thi"]))

    def Sinv(y, a, th):
        z = y + 1 / (1 + np.exp(a * th))
        with np.errstate(divide="ignore", invalid="ignore"):
            return th - np.log(1 / z - 1) / a

    def IE(e):
        return (q["c1"] * e + q["p"] - Sinv(e / (ke - q["re"] * e), q["ae"], q["the"])) / q["c2"]

    def II(e):
        e = np.atleast_1d(e).astype(float)
        lo = np.full_like(e, -0.2); hi = np.full_like(e, ki - 1e-9)
        g = lambda I: (ki - q["ri"] * I) * S(q["c3"] * e - q["c4"] * I + q["q"], q["ai"], q["thi"]) - I
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            left = g(lo) * g(mid) <= 0
            hi = np.where(left, mid, hi); lo = np.where(left, lo, mid)
        return 0.5 * (lo + hi)

    eg = np.linspace(-0.1, ke - 1e-6, n)
    with np.errstate(all="ignore"):
        d = IE(eg) - II(eg)
    out = []
    F, _, _ = wc_rhs(q)
    for k in np.where((np.diff(np.sign(d)) != 0) & np.isfinite(d[:-1]) & np.isfinite(d[1:]))[0]:
        a, b = eg[k], eg[k + 1]
        for _ in range(50):
            mid = 0.5 * (a + b)
            with np.errstate(all="ignore"):
                if np.sign(IE(a) - II(a)[0]) * np.sign(IE(mid) - II(mid)[0]) <= 0:
                    b = mid
                else:
                    a = mid
        e = 0.5 * (a + b); i = float(II(e)[0])
        if abs(IE(e) - i) > 1e-3:
            continue
        h = 1e-6
        J = np.column_stack([(F(np.array([e + h, i])) - F(np.array([e - h, i]))) / (2 * h),
                             (F(np.array([e, i + h])) - F(np.array([e, i - h]))) / (2 * h)])
        tr, det = np.trace(J), np.linalg.det(J)
        out.append((e, i, tr, det, bool(tr < 0 and det > 0)))
    return out


def wc_branch_in_P(pars, egrid):
    """Exact steady-state curve against the input P, parametrised by E: on the I-nullcline I = I_I(E), and
    the E equation solved for P.  Returns P(E), I(E), trace, det of the Jacobian (arrays)."""
    q = dict(WC_OSC); q.update(pars)
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"]))
    q0 = dict(q); q0["p"] = 0.0
    ie0, ii = wc_nullclines(q0, egrid)          # E-nullcline at P = 0:  I = (c1 E - Sinv(.))/c2
    P = q["c2"] * (ii - ie0)                    # shift needed so that the E-nullcline passes through (E, I_I(E))
    tr = np.empty_like(egrid); det = np.empty_like(egrid)
    for k, (e, i, p) in enumerate(zip(egrid, ii, P)):
        qq = dict(q); qq["p"] = p
        F, _, _ = wc_rhs(qq); h = 1e-6
        J = np.column_stack([(F(np.array([e + h, i])) - F(np.array([e - h, i]))) / (2 * h),
                             (F(np.array([e, i + h])) - F(np.array([e, i - h]))) / (2 * h)])
        tr[k], det[k] = np.trace(J), np.linalg.det(J)
    return P, ii, tr, det


def wc_emax(pars):
    """Largest E for which the E-nullcline exists: E/(k_E - r E) must stay below k_E = max S_E."""
    q = dict(WC_OSC); q.update(pars)
    ke = 1 - 1 / (1 + np.exp(q["ae"] * q["the"]))
    return ke * ke / (1 + q["re"] * ke)
