Every number and figure in this book was computed by code that you can read and run. Each figure caption has a **code ↗** link that opens the script that made it, as a syntax-highlighted page in your browser with a download link. The full list is in the [code index](code/index.html). The study kit (on the landing page) contains ready-to-run `.ode` files and notebooks.

## The tools

- **pyauto-xpp** ([zetaone.github.io/pyauto-xpp](https://zetaone.github.io/pyauto-xpp/)): XPPAUT 8.4, Bard Ermentrout's dynamical-systems program, with its AUTO, as a Python library. Every trajectory, steady state, network simulation, neural field, Langevin simulation, adjoint and bifurcation diagram here is computed by XPPAUT's own C code. Typical calls:
  ```python
  import pyxpp
  m = pyxpp.load(text=ode_text)          # an XPP model from its .ode text
  m.set(p=1.25)                          # change parameters or initial conditions
  tr = m.run(total=100)                  # Initialconds > Go: a Trajectory
  eq = m.equilibrium({"e": 0.2, "i": 0.1})            # Newton for a steady state
  br = m.auto.run("p", start="steady", ds=-0.02)      # AUTO from an equilibrium
  po = m.auto.run(grab=br.special("HB")[0].label, choice="periodic")
  ```
- **XPP features used for large systems**: arrays (`u[0..N-1]'=...`), the `conv` special for spatial convolutions (Chapters 8–9), `mmult` with a weight table read from a file (Hopfield network, Chapter 11), `sum(0,N-1)of(shift(...))` for all-to-all coupling (θ-neuron networks), and `wiener` variables for Langevin equations (Chapter 14). XPP limits the number of parameters to a few hundred, so networks use at most 300 neurons with individual parameters.
- **NumPy** for three things XPP cannot do directly: two-dimensional neural fields (FFT convolution, Chapter 9), exact Gillespie simulations of the stochastic population (Chapters 14–15), and numerical integrals (Chapters 8, 15).
- **matplotlib** for the figures; **ManimGX** and Manim Slides for the chapter decks.
- **Themes**: the switcher at the bottom right of the HTML book offers the book's own style (Classic, the default) and 17 open-source (MIT) stylesheets from GitHub projects: Tufte CSS, LaTeX.css, Pico, Water.css, Simple.css, Sakura, new.css, MVP.css, awsm.css, github-markdown-css, Bamboo and Marx.

## The numerics library: `wc_lib.py`

[`wc_lib.py`](code/wc_lib.html) holds everything shared:

| function | what it does | chapters |
|---|---|---|
| `MODELS`, `load(name)` | models as XPP `.ode` text: one population (`pop1`, `pop1x`), the Wilson–Cowan pair (`wc`), its STM form (`stm`) | all |
| `WC_OSC`, `WC_HYST`, `WC_FIG6`, `WC_FIG7`, `WC_FIG10` | Wilson and Cowan's 1972 parameter sets | 5–7 |
| `wc_rhs`, `wc_nullclines` | the vector field; both nullclines exactly (the $E$-nullcline through the inverse sigmoid) | 5–7 |
| `wc_fixed_points`, `wc_steady_states_fast` | all steady states with stability | 5–7 |
| `wc_branch_in_P`, `wc_emax` | the exact steady-state curve against $P$, parametrised by $E$; folds and Hopf points from it | 6, 7 |
| `theta_network` | XPP text for $N$ θ-neurons with Lorentzian excitabilities and shared synapses | 1, 3, 12 |
| `traj`, `periodic_orbit`, `floquet`, `phase_map` | trajectories, cycles, adjoint PRCs and isochrons (shared with the isochron book) | 6 |

## Checks

Results were checked against independent calculations wherever possible:

- the steady-state network rate of 150 θ-neurons against the analytic gain (0.1703 measured, 0.1700 predicted; Chapter 3);
- the cusp of the one-population model against the analytic $4/\beta$ (Chapter 2);
- the Hopf point and period from the exact steady-state curve ($P = 1.878$, $T = 2.36$) against AUTO ($P = 1.879$, $T = 2.358$; Chapter 6);
- neural-field front speeds against $c = (1-2\theta)/2\theta$ to three digits, and the bump width against Amari's condition (1.88 vs 1.94, within half a grid cell; Chapter 8);
- the exact MPR mean field against a 300-neuron network (Chapter 13);
- the variance of the stochastic population against the linear noise approximation, switching times against the quasi-potential barrier, and the mean shift against the one-loop correction (Chapters 14–15).

## Reproducing everything

```sh
for f in scripts/wilson-cowan/figs/ch*_figs.py; do .venv/bin/python "$f"; done
.venv/bin/python scripts/wilson-cowan/book/build_code.py
node scripts/wilson-cowan/book/build.mjs --pdf
.venv/bin/python scripts/wilson-cowan/book/themes.py        # adds the theme switcher
bash scripts/wilson-cowan/decks/render_all.sh
.venv/bin/python scripts/wilson-cowan/study/make_notebooks.py
.venv/bin/python scripts/wilson-cowan/site/build.py
```
