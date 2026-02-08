# Issue coverage by category

Maps **CODE_AUDIT.md** and **UX_UI_REVIEW.md** to GitHub issues and area labels.

**Note:** Issues #1–#6 are older/duplicate security issues (same topics as #7–#12). The canonical audit set is **#7–#47** (41 issues). UX issues are **#48–#63** (16 issues).

---

## Audit sections → issues

| Audit section | Findings | Issue numbers |
|---------------|----------|---------------|
| **1. Security** | 1.1–1.7 | #7 (secret key), #8 (XSS), #9 (markdown state), #10 (CSRF), #11 (upload field), #12 (upload size), #13 (GET mutating) |
| **2. Database** | 2.1–2.7 | #14 (schema drift), #15 (indexes), #16 (connection leak), #17 (settings connections), #18 (giant tx), #19 (FK), #20 (db path), #42 (schema.sql dead), #47 (update_time) |
| **3. Architecture & code quality** | 3.1–3.6, 3.3a | #21 (monolithic), #22 (bare except), #23 (N+1), #24 (canonical label), #25 (duplicate metadata), #26 (init_db), #27 (os.chdir), #45 (Bootstrap) |
| **4. Performance** | 4.1–4.4 | #28 (home pagination), #29 (message pagination), #30 (caching), #31 (JSON in templates) |
| **5. Testing** | 5.1–5.3 | #32 (zero tests), #33 (broken fixtures), #34 (fixture format) |
| **6. Content rendering** | 6.0–6.5 | #35 (content-type), #36 (tool as user), #37 (system msgs), #38 (empty content), #39 (citations) |
| **7. Dark mode / theme** | 7.1–7.2 | #40 (CSS class), #41 (info box) |
| **8. Miscellaneous** | 8.1–8.6 | #42, #43 (datetime), #44 (back button), #45, #46 (favicon), #47 |

---

## Area labels → issue counts

| Area | Issues |
|------|--------|
| **area: security** | #7, #8, #9, #10, #11, #12, #13 |
| **area: database** | #14, #15, #16, #17, #18, #19, #20, #42, #47 |
| **area: architecture** | #21, #26, #27 |
| **area: code-quality** | #9, #21, #22, #25, #26, #27, #45 |
| **area: performance** | #15, #23, #28, #29, #30, #31 |
| **area: testing** | #32, #33, #34 |
| **area: rendering** | #35, #36, #37, #38, #39 |
| **area: ux** | #24, #28, #40, #41, #43, #44, #46, **#48–#63** (16 UX-specific) |

Every audit category and every area label has at least one issue.

---

## Scripts

- **`.gh-issues/create-issues.ps1`** — creates the 41 audit issues (run once; issues already exist).
- **`.gh-issues/create-ux-issues.ps1`** — creates the 16 UX issues (run once; issues already exist).

To add **area: architecture** when (re-)creating audit issues, ensure issues for monolithic app, init_db, and os.chdir include that label in the script.
