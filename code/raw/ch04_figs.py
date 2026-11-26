"""Chapter 4 figures: deriving the Wilson–Cowan equations; the WC and STM forms.
Run:  .venv/bin/python scripts/wilson-cowan/figs/ch04_figs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import wc_lib as W
import figkit as K


def circuit():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    E = (2.4, 2.0); I = (6.2, 2.0)
    for (cx, cy), col, lab in [(E, K.ACC2, "$E$"), (I, K.BLUE, "$I$")]:
        ax.add_patch(Circle((cx, cy), 0.75, fc=col, ec="none", alpha=0.18))
        ax.add_patch(Circle((cx, cy), 0.75, fc="none", ec=col, lw=2.5))
        ax.text(cx, cy, lab, ha="center", va="center", fontsize=22, color=col)
    def arrow(p, q, col, rad, label, lpos, inhib=False):
        a = FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}", arrowstyle="-[" if inhib else "-|>",
                            mutation_scale=18, lw=2.2, color=col)
        ax.add_patch(a); ax.text(*lpos, label, fontsize=15, color=col, ha="center", va="center")
    arrow((3.1, 2.45), (5.45, 2.45), K.ACC2, -0.25, "$c_3$", (4.3, 3.25))
    arrow((5.45, 1.55), (3.1, 1.55), K.BLUE, -0.25, "$c_2$", (4.3, 0.72), inhib=True)
    arrow((1.75, 2.55), (1.95, 2.72), K.ACC2, -2.4, "$c_1$", (1.0, 3.35))
    arrow((6.85, 2.55), (6.65, 2.72), K.BLUE, 2.4, "$c_4$", (7.45, 3.35), inhib=True)
    ax.annotate("", xy=(1.65, 1.6), xytext=(0.3, 1.0), arrowprops=dict(arrowstyle="-|>", color=K.ORANGE, lw=2))
    ax.text(0.25, 0.7, "$P$", fontsize=15, color=K.ORANGE)
    ax.annotate("", xy=(6.95, 1.6), xytext=(8.3, 1.0), arrowprops=dict(arrowstyle="-|>", color=K.ORANGE, lw=2))
    ax.text(8.25, 0.7, "$Q$", fontsize=15, color=K.ORANGE)
    ax.set_xlim(0, 8.7); ax.set_ylim(0.2, 3.9); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("excitatory ($E$) and inhibitory ($I$) populations: arrows excite, bars inhibit")
    K.save(fig, "ch04_circuit")


def equivalence():
    """WC form (activities) and STM form (inputs) with r = 0: if s_E = c1 E - c2 I + P and s_I = c3 E - c4 I + Q
    at t = 0 and the inputs are constant, the two systems trace the same orbit."""
    base = "S(x,a,th)=1/(1+exp(-a*(x-th)))-1/(1+exp(a*th))\npar c1=16,c2=12,c3=15,c4=3,ae=1.3,the=4,ai=2,thi=3.7,p=1.25,q=0\n"
    wc = W.load_text(base + """e'=-e+S(c1*e-c2*i+p,ae,the)
i'=-i+S(c3*e-c4*i+q,ai,thi)
init e=0.1,i=0.05
@ meth=cvode,tol=1e-10,atol=1e-10,dt=0.01,total=40
done""")
    st = W.load_text(base + """ue'=-ue+c1*S(ue,ae,the)-c2*S(ui,ai,thi)+p
ui'=-ui+c3*S(ue,ae,the)-c4*S(ui,ai,thi)+q
init ue=0,ui=0
@ meth=cvode,tol=1e-10,atol=1e-10,dt=0.01,total=40
done""")
    e0, i0 = 0.1, 0.05
    st.set(ue=16 * e0 - 12 * i0 + 1.25, ui=15 * e0 - 3 * i0)
    a = wc.run(total=40, dt=0.01); b = st.run(total=40, dt=0.01)
    t = np.asarray(a.t)
    sE_from_wc = 16 * np.asarray(a["e"]) - 12 * np.asarray(a["i"]) + 1.25
    # a second STM run started from the "wrong" place: the two forms agree only on the invariant set s = W a + P
    st.set(ue=0.0, ui=0.0)
    c = st.run(total=40, dt=0.01)
    K.savedata("ch04_equiv", t=t, sE_wc=sE_from_wc, uE=np.asarray(b["ue"]), uE2=np.asarray(c["ue"]))
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.6, 1]})
    axs[0].plot(t, sE_from_wc, color=K.ACC2, lw=3.2, label="WC form: $c_1E - c_2I + P$")
    axs[0].plot(b.t, b["ue"], "--", color=K.INK, lw=1.6, label="STM form: $s_E(t)$")
    axs[0].set_xlabel("time"); axs[0].set_ylabel("input to $E$"); axs[0].legend(fontsize=9, loc="lower right")
    axs[0].set_title("same start, same orbit")
    err = np.abs(sE_from_wc - np.asarray(b["ue"]))
    axs[1].semilogy(t, err + 1e-9, color=K.ACC, lw=1.2)
    axs[1].set_ylim(1e-9, 1); axs[1].set_xlabel("time"); axs[1].set_ylabel("absolute difference")
    axs[1].set_title("agreement to stored precision ($10^{-5}$)")
    fig.tight_layout()
    K.save(fig, "ch04_equiv", wide=True)
    print("max diff consistent:", err.max())


if __name__ == "__main__":
    circuit()
    equivalence()
