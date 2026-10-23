# Build, check and publish the packages of gettext-translator.
#
# Two ways to publish:
#   - make release: tags vX.Y.Z and pushes the tag; the Publish GitHub workflow
#     uploads to PyPI with Trusted Publishing (no tokens needed).
#   - make publish-test / make publish: uploads from this machine with twine,
#     using the API tokens in ~/.pypirc or TWINE_USERNAME / TWINE_PASSWORD.
# Already published versions are skipped, bump the version of each changed package.

PYTHON ?= python3
PACKAGES := . $(wildcard translators/*)
VERSION := $(shell sed -n 's/^__version__ = "\(.*\)"/\1/p' src/gettext_translator/version.py)
PART ?= patch
NEW_VERSION = $(shell $(PYTHON) -c "v=[int(x) for x in '$(VERSION)'.split('.')]; i=['major','minor','patch'].index('$(PART)'); v[i]+=1; v[i+1:]=[0]*(2-i); print('.'.join(map(str,v)))" 2>/dev/null)

.PHONY: help dev lint test build check bump publish-test publish release clean

help:
	@echo "make dev           install the packages in editable mode and the dev tools"
	@echo "make lint          ruff check"
	@echo "make test          pytest"
	@echo "make build         build sdist and wheel of every package into dist/"
	@echo "make check         lint, test, build and twine check"
	@echo "make bump         bump the patch version and commit it (PART=minor or PART=major)"
	@echo "make publish-test  upload dist/ to TestPyPI with twine"
	@echo "make publish       upload dist/ to PyPI with twine"
	@echo "make release       tag v$(VERSION) and push it, the Publish workflow uploads to PyPI"
	@echo "make clean         remove build artifacts"

dev:
	$(PYTHON) -m pip install -e translators/gettext-translator-service -e . \
		-e translators/gettext-translator-azure -e translators/gettext-translator-chatgpt \
		-e translators/gettext-translator-gemini -e translators/gettext-translator-ollama \
		pytest ruff build twine

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

build: clean
	for package in $(PACKAGES); do $(PYTHON) -m build "$$package" --outdir dist || exit 1; done

check: lint test build
	$(PYTHON) -m twine check --strict dist/*

bump:
	@git diff --quiet HEAD || { echo "Commit your changes first"; exit 1; }
	@[ -n "$(NEW_VERSION)" ] || { echo "PART must be major, minor or patch"; exit 1; }
	sed -i 's/^__version__ = ".*"/__version__ = "$(NEW_VERSION)"/' src/gettext_translator/version.py
	git commit -am "v$(NEW_VERSION)"

publish-test: check
	$(PYTHON) -m twine upload --repository testpypi --skip-existing dist/*

publish: check
	@read -p "Upload dist/ to PyPI? Published versions can't be replaced [y/N] " answer && [ "$$answer" = y ]
	$(PYTHON) -m twine upload --skip-existing dist/*

release: check
	@git diff --quiet HEAD || { echo "Commit your changes first"; exit 1; }
	@read -p "Tag v$(VERSION) and push it to origin? [y/N] " answer && [ "$$answer" = y ]
	git tag -a v$(VERSION) -m "v$(VERSION)"
	git push origin v$(VERSION)

clean:
	rm -rf dist build src/*.egg-info translators/*/*.egg-info translators/*/build
