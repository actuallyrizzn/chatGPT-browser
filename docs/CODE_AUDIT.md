# Code Audit -- ChatGPT Browser

**Date:** 2026-02-08
**Auditor:** AI Code Audit (Neckbeard Mode)
**Scope:** All application source -- `app.py`, `init_db.py`, `schema.sql`, `run_ingest.py`, templates, CSS, tests

---

## Executive Summary

The application works, but it is in a "weekend prototype" state. There are security holes, performance cliffs, architectural drift between `schema.sql` and the runtime DDL, a markdown XSS vector, zero real test coverage, and several dark-mode / UX regressions. The sections below are ordered roughly by severity.

---

## 1. Security

### 1.1 Secret Key Is Random Per Restart (HIGH)

```python
app.secret_key = os.urandom(24)  # app.py line 11
```

Every time the Flask process restarts, every user session is invalidated. Worse, in a multi-worker deployment (gunicorn, waitress) each worker would have a **different** secret key, meaning sessions bounce randomly between workers.

**Fix:** Load from an environment variable or a persistent file:
```python
app.secret_key = os.environ.get('SECRET_KEY') or open('.secret_key','rb').read()
```

### 1.2 Markdown XSS (HIGH)

```python
@app.template_filter('markdown')
def markdown_filter(text):
    if text is None:
        return ""
    return Markup(md.convert(text))   # line 148
```

`Markup()` tells Jinja "this string is already safe -- do not escape it." The Python `markdown` library does **not** sanitise HTML by default, so any conversation content containing `<script>`, `<img onerror=...>`, or `<iframe>` will be injected verbatim into the page. Because conversation data comes from an external JSON export, this is a stored XSS vector.

**Fix:** Add `bleach` or use the `markdown` library's `safe_mode` / an HTML-sanitiser extension, or at minimum run the output through `markupsafe.escape()` before wrapping in `Markup()`.

### 1.3 Markdown Instance Is Shared and Never Reset (MEDIUM)

```python
md = markdown.Markdown(extensions=['fenced_code', 'tables'])  # line 14
```

The `markdown.Markdown` object accumulates state between calls (e.g. footnote counters, reference link defs). After rendering N messages, cross-contamination between conversations is inevitable. You must call `md.reset()` before each conversion, or create a new instance per call:

```python
def markdown_filter(text):
    md.reset()
    return Markup(md.convert(text))
```

### 1.4 No CSRF Protection (MEDIUM)

The settings form and import form use `POST` but there is no CSRF token. Any page on any origin can submit a form pointed at `/import` or `/update_names`. Flask-WTF or a manual token would fix this.

### 1.5 File Upload Field Name Mismatch (BUG)

Settings template:
```html
<input type="file" ... id="json_file" name="json_file" ...>
```

Route handler:
```python
if 'file' not in request.files:   # line 424
```

The field is named `json_file` in the HTML but the backend looks for `file`. **The import form is completely broken via the web UI.** It will always return "No file uploaded."

### 1.6 No Upload Size Limit

Flask's default `MAX_CONTENT_LENGTH` is unlimited. A malicious or accidental multi-GB upload will eat all RAM (the handler does `file.read()` into a single string). Set:
```python
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024  # 256 MB
```

### 1.7 Toggle Routes Use GET and Are Not Idempotent

`/toggle_dark_mode`, `/toggle_view_mode`, `/toggle_verbose_mode` are all `GET` endpoints that mutate server-side state. Browser prefetch, link scanners, and crawlers can flip settings silently. These should be `POST`.

---

## 2. Database & Data Layer

### 2.1 Schema Drift -- `schema.sql` vs Runtime DDL (HIGH)

`schema.sql` and `init_db()` inside `app.py` define **completely different** schemas:

