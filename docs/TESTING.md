# Testing Guide

## Setup (use venv)

```powershell
# From project root
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-testing.txt
# For E2E tests only:
playwright install
```

## Running tests

```powershell
# All tests (unit + integration + E2E if Playwright installed)
pytest

# Exclude E2E (faster, no browser)
pytest -m "not e2e"

# With coverage report
pytest -m "not e2e" --cov=app --cov-report=term-missing --cov-report=html

# Only unit tests
pytest tests/unit

# Only integration tests
pytest tests/integration

# Only E2E tests
pytest tests/e2e -m e2e
```

## Coverage

Running `pytest -m "not e2e" --cov=app --cov-report=term-missing` targets **~97%** coverage of `app.py`. Remaining untested: `if __name__ == '__main__'` (app entry point) and a few defensive branches.

- **Unit**: Template filters (`fromjson`, `tojson`, `datetime`, `json_loads`, `markdown`), helpers (`_parse_timestamp`, `get_setting`, `set_setting`), `import_conversations_data` (including empty message skip, metadata), `init_db`, `init_db.main()`, `run_ingest.main()`.
- **Integration**: All Flask routes with a temporary SQLite DB (index, conversation, nice conversation, full view, 404s, settings, update_names, toggles, import including empty file and error handling).
- **E2E**: Home page, settings link, conversation nice view, settings page (Playwright; optional).

## Requirements

- **requirements-testing.txt**: pytest, pytest-cov, pytest-xdist, pytest-mock, pytest-playwright, playwright, httpx.
- E2E uses a live server on port **5764** (ensure it is free when running E2E tests).
