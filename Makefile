PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
NPM ?= npm
UVICORN ?= uvicorn

.PHONY: install-backend install-frontend install dev-backend dev-frontend build-frontend rebuild-index check-backend check-frontend check

install-backend:
	$(PIP) install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch==2.2.2+cpu
	$(PIP) install --no-cache-dir -r backend/requirements.txt

install-frontend:
	cd frontend && $(NPM) install

install: install-backend install-frontend

dev-backend:
	$(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && $(NPM) run dev

build-frontend:
	cd frontend && $(NPM) run build

rebuild-index:
	$(PYTHON) -m backend.scripts.rebuild_index

check-backend:
	$(PYTHON) -m compileall backend
	$(PYTHON) -c "from backend.app.main import app; print(app.title)"

check-frontend:
	cd frontend && $(NPM) run build

check: check-backend check-frontend
