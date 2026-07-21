# A Beamer template for UGE/Inria/CEA

## Why this repository ?
Since we are often working with different institutions, we have to switch between our their templates regularly, which is not always an easy task.


## What is it ?
The purpose of this LaTeX/Beamer theme is to provide a template for presentations at Université Gustave Eiffel or Inria or CEA.


## How to Compile and Build
A simplified `Makefile` is provided to compile the presentation slides directly. Make sure you have a LaTeX distribution (such as MacTeX or TeX Live) installed with `pdflatex`, `bib2gls`, and `biber` in your system path.

To build the presentation PDF:
```bash
make
# or
make build
```
This runs the full compilation sequence:
1. `pdflatex` to generate initial auxiliary files.
2. `bib2gls` to process acronyms and symbols.
3. `biber` to process bibliography citations.
4. Two more runs of `pdflatex` to resolve references, citations, and table of contents.

To clean up intermediate build files (like `.aux`, `.log`, `.nav`, etc.):
```bash
make clean
```

To clean up everything including the generated `main.pdf`:
```bash
make distclean
```

### Error Handling
The `Makefile` intercepts any fatal compilation errors from `pdflatex` or log warnings from `biber`, formats them, and prints the error snippet in **red** to the terminal for easy debugging.

- Overleaf link (read only): https://www.overleaf.com/read/vxnjgfmyvccj

  If you do not want to install a LaTeX distribution or just want to try first, on Overleaf you can click on `Make a copy` (or `copy project`, according to where you are).
  This copy will be editable so you will be able to play around. 


## Demonstration files
- **ready2Go**: <img src="original/gotham-example/screenshotGotham-1.png" width="300">
- **UGE official**: <img src="original/examples_UGE/screenshotUGEofficial.png" width="300">
- **UGE unofficial light**: <img src="original/examples_UGE/screenshotUGEunofficial-1.png" width="300">
- **UGE unofficial dark**: <img src="original/examples_UGE/screenshotUGEunofficial-2.png" width="300">
- **Inria old style**: <img src="original/examples_Inria/screenshotInriaOld.png" width="300">
- **Inria RF style**: <img src="original/examples_Inria/screenshotInriaRF.png" width="300">
- **CEA example**: <img src="original/examples_CEA/screenshotCEA.png" width="300">


## Credits & Modifications
This repository is based on the original template developed by:
* **Romain NOËL** (romain.noel@inria.fr / romain.noel@univ-eiffel.fr)
* Original Github repository: [beamer-template_uge-inria](https://github.com/Universite-Gustave-Eiffel/beamer-template_uge-inria)

This fork introduces extra modifications to simplify the build process (migrating away from CMake/latexmk in favor of a clean, simple Makefile), resolves theme incompatibility issues with the appendix slide numbers, and fully integrates the bibliography and reference listings directly in the slides.

