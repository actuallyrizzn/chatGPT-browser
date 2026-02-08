## Proposed solution

- **Root cause:** `app.secret_key = os.urandom(24)` runs at import time, so every process restart gets a new key and all existing sessions are invalidated. In multi-worker setups each worker would have a different key.
- **Fix:** Load secret key from environment variable `SECRET_KEY` first; if not set, try reading from a persistent file (e.g. `.secret_key` in the project root, created once if missing). Only fall back to `os.urandom(24)` in development and log a warning so production deployments are reminded to set `SECRET_KEY`.
- **Backward compatibility:** If neither env nor file is set, retain current behavior (urandom) but log a warning. No breaking change for existing installs that do not set SECRET_KEY.
