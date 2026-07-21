# Build configuration
BUILD_DIR ?= .build
PDF_TARGET ?= main.pdf
SRC ?= main.tex

# Tool definitions
PDFLATEX ?= pdflatex
BIBER ?= biber

# Environment variables setup to ensure paths are correct
export TEXINPUTS := .:$(BUILD_DIR):./parts:./resources:./sources:./sources/gotham:./sources/Inria:$(TEXINPUTS)
export BIBINPUTS := .:./resources:$(BIBINPUTS)

.PHONY: all build clean distclean fast full

all: build

fast:
	mkdir -p $(BUILD_DIR)
	$(call run_latex)
	cp $(BUILD_DIR)/main.pdf $(PDF_TARGET)

full: build

define run_latex
$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) --shell-escape $(SRC) || { \
	printf "\n\033[1;31m==================================================\033[0m\n"; \
	printf "\033[1;31m   LATEX COMPILATION FAILED! Extracting errors... \033[0m\n"; \
	printf "\033[1;31m==================================================\033[0m\n\n"; \
	LOG_FILE="$(BUILD_DIR)/main.log"; \
	BLG_FILE="$(BUILD_DIR)/main.blg"; \
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
endef

build:
	mkdir -p $(BUILD_DIR)
	$(call run_latex)
	-bib2gls --dir $(BUILD_DIR) main
	-$(BIBER) --output-directory $(BUILD_DIR) $(BUILD_DIR)/main
	$(call run_latex)
	$(call run_latex)
	cp $(BUILD_DIR)/main.pdf $(PDF_TARGET)

clean:
	rm -rf $(BUILD_DIR)

distclean: clean
	rm -f $(PDF_TARGET)