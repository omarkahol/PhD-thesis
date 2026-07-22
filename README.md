# Thesis

This repository contains the LaTeX source code for the thesis and its accompanying presentation.

## Compilation

The thesis can be compiled using the provided `makefile`. Simply run the commands below in the root of the repository to perform different actions:

- `make` or `make all`: Compiles the main thesis **without** the cover pages.
- `make full`: Compiles the main thesis **with** the IPP cover pages.
- `make fast`: Acts the same as `make all`.
- `make chapters`: Compiles each chapter separately and outputs the resulting PDFs into a `chapters/` directory.
- `make chapter-<name>`: Compiles a single specific chapter (e.g., `make chapter-introduction`).
- `make setup-no-covers`: Configures the build flags to exclude the cover pages.
- `make setup-covers`: Configures the build flags to include the cover pages.
- `make covers`: Compiles only the cover pages (located in the `IPP` directory).
- `make clean`: Removes the `.build` auxiliary directory and the generated thesis PDF.
- `make clean-cache`: Removes the global Biber cache and cleans the local build files (useful if Biber acts up).
- `make presentation`: Compiles the presentation slides (in `presentation/` directory) into a PDF.

## Acknowledgements

This thesis was typeset with LaTeX.
It uses the *Clean Thesis* style developed by Ricardo Langner.
The design of the *Clean Thesis* style is inspired by user guide documents from Apple Inc.

Download the *Clean Thesis* style at http://cleanthesis.der-ric.de/

This project has received funding from the European Union's Horizon Europe research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101072551 (TRACES).
