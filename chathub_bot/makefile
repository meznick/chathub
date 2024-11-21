# Define directories and files
SRC_DIR := .
# potentially there will be more of these
DOMAIN := bot
POT_FILE := bot/locales/$(DOMAIN).pot
PO_DIR := bot/locales
CFG_FILE := babel.cfg
VERSION := $(shell python3 -c "import os; import sys; sys.path.insert(0, '$(SRC_DIR)'); from bot import __version__; print(__version__)")

# Goals
.PHONY: extract compile update

# auto run all

all: extract update compile

# generic update on new iterations:
update_templates: extract update

extract:
	@echo "Extracting..."
	pybabel extract -F $(CFG_FILE) -o $(POT_FILE) --input-dirs=$(SRC_DIR) \
	--project="SpeedDatingBot" \
	--version=$(VERSION)

update:
	@echo "Updating..."
	pybabel update -i $(POT_FILE) -d $(PO_DIR) -D $(DOMAIN)

compile:
	@echo "Compiling..."
	pybabel compile -d $(PO_DIR) -D $(DOMAIN)

init:
	@echo "Initializing for ru..."
	pybabel init -i $(POT_FILE) -d $(PO_DIR) -l ru -D $(DOMAIN)
	@echo "Initializing for en..."
	pybabel init -i $(POT_FILE) -d $(PO_DIR) -l en -D $(DOMAIN)
