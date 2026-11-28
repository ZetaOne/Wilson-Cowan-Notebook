This appendix collects the mathematics used in the book, each with the picture that goes with it. It assumes calculus and a first course in differential equations; Strogatz's *Nonlinear Dynamics and Chaos* (chapters 2–8) is the natural companion.

## A.1 Flows on a line

For $\dot x = F(x)$, draw $F$ against $x$. Where $F > 0$ the state moves right, where $F < 0$ left. Zeros of $F$ are **fixed points**: stable where $F$ crosses zero going down ($F' < 0$), unstable where it crosses going up. Stable and unstable points alternate. As a parameter changes, two fixed points can collide and vanish where the curve becomes tangent to the axis: a **saddle-node (fold) bifurcation**. Near a vanished pair the flow stays slow (a “ghost”), with passage time $\propto 1/\sqrt{\text{distance from the fold}}$. Used in Chapters 2, 7, 10, 14.

## A.2 Flows in the plane: linear stability

For $\dot{\vec x} = \vec F(\vec x)$ in two dimensions, a fixed point $\vec x^*$ is classified by the **Jacobian** $J = D\vec F(\vec x^*)$, through its trace $\tau = J_{11} + J_{22}$ and determinant $\Delta = J_{11}J_{22} - J_{12}J_{21}$:

| condition | type |
|---|---|
| $\Delta < 0$ | saddle |
| $\Delta > 0$, $\tau < 0$, $\tau^2 > 4\Delta$ | stable node |
| $\Delta > 0$, $\tau < 0$, $\tau^2 < 4\Delta$ | stable focus (spiral in) |
| $\Delta > 0$, $\tau > 0$ | unstable node or focus |

**Nullclines** ($\dot x_1 = 0$ and $\dot x_2 = 0$) cross at fixed points; where they are tangent, $\Delta = 0$ (a fold). A **Hopf bifurcation** happens where $\tau$ passes through zero with $\Delta > 0$: eigenvalues $\pm i\sqrt\Delta$, a small cycle of period $\approx 2\pi/\sqrt\Delta$. **Poincaré–Bendixson**: a trajectory confined to a bounded region with no fixed points approaches a closed orbit. Used in Chapters 5–7.

## A.3 Fourier modes and dispersion relations

A linear equation with translation-invariant coupling, $\partial_t u = -u + \gamma\int w(x - y)u(y)\,\dd y$, is diagonalised by waves $e^{ikx}$, because convolution with $w$ multiplies a wave by the Fourier transform $\hat w(k) = \int w(x)e^{-ikx}\,\dd x$. Each mode grows at its own rate, $\lambda(k) = -1 + \gamma\hat w(k)$. Instability first appears at the maximum of $\hat w$: at $k = 0$ the whole field switches (a uniform fold); at $k_c > 0$ a pattern of wavelength $2\pi/k_c$ forms (a **Turing instability**). For a Gaussian, $\int e^{-x^2/\sigma^2}e^{-ikx}\,\dd x = \sigma\sqrt\pi\,e^{-\sigma^2k^2/4}$. Used in Chapter 9.

## A.4 Continuity equations

If objects move along a line or circle with velocity $F(\theta)$ and are conserved, their density $\eta$ obeys $\partial_t\eta + \partial_\theta(F\eta) = 0$: the change in a small interval equals inflow minus outflow. At steady state the flux $F\eta$ is constant, so $\eta \propto 1/F$: crowded where slow. Used in Chapter 13.

## A.5 Gaussian integrals and Wick's theorem

$\int e^{-x^2/(2\sigma^2)}\,\dd x = \sqrt{2\pi}\,\sigma$. For a vector, $\int e^{-\frac12\vec x^{\,T}A\vec x + \vec J\cdot\vec x}\,\dd^n x = (2\pi)^{n/2}(\det A)^{-1/2}e^{\frac12\vec J^{\,T}A^{-1}\vec J}$. Derivatives with respect to $\vec J$ generate moments. All moments of a zero-mean Gaussian follow from the covariance by summing over pairings (**Wick's theorem**): $\langle x_1x_2x_3x_4\rangle = C_{12}C_{34} + C_{13}C_{24} + C_{14}C_{23}$. Used in Chapter 15.

## A.6 Laplace's method

For small $\epsilon$, $\int e^{-S(x)/\epsilon}\,g(x)\,\dd x$ is dominated by the minimum $x_0$ of $S$. Expanding $S$ to second order gives a Gaussian of variance $\epsilon/S''(x_0)$; higher terms give corrections in powers of $\epsilon$. The mean is shifted from $x_0$ by $-\epsilon S'''/(2S''^2) + O(\epsilon^2)$. Used in Chapter 15.

## A.7 Stochastic processes

- **Master equation**: for a jump process, $\dot P(n) = \sum(\text{rate into } n)P - \sum(\text{rate out of } n)P$. Simulate exactly with the **Gillespie algorithm**: wait an exponential time with rate equal to the total rate, then choose a jump with probability proportional to its rate.
- **Langevin equation**: $\dot x = F(x) + \sqrt{D(x)}\,\xi(t)$ with white noise $\langle\xi(t)\xi(t')\rangle = \delta(t - t')$; equivalent to the **Fokker–Planck equation** $\partial_t p = -\partial_x(Fp) + \tfrac12\partial_x^2(Dp)$. XPPAUT integrates it with `wiener` variables and the Euler method.
- **Ornstein–Uhlenbeck process**: $\dot x = -kx + \sqrt D\,\xi$ has stationary variance $D/(2k)$.
- **Kramers' law**: the mean time to escape a potential well of depth $\Delta\Phi$ with noise of strength $\propto 1/N$ grows like $e^{N\Delta\Phi}$.

Used in Chapters 14 and 15.
