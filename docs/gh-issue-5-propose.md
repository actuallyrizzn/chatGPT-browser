## Proposed solution

- **Root cause:** In `templates/settings.html` the file input has `name="json_file"`, but in `app.py` the import route checks `request.files['file']`. So the backend never receives the uploaded file and always returns 400 "No file uploaded".
- **Fix (option A):** Change the template to `name="file"` so it matches the backend. Minimal change, web import works immediately.
- **Fix (option B):** Change the backend to accept both: `request.files.get('file') or request.files.get('json_file')` so either form field name works.
- **Recommendation:** Option A (change template to `name="file"`) for consistency with the backend and common convention. Will implement Option A.
