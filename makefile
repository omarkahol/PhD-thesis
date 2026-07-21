PROJ = my-thesis
LC = latexmk
AUXSDIR = .build
OPT = -halt-on-error
# NOTE: If using biber/biblatex, consider removing '-bibtex' from ARGS below
ARGS = -pdfxe -outdir=$(AUXSDIR) -pdfxelatex="xelatex $(OPT)" -use-make -bibtex
IPP_DIR = IPP
IPP_COVERS = 1ere.tex 4eme.tex
SOURCES = $(PROJ).tex my-thesis-setup.tex cleanthesis.sty bib-refs.bib $(wildcard content/*.tex)

# 'make' or 'make all' -> compiles thesis without covers
all: setup-no-covers $(PROJ).pdf

# 'make fast' -> same as 'all'
fast: all

# 'make chapters' -> compile each chapter separately into the chapters/ folder
chapters: setup-no-covers
	mkdir -p $(AUXSDIR)/chapters/content
	@for chap in content/chapter-*.tex; do \
		chap_name=$$(basename $$chap .tex); \
		echo "Compiling $$chap_name..."; \
		$(LC) -pdfxe -outdir=$(AUXSDIR)/chapters -jobname=$$chap_name -pretex="\def\UseIncludeOnly{1} \includeonly{content/$$chap_name}" -usepretex my-thesis.tex || exit 1; \
	done
	mkdir -p chapters
	cp $(AUXSDIR)/chapters/chapter-*.pdf chapters/
	@echo "All chapters compiled into chapters/ directory."

# 'make chapter-<name>' -> compile a specific chapter (e.g., make chapter-introduction)
chapter-%: setup-no-covers
	mkdir -p $(AUXSDIR)/chapters/content
	@echo "Compiling chapter-$*..."
	$(LC) -pdfxe -outdir=$(AUXSDIR)/chapters -jobname=chapter-$* -pretex="\def\UseIncludeOnly{1} \includeonly{content/chapter-$*}" -usepretex $(PROJ).tex || exit 1
	mkdir -p chapters
	cp $(AUXSDIR)/chapters/chapter-$*.pdf chapters/
	@echo "Chapter chapter-$* compiled into chapters/ directory."


# --- Main Compilation ---
$(PROJ).pdf : $(SOURCES)
	mkdir -p $(AUXSDIR)/content
	$(LC) $(ARGS) $(PROJ).tex || { \
		printf "\n\033[1;31m==================================================\033[0m\n"; \
		printf "\033[1;31m   LATEX COMPILATION FAILED! Extracting errors... \033[0m\n"; \
		printf "\033[1;31m==================================================\033[0m\n\n"; \
		LOG_FILE="$(AUXSDIR)/$(PROJ).log"; \
		BLG_FILE="$(AUXSDIR)/$(PROJ).blg"; \
		if grep -q -E "^[[:space:]]*!|Emergency stop|Fatal error" $$LOG_FILE 2>/dev/null; then \
			printf "\033[1;31m[Found error(s) in LaTeX log file ($$LOG_FILE)]:\033[0m\n"; \
			grep -n -A 5 -E "^[[:space:]]*!|Emergency stop|Fatal error" $$LOG_FILE; \
		elif [ -f $$BLG_FILE ] && grep -q -E "ERROR -|I found no|error|Fatal" $$BLG_FILE 2>/dev/null; then \
			printf "\033[1;31m[Found error(s) in Bibliography log file ($$BLG_FILE)]:\033[0m\n"; \
			grep -n -A 3 -E "ERROR -|I found no|error|Fatal" $$BLG_FILE; \
		else \
			printf "\033[1;33mNo standard error strings found. Printing end of LaTeX log:\033[0m\n"; \
			tail -n 20 $$LOG_FILE 2>/dev/null; \
			if [ -f $$BLG_FILE ]; then \
				printf "\n\033[1;33mPrinting complete Bibliography log ($$BLG_FILE):\033[0m\n"; \
				cat $$BLG_FILE; \
			fi; \
		fi; \
		exit 1; \
	}
	mv .build/${PROJ}.pdf ./

# --- Cover Toggles ---
setup-no-covers:
	mkdir -p $(AUXSDIR)
	printf '%s\n' '\renewcommand{\thesisUseIPPCovers}{0}' > $(AUXSDIR)/build-flags.tex

setup-covers:
	mkdir -p $(AUXSDIR)
	printf '%s\n' '\renewcommand{\thesisUseIPPCovers}{1}' > $(AUXSDIR)/build-flags.tex

# --- Auxiliary Rules ---
covers:
	cd $(IPP_DIR) && $(LC) -pdfxe -pdfxelatex="xelatex $(OPT)" -use-make -bibtex $(IPP_COVERS)

clean:
	rm -rf $(AUXSDIR)
	rm -f $(PROJ).pdf

# Run this manually via 'make clean-cache' ONLY when Biber misbehaves
clean-cache: clean
	@echo "Clearing global Biber cache... (Next compilation will take a few seconds longer)"
	rm -rf $$(biber --cache)

.PHONY: all fast full clean covers clean-cache setup-no-covers setup-covers