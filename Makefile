PYTHON ?= python3
CHECK_SCRIPT ?= scripts/site_checks.py
GITLEAKS ?= gitleaks

.PHONY: bootstrap test smoke consistency secret-scan ci

bootstrap:
	@echo "No bootstrap step required for static public pages."

test:
	@$(PYTHON) $(CHECK_SCRIPT) --mode test

smoke:
	@$(PYTHON) $(CHECK_SCRIPT) --mode smoke

consistency:
	@$(PYTHON) $(CHECK_SCRIPT) --mode consistency

secret-scan:
	@command -v $(GITLEAKS) >/dev/null
	@$(GITLEAKS) detect --no-banner --source .

ci: bootstrap test smoke consistency secret-scan
