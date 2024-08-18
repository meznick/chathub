# Define directories and files
SRC_DIR := .
DOMAIN := bot  # potentially there will be more of these
POT_FILE := bot/locales/$(DOMAIN).pot
PO_DIR := bot/locales
CFG_FILE := babel.cfg

# Goals
.PHONY: extract compile update

# only for full re-initialization
all: extract init update compile

# generic update on new iterations:
update_templates: extract update compile

extract:
	@echo "Extracting..."
	pybabel extract -F $(CFG_FILE) -o $(POT_FILE) --input-dirs=$(SRC_DIR) \
	--project="SpeedDatingBot" \
	--version="0.1" \
	--copyright-holder="Nick Letov" \
	--msgid-bugs-address="mezhng@gmail.com"

update:
	@echo "Updating..."
	pybabel update -i $(POT_FILE) -d $(PO_DIR)

compile:
	@echo "Compiling..."
	pybabel compile -d $(PO_DIR) -D $(DOMAIN)

init:
	@echo "Initializing for ru..."
	pybabel init -i $(POT_FILE) -d $(PO_DIR) -l ru -D $(DOMAIN)
	@echo "Initializing for en..."
	pybabel init -i $(POT_FILE) -d $(PO_DIR) -l en -D $(DOMAIN)
