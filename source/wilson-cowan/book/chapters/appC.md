## Notation

| symbol | meaning | first used |
|---|---|---|
| $a_i$, $a(t)$ | activity of population $i$ (fraction active, or rate) | 1 |
| $s_i$ | input (synaptic drive) to population $i$ | 1, 4 |
| $f$, $\mathcal S$ | gain (activation) function; Wilson–Cowan's shifted logistic $\mathcal S(x) = 1/(1+e^{-a(x-\theta)}) - 1/(1+e^{a\theta})$ | 1, 3 |
| $\beta$ or $a$, $\theta$ | steepness and threshold of a sigmoid | 2, 3 |
| $w_{ij}$, $W$ | connection weight from population $j$ to $i$ | 1 |
| $r$, $k$ | refractory period; maximum of the sigmoid ($k = \max\mathcal S$) | 3, 4 |
| $E$, $I$ | excitatory and inhibitory activities | 4 |
| $c_1, c_2, c_3, c_4$ | E→E, I→E, E→I, I→I connection strengths | 4 |
| $P$, $Q$ | external inputs to $E$ and $I$ | 4 |
| $\tau$, $\tau_E$, $\tau_I$ | time constants | 1, 4 |
| $J$, $\operatorname{tr}J$, $\det J$ | Jacobian, its trace and determinant | 5 |
| $T$, $\vartheta$ | period of a limit cycle; phase | 6 |
| $u(x, t)$, $w(x - y)$ | neural field; spatial connectivity kernel | 8 |
| $W(a) = \int_0^a w$ | integrated kernel (Amari's bump condition) | 8 |
| $\hat w(k)$, $\lambda(k)$, $k_c$ | Fourier transform of $w$; growth rate; critical wavenumber | 9 |
| $\gamma = f'(u_0)$ | gain at a uniform state | 9 |
| $L(\vec u)$ | Lyapunov (energy) function | 11 |
| $\vec\xi^{\,\mu}$, $m_\mu$ | stored pattern; overlap with it | 11 |
| $\eta(s)$, $\kappa(s)$, $\hat t$ | refractory and response kernels; last spike time | 12 |
| $A(t)$ | population activity (spikes per neuron per unit time) | 12 |
| $\theta_i$, $F(\theta, s)$ | phase of a spiking neuron; its speed | 13 |
| $\eta_i(\theta, t)$ | phase density (Klimontovich) | 13 |
| $\eta_0$, $\Delta$ | centre and half-width of the Lorentzian distribution of excitabilities | 12, 13 |
| $r$, $v$ | rate and mean voltage in the MPR equations | 13 |
| $N$ | number of neurons | 1, 14 |
| $F(a)$, $G(a)$ | drift and diffusion of the stochastic population | 14 |
| $C$, $\sigma^2$ | covariance / variance | 14, 15 |
| $\Phi(a)$ | quasi-potential | 14 |
| $S$, $\epsilon$ | action; small parameter ($1/N$) | 15 |
| $\Gamma[a]$, $\Gamma[a, C]$ | effective actions | 15 |

## Glossary

- **Activity equation**: first-order ODE for an activity, with a gain function of a weighted sum of inputs.
- **Coarse-graining**: describing a system at lower resolution, averaging out microscopic detail.
- **Mean field theory**: the approximation that each unit feels only the average of the others; all correlations neglected.
- **Quasi-stationarity**: activity changes slowly compared with the averaging window (one interspike interval).
- **Nullcline**: curve where one component of the flow vanishes.
- **Hysteresis**: the state depends on the history of the input, because of coexisting stable states.
- **Hopf bifurcation**: a steady state loses stability with complex eigenvalues and a small limit cycle appears.
- **Homoclinic bifurcation**: a limit cycle collides with a saddle; its period diverges.
- **Bump, front, pulse**: localised stationary activity; a travelling switch between two states; a travelling localised excitation.
- **Turing instability**: a uniform state loses stability to a spatial pattern of preferred wavelength.
- **Lyapunov function**: a quantity that never increases along trajectories.
- **Klimontovich equation**: the continuity equation for the exact (singular) density of particles or phases.
- **Master equation, Fokker–Planck, Langevin**: exact, diffusion and stochastic-trajectory descriptions of a random process.
- **Linear noise approximation**: Gaussian fluctuations around mean field, variance $\propto 1/N$.
- **Loop expansion**: expansion of a path integral around its critical point, organised by Feynman diagrams; each loop adds a power of $\epsilon$.
- **Effective action**: Legendre transform of the cumulant generating functional; its stationary point gives the exact mean.

## Reading list

**The review and the original papers**
- C. C. Chow and Y. Karimipanah, “Before and beyond the Wilson–Cowan equations,” *J. Neurophysiol.* 123, 1645–1656 (2020).
- H. R. Wilson and J. D. Cowan, “Excitatory and inhibitory interactions in localized populations of model neurons,” *Biophys. J.* 12, 1–24 (1972).
- H. R. Wilson and J. D. Cowan, “A mathematical theory of the functional dynamics of cortical and thalamic nervous tissue,” *Kybernetik* 13, 55–80 (1973).

**Collected in `resources/WC-Model/refs/`**
- Kilpatrick (2014), Wilson–Cowan model, *Encyclopedia of Computational Neuroscience*.
- Ermentrout (2014), Neural field models, *Encyclopedia of Computational Neuroscience*; Ermentrout (1998), “Neural networks as spatio-temporal pattern-forming systems,” *Rep. Prog. Phys.* 61, 353.
- Bressloff, Cowan, Golubitsky, Thomas and Wiener (2002), “What geometric visual hallucinations tell us about the visual cortex,” *Neural Comput.* 14, 473.
- Chow and Buice (2015), “Path integral methods for stochastic differential equations,” *J. Math. Neurosci.* (arXiv:1009.5966).
- Buice, Cowan and Chow (2010), “Systematic fluctuation expansion for neural network activity equations,” *Neural Comput.* (arXiv:0902.3925).
- Hildebrand, Buice and Chow (2007), “Kinetic theory of coupled oscillators,” *Phys. Rev. Lett.* (arXiv:nlin/0612029); Buice and Chow (2007), “Correlations, fluctuations and stability of a finite-size network of coupled oscillators,” *Phys. Rev. E* (arXiv:0704.1650).
- Buice and Chow (2013), “Generalized activity equations for spiking neural network dynamics,” *Front. Comput. Neurosci.*; Buice and Chow (2013), “Dynamic finite size effects in spiking neural networks,” *PLoS Comput. Biol.*
- Qiu and Chow (2018), “Finite-size effects for spiking neural networks with spatially dependent coupling,” *Phys. Rev. E* (arXiv:1805.03601).
- Helias and Dahmen (2019), *Statistical field theory for neural networks*, lecture notes (arXiv:1901.10416).
- Ocker et al. (2017), “Linking structure and activity in nonlinear spiking networks,” *PLoS Comput. Biol.*
- Hopfield (1982), *PNAS* 79, 2554; Hopfield (1984), *PNAS* 81, 3088.
- Gerstner, Kistler, Naud and Paninski, *Neuronal Dynamics*, chapters 12–15 (online; links in `resources/WC-Model/web/`).

**Not downloaded (DOIs)**
- Cowan, Neuman and van Drongelen (2016), “Wilson–Cowan equations for neocortical dynamics,” *J. Math. Neurosci.*, doi:10.1186/s13408-015-0034-5.
- Destexhe and Sejnowski (2009), “The Wilson–Cowan model, 36 years later,” *Biol. Cybern.*, doi:10.1007/s00422-009-0328-3.
- “The evolution of the Wilson–Cowan model,” *Biol. Cybern.* (2021), doi:10.1007/s00422-021-00912-7.
- Coombes (2005), “Waves, bumps, and patterns in neural field theories,” *Biol. Cybern.*, doi:10.1007/s00422-005-0574-y.
- Bressloff et al. (2001), “Geometric visual hallucinations, Euclidean symmetry and the functional architecture of striate cortex,” *Phil. Trans. R. Soc. B* (PMC1088430).
- Griffith (1963), “A field theory of neural nets: I,” *Biophys. J.*, doi:10.1016/S0006-3495(63)86822-8.
- Amari (1977), “Dynamics of pattern formation in lateral-inhibition type neural fields,” *Biol. Cybern.*, doi:10.1007/BF00337259.
- Ermentrout and Cowan (1979), “A mathematical theory of visual hallucination patterns,” *Biol. Cybern.*, doi:10.1007/BF00336965.
- Buice and Chow (2013), “Beyond mean field theory: statistical field theory for neural networks,” *J. Stat. Mech.*, doi:10.1088/1742-5468/2013/03/P03003.
- Montbrió, Pazó and Roxin (2015), “Macroscopic description for networks of spiking neurons,” *Phys. Rev. X* 5, 021028.
