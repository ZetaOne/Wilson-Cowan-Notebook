# Wilson-Cowan-Notebook

**The website: https://zetaone.github.io/Wilson-Cowan-Notebook/**

A book on the Wilson&ndash;Cowan model of neuronal populations, from the basics up, following
C. C. Chow and Y. Karimipanah, *Before and beyond the Wilson&ndash;Cowan equations*, J. Neurophysiol. 123
(2020) 1645-1656 ([the paper](https://doi.org/10.1152/jn.00404.2019)), together with Wilson & Cowan (1972).

## What is on the site

- **The book**: 16 chapters and 3 appendices, from why populations and the sigmoid, through the E&ndash;I
  phase plane, oscillations, multistability, neural fields and patterns, to spiking mean fields,
  finite-size effects and path integrals; in the browser or as a PDF.
- **Slide decks**, one per chapter, geometry first; each remembers the slide you stopped at.
- **The code** behind every figure, to read or download.
- **A study kit**: XPP `.ode` files and executed notebooks.
- **Your reading**, kept in your own browser only: highlights and notes, where you stopped, your
  progress in each deck. Nothing is sent anywhere.

Every simulation is computed by Bard Ermentrout's
[XPPAUT](https://sites.pitt.edu/~phase/bard/bardware/xpp/xpp.html) through [pyauto-xpp](https://zetaone.github.io/pyauto-xpp/); the
models can also be explored in the browser with [XPPAUT-Web](https://zetaone.github.io/XPPAUT-Web/). Its sister book:
[Isochrons-Notebook](https://zetaone.github.io/Isochrons-Notebook/).

## About this repository

The site files here are generated: they are rebuilt from the book's sources, so changes go into
those, not into these files. GitHub Pages publishes the `main` branch.

The sources are in [`source/wilson-cowan/`](source/wilson-cowan/), copied in on every build:

- `book/`: the chapters (Markdown) and the book builder (`build.mjs`, `build_code.py`)
- `figs/`: one script per figure; `wc_lib.py`, `figkit.py`: the shared model code and plot style
- `decks/`: one slide-deck script per chapter (ManimGX through `sciviz`, the animation tools of
  this project, which are not included here) and `render_all.sh`
- `study/`: the XPP `.ode` files of the study kit and `make_notebooks.py`, which writes its notebooks
- `site/`: this website's builder (`build.py`) and its page assets

Made by Jeevan Kumar Gochhayat ([github.com/ZetaOne](https://github.com/ZetaOne)).