| Difference | `schema.sql` | `app.py init_db()` |
|---|---|---|
| `conversations.id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | `TEXT PRIMARY KEY` |
| Messages columns | `author_name`, `author_role`, `content_type`, `content_parts`, `status`, `channel`, `weight`, `end_turn` | `role`, `content` |
| Metadata columns | `default_model_slug`, `parent_id` | `message_source`, `serialization_metadata` |
| Settings PK | `INTEGER PRIMARY KEY AUTOINCREMENT` + `key UNIQUE` | `key TEXT PRIMARY KEY` |
| Indexes | Yes (4 indexes defined) | None |

`schema.sql` is never executed by the application -- the app creates tables inline in `init_db()`. The schema file is dead documentation that will mislead anyone reading it.

**Fix:** Delete the inline DDL, make `init_db()` execute `schema.sql`, and reconcile the two schemas into one source of truth.

### 2.2 No Indexes (MEDIUM-HIGH)

The runtime DDL creates zero indexes. With 3840 conversations and potentially hundreds of thousands of messages, every query that joins or filters on `conversation_id`, `parent_id`, or children relationships does a full table scan.

**Fix:** Add at minimum:
```sql
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);
CREATE INDEX IF NOT EXISTS idx_message_children_parent_id ON message_children(parent_id);
CREATE INDEX IF NOT EXISTS idx_message_children_child_id ON message_children(child_id);
```

### 2.3 Connection-Per-Call With No Pooling or Context Manager

Every `get_db()` call opens a new SQLite connection and the caller is responsible for closing it. If any code path raises before `conn.close()`, the connection leaks. Flask's `g` object exists specifically for this:

```python
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('chatgpt.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### 2.4 `get_setting()` Opens and Closes a Connection Per Setting

The `index()` route calls `get_setting()` 4 times, each opening a fresh connection. The `conversation()` route calls it 6+ times. This is brutally wasteful. Either batch settings into one query or use the `g`-based connection.

### 2.5 `import_conversations_data` Runs All Inserts in a Single Giant Transaction

For 3840 conversations with ~100k+ messages, SQLite accumulates the entire WAL before committing. If the process is killed mid-import, nothing is saved. Consider committing in batches (every 100 conversations).

### 2.6 Foreign Keys Are Declared but Never Enforced

SQLite requires `PRAGMA foreign_keys = ON` per connection to enforce FK constraints. This pragma is never set. The FK declarations are purely decorative.

### 2.7 Hardcoded Database Path

```python
conn = sqlite3.connect('chatgpt.db')  # line 32
```

This is relative to CWD, not to the application directory. Running `python app.py` from a different directory creates/opens a different database. Use `os.path.dirname(__file__)` or an env var.

---

## 3. Architecture & Code Quality

### 3.1 Monolithic Single File

All routes, DB logic, template filters, import logic, and settings management live in one 496-line `app.py`. This makes testing, extension, and reasoning about the code harder than necessary. Consider splitting into:
- `models.py` or `db.py` -- DB access, settings
- `filters.py` -- Jinja template filters
- `routes/` -- route modules
- `ingest.py` -- import logic

### 3.2 Bare `except:` Clauses

```python
@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value)
    except:        # <-- catches SystemExit, KeyboardInterrupt, everything
        return []
```

Same pattern in `tojson`. Use `except (ValueError, TypeError):` at minimum.

### 3.3 N+1 Query in Nice Conversation View (Canonical Path)

```python
while current_id:
    message = conn.execute('...WHERE m.id = ?', (current_id,)).fetchone()
    ...
    current_id = message['parent_id']
```

This walks the tree one row at a time, issuing a separate SQL query per message. For a 200-message conversation, that's 200 round-trips. A recursive CTE would be O(1) queries:

```sql
WITH RECURSIVE path AS (
    SELECT * FROM messages WHERE id = :endpoint_id
    UNION ALL
    SELECT m.* FROM messages m JOIN path p ON m.id = p.parent_id
)
SELECT * FROM path;
```

**IMPORTANT -- DO NOT constrain the path walk by `conversation_id`.** ChatGPT "Branch" conversations share parent message IDs with their source conversation. The walk from leaf to root naturally crosses conversation boundaries to include the inherited context, and this is **correct by design**. Verified that branched conversations produce a clean transition: parent conversation messages form a contiguous block at the root side, current conversation messages at the leaf side. Example: "Dallas Storm Ice Prediction" path=337 (120 from this conversation + 217 inherited from its branch) -- this is the full conversation as the user experienced it.

### 3.3a Canonical Path Info Box Label Is Misleading (LOW -- cosmetic)

The nice view shows `Canonical Path: 337 messages (127 total)` where 337 is the full path (correct) and 127 is `COUNT(*) WHERE conversation_id = ?` (only messages belonging directly to this conversation record). For branched conversations, this looks paradoxical (path > total). The label should be clarified, e.g. "337 messages in thread (127 in this branch)" or just drop the total count.

### 3.4 Duplicate Metadata Extraction Logic

The dict-building code that pops `message_type`, `model_slug`, etc. into a `metadata` sub-dict is copy-pasted identically in `conversation()` (lines 208-224) and `nice_conversation()` (lines 280-293). Extract to a helper function.

### 3.5 `init_db.py` Deletes the Entire Database

```python
if os.path.exists('chatgpt.db'):
    os.remove('chatgpt.db')
```

Running `init_db.py` nukes all data with no confirmation prompt. This is a data-loss footgun. At minimum add a `--force` flag or a "are you sure?" prompt.

### 3.6 `run_ingest.py` Does `os.chdir()` at Module Level

```python
os.chdir(os.path.dirname(os.path.abspath(__file__)))
```

This is a side-effect at import time that affects the entire process. If `run_ingest` were ever imported by another module, it would silently change the working directory. Prefer configuring paths explicitly.

---

## 4. Performance

### 4.1 Home Page Renders All 3840 Conversations at Once

There is zero pagination. The server fetches every row from `conversations`, renders 3840 Bootstrap cards, and sends a ~900KB HTML document. The browser has to parse and lay out 3840 DOM nodes. This is the single biggest performance problem in the app.

**Fix:** Add server-side pagination (`LIMIT/OFFSET` or cursor-based) or at least client-side virtual scrolling.

### 4.2 Full Conversation View Fetches Every Message

The dev/full view does `SELECT ... WHERE conversation_id = ? ORDER BY create_time` with no limit. Conversations with thousands of messages will produce enormous HTML responses.

### 4.3 No Caching of Any Kind

Settings are re-read from SQLite on every single request. Static assets have no cache headers. There's no ETag, no `Last-Modified`, no `Cache-Control`.

### 4.4 JSON Serialisation in Templates

Every message's `content` column stores a JSON string. The template parses it with `|fromjson`, renders it, and discards the result. If the same conversation is viewed 10 times, the same JSON is parsed 10 times. Consider parsing in the route and passing structured data to the template.

---

## 5. Testing

### 5.1 Zero Actual Tests

The `tests/` directory contains `conftest.py` with fixtures but no test files. There is literally zero test coverage.

### 5.2 Broken Test Fixtures

```python
original_get_db = app.get_db   # conftest.py line 29
```

`app` is the Flask application object. It does not have a `get_db` attribute -- `get_db` is a module-level function. This fixture will crash with `AttributeError` if any test tries to use it.

### 5.3 Sample Export Fixture Doesn't Match Import Code

The `sample_chatgpt_export` fixture wraps conversations in `{"conversations": [...]}`, but `import_conversations_data()` expects a bare list of conversation dicts. The fixture would fail on import.

---

## 6. Content Rendering & Data Handling

### 6.0 Overview

Analysis of all 182,043 messages in the database reveals that the rendering layer only handles one of the ~7 content types in ChatGPT exports. The template assumes every `parts` element is either a string (render as markdown) or a dict (dump as JSON). This produces broken output for the majority of conversations.

### 6.1 No Content-Type Dispatch (HIGH)

The template does:
```html
{% if part is string %}
    {{ part|markdown|safe }}
{% else %}
    <pre><code>{{ part|tojson(indent=2) }}</code></pre>
{% endif %}
```

This handles strings fine but dumps ALL dict-type parts as raw JSON. The data contains at least 6 distinct dict `content_type` values that need specific handling:

| `content_type` | Count | What It Is | Current Rendering |
|---|---|---|---|
| `image_asset_pointer` | 3,207 | User images / DALL-E output | Giant JSON blob |
| `audio_transcription` | ~745 | Voice mode text (has `.text` field) | JSON blob (text is INSIDE) |
| `audio_asset_pointer` | ~745 | Audio binary reference | JSON blob |
| `real_time_user_audio_video_asset_pointer` | ~746 | Video/screenshare reference | JSON blob |
| Other structured content | various | Tool results, search refs | JSON blob |

### 6.2 Tool Messages Display as User Messages (HIGH)

22,235 messages have `role = "tool"`. The template labels everything non-assistant as the user's name:
```html
{{ assistant_name if message.role == 'assistant' else user_name }}
```

Tool responses (reminder confirmations, search results, code interpreter output) show as "Rizzn" said them.

### 6.3 System Messages Not Filtered in Nice Mode (MEDIUM)

18,776 system messages exist, 100% with empty content. They render as blank "Rizzn None" bubbles. The Nice Mode filter `{%- if content and content|length > 0 -%}` catches `[]` but not `[""]` (array with one empty string), so some leak through.

### 6.4 Empty Content Suppression Is Incomplete (MEDIUM)

Breakdown of empty-content messages by role:
- system: 18,776/18,776 (100%)
- tool: 15,657/22,235 (70.4%)
- assistant: 21,760/82,444 (26.4%)
- user: 2,454/58,588 (4.2%)

Every single conversation in the top 50 has empty nodes in its canonical path. The filter misses `[""]`, `[null]`, and `["", "some text"]` (where the empty part still renders).

### 6.5 Web Search / Citation References Render as Garbage (MEDIUM)

Assistant messages using web search contain inline reference markers (`turn0news1`, `turn0news7`) and `navlist` structures that render as raw text with broken unicode glyphs instead of being parsed into footnote-style citations.

---

## 7. Dark Mode / Theme Issues

### 6.1 CSS Class Mismatch

The `nice_conversation.html` and `conversation.html` inline styles target `.dark-mode` but the body class applied by `base.html` is `dark` (no `-mode` suffix):

```html
<body {% if dark_mode %}class="dark"{% endif %}>
```

```css
/* In conversation.html */
.dark-mode .message { ... }   /* NEVER MATCHES */
```

This means the inline dark-mode overrides for message backgrounds, metadata, etc. in both conversation templates are dead CSS. Dark mode "works" only because `style.css` uses `body.dark` correctly for the global variables, but the template-level refinements (e.g. metadata pre/code backgrounds) never apply.

### 6.2 Nice Conversation Info Box Ignores CSS Variables

The info box in `nice_conversation.html` hardcodes:
```css
.info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; }
```

In dark mode it renders as a bright white rectangle on a dark background (visible in screenshots).

---

## 8. Miscellaneous

### 8.1 `schema.sql` vs Reality

As noted in 2.1, `schema.sql` is completely out of sync and is misleading dead code.

### 8.2 `datetime` Filter Uses Naive Local Time

```python
datetime.fromtimestamp(timestamp).strftime(...)
```

This uses the server's local timezone with no indication to the user. Consider using UTC and displaying with timezone info, or at least documenting the behavior.

### 8.3 No Back/Home Button in Conversation Views

Once inside a conversation, the only way back is clicking "ChatGPT Browser" in the navbar. There's no breadcrumb, no "Back to list" button.

### 8.4 Bootstrap 5.1.3 CDN Link Is Old

The app loads Bootstrap 5.1.3 from a CDN. Current stable is 5.3.x. The older version lacks some dark-mode utilities and accessibility fixes.

### 8.5 No Favicon

The browser shows a generic icon / 404 for `/favicon.ico` on every page load.

### 8.6 `update_time` Sorted as String

```sql
ORDER BY update_time DESC
```

`update_time` is stored as `TEXT` in the runtime schema. String sorting of epoch floats like `"1706900430.0"` vs `"1680900430.0"` happens to work because the strings are the same length, but this is fragile and technically incorrect. Store as `REAL` or `INTEGER`.

---

## Summary Table

| # | Issue | Severity | Effort |
|---|---|---|---|
| 1.1 | Random secret key per restart | HIGH | Trivial |
| 1.2 | Markdown XSS | HIGH | Small |
| 1.3 | Shared markdown instance state bleed | MEDIUM | Trivial |
| 1.4 | No CSRF | MEDIUM | Small |
| 1.5 | File upload field name mismatch (`json_file` vs `file`) | BUG | Trivial |
| 1.6 | No upload size limit | MEDIUM | Trivial |
| 1.7 | GET-based state mutation routes | MEDIUM | Small |
| 2.1 | Schema drift (`schema.sql` vs `init_db()`) | HIGH | Medium |
| 2.2 | No database indexes | MEDIUM-HIGH | Trivial |
| 2.3 | Connection-per-call, no cleanup on error | MEDIUM | Small |
| 2.4 | Multiple DB connections per request for settings | LOW-MEDIUM | Small |
| 2.5 | Giant single transaction on import | LOW-MEDIUM | Small |
| 2.6 | Foreign keys declared but unenforced | LOW | Trivial |
| 2.7 | Hardcoded relative DB path | LOW-MEDIUM | Trivial |
| 3.1 | Monolithic single file | LOW (tech debt) | Medium |
| 3.2 | Bare `except:` clauses | LOW | Trivial |
| 3.3 | N+1 query in canonical path (DO NOT add conversation_id constraint) | MEDIUM | Medium |
| 3.3a | Canonical path info box label misleading for branches | LOW | Trivial |
| 3.4 | Duplicated metadata extraction | LOW | Trivial |
| 3.5 | `init_db.py` deletes DB without confirmation | MEDIUM | Trivial |
| 3.6 | `os.chdir` at import time | LOW | Trivial |
| 4.1 | No pagination on home page (3840 cards) | HIGH | Medium |
| 4.2 | No message pagination in conversations | MEDIUM | Medium |
| 4.3 | No caching whatsoever | LOW-MEDIUM | Medium |
| 4.4 | JSON re-parsed in templates every render | LOW | Small |
| 5.1 | Zero tests | HIGH (quality) | Large |
| 5.2 | Broken test fixtures | MEDIUM | Small |
| 5.3 | Sample fixture doesn't match import format | LOW | Trivial |
| 6.0-6.1 | No content-type dispatch (images, audio, video all dump as JSON) | HIGH | Large |
| 6.2 | Tool messages display as user messages | HIGH | Small |
| 6.3 | System messages not filtered in Nice Mode | MEDIUM | Small |
| 6.4 | Empty content suppression is incomplete | MEDIUM | Small |
| 6.5 | Web search/citation references render as garbage | MEDIUM | Medium |
| 7.1 | `.dark-mode` vs `.dark` CSS class mismatch | MEDIUM | Trivial |
| 7.2 | Info box ignores CSS variables in dark mode | LOW | Trivial |
| 8.1 | `schema.sql` is dead/misleading | MEDIUM | Small |
| 8.2 | Naive local time in datetime display | LOW | Small |
| 8.3 | No back button in conversation views | LOW | Trivial |
| 8.4 | Old Bootstrap version | LOW | Trivial |
| 8.5 | No favicon | LOW | Trivial |
| 8.6 | `update_time` string-sorted epoch | LOW | Small |

---

## Recommended Priority Order

1. **Fix the file upload field name** (1.5) -- the web import is literally broken right now.
2. **Fix the XSS vector** (1.2) -- sanitise markdown output.
3. **Build a content-type-aware renderer** (6.0-6.1) -- this is the single biggest improvement. Images, audio transcripts, tool results, and search citations all need type-specific rendering instead of JSON dumps. Affects thousands of messages.
4. **Fix role display logic** (6.2) -- tool and system messages must not show as user. Add role-specific styling and filtering.
5. **Fix the secret key** (1.1) -- load from env or file.
6. **Add indexes** (2.2) -- instant query speedup for free.
7. **Add pagination to the home page** (4.1) -- currently unusable with 3840 entries.
8. **Fix empty content suppression** (6.4) -- filter `[""]`, `[null]`, and empty-string parts properly.
9. **Fix the dark-mode CSS class mismatch** (7.1, 7.2) -- visible UI bug.
10. **Fix the markdown state bleed** (1.3) -- add `md.reset()`.
11. **Use Flask `g` for DB connections** (2.3, 2.4).
12. **Reconcile or delete `schema.sql`** (2.1, 8.1).
13. **Write actual tests** (5.1, 5.2, 5.3).
14. Everything else.

**Protective note on canonical path:** The canonical path logic (walking `parent_id` to root without constraining by `conversation_id`) is correct and must be preserved. It correctly handles ChatGPT conversation branches by including inherited parent context. Any N+1 optimization (e.g. recursive CTE) must preserve this cross-conversation walk behavior.
