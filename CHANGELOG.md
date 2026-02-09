# Changelog

All notable changes to ChatGPT Browser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (None)

### Changed
- (None)

### Fixed
- (None)

## [1.3.7] - 2026-02-08

### Changed
- **Canonical path label** (fixes #24): Info box now says "X messages in thread (Y in this branch)".
- **run_ingest CWD** (fixes #27): os.chdir moved into main() and default path uses BASE_DIR so import-time CWD is unchanged.

## [1.3.6] - 2026-02-08

### Added
- (None)

### Changed
- **Bootstrap** (fixes #45): CDN updated from 5.1.3 to 5.3.3 (CSS and JS).
- **Nice view** (fixes #37, #38): System messages and messages with no displayable content are excluded from the canonical path. Empty/whitespace-only parts are skipped when rendering. Datetime filter returns "—" for None or invalid timestamps (no more "None" in headers).

### Fixed
- Removed workflow cruft: deleted docs/gh-close-*.md, docs/gh-issue-*-comment.md, docs/gh-issue-*-close.md; removed committed docs/gh-issue-1-propose.md, docs/gh-issue-5-propose.md.

## [1.3.5] - 2026-02-08

### Added
- **Back to conversations** link (fixes #44) at top of conversation and nice_conversation views.

### Changed
- **Datetime filter** (fixes #43): timestamps now shown in UTC with " UTC" suffix (e.g. `2022-01-01 00:00 UTC`).

### Fixed
- **Nice view info box** (fixes #41): uses CSS variables `--card-bg` and `--border-color` so it follows dark mode.

## [1.3.4] - 2026-02-08

### Added
- **Favicon** (fixes #46): SVG favicon in `static/favicon.svg`, linked from `base.html`.

### Fixed
- **Dark mode CSS class** (fixes #40): Conversation template inline styles now use `body.dark` instead of `.dark-mode` so message and metadata dark styles apply.

## [1.3.3] - 2026-02-08

### Changed
- **Role-aware message labels** (fixes #36): Tool and system messages now show "Tool" and "System" instead of the user's name; user/assistant unchanged. Message div uses class by role (tool/system get muted styling).

## [1.3.2] - 2026-02-08

### Added
- **Home page pagination** (fixes #28): Index uses `page` and `per_page` query params (default 50 per page, max 100). Previous/Next and "Page X of Y" in template; `ORDER BY update_time DESC` with LIMIT/OFFSET.

## [1.3.1] - 2026-02-08

### Changed
- **Toggle routes use POST only** (fixes #13): `/toggle_dark_mode`, `/toggle_view_mode`, `/toggle_verbose_mode` now accept only POST; GET returns 405. Navbar dark mode uses a POST form; settings and conversation pages use `fetch(..., { method: 'POST' })` for toggles to avoid prefetch/crawler-triggered state changes.

## [1.3.0] - 2026-02-08

### Added
- **SECRET_KEY** config: load from `SECRET_KEY` env, else `.secret_key` file beside `app.py`, else random with warning (fixes #1, #7)
- **Markdown XSS sanitization**: bleach-based sanitization of markdown output; allowed tags/attrs whitelist (fixes #2, #8)
- **Per-call Markdown instance**: new `markdown.Markdown()` per filter call to avoid shared state bleed (fixes #3, #9)
- **Upload size limit**: `MAX_CONTENT_LENGTH` from env `MAX_UPLOAD_MB` (default 100 MB); 413 handler (fixes #6, #12)
- **Import form**: settings import accepts `file` or `json_file`; template uses `name="file"` (fixes #5, #11)
- Unit test for markdown XSS (script tags stripped)
- Dependency: `bleach==6.1.0` for HTML sanitization

### Changed
- Jinja filters `fromjson`/`tojson`: bare `except` replaced with explicit `(TypeError, ValueError, json.JSONDecodeError)` (fixes #22)

### Fixed
- (Security/behavior items listed under Added above)

## [1.2.0] - 2024-01-15

### Added
- **Dual View Modes**: Nice Mode and Dev Mode for different use cases
- **Theme Support**: Dark and light theme toggle
- **Enhanced Import**: Better handling of large conversation exports
- **Metadata Display**: Technical details in Dev Mode
- **Conversation Threading**: Support for complex conversation trees
- **Settings Persistence**: User preferences saved in database
- **Markdown Rendering**: Code blocks and formatting support

### Changed
- **UI Redesign**: Modern, responsive interface
- **Performance**: Optimized for large conversation databases
- **Database Schema**: Enhanced to support conversation threading
- **Import Process**: More robust error handling and validation

### Fixed
- **Database Locking**: Resolved concurrent access issues
- **Memory Usage**: Reduced memory consumption for large datasets
- **Import Errors**: Better handling of malformed JSON files
- **Display Issues**: Fixed conversation rendering problems

### Technical
- **Flask 3.0.2**: Updated to latest Flask version
- **SQLite Optimization**: Improved database performance
- **Error Handling**: Enhanced error reporting and logging
- **Code Quality**: Improved code structure and documentation

## [1.1.0] - 2023-12-01

### Added
- **Basic Import**: Support for ChatGPT JSON export files
- **Conversation List**: View all imported conversations
- **Simple Viewing**: Basic conversation display
- **Settings Page**: Basic configuration options
- **Database Storage**: SQLite database for conversation storage

### Changed
- **Initial Release**: Basic functionality for conversation browsing
- **Simple UI**: Clean, minimal interface
- **Local Storage**: All data stored locally

### Fixed
- **Initial Bugs**: Resolved basic functionality issues
- **Import Issues**: Fixed file upload and processing
- **Display Problems**: Corrected conversation rendering

## [1.0.0] - 2023-11-15

### Added
- **Initial Release**: First public release of ChatGPT Browser
- **Basic Flask Application**: Web interface for conversation browsing
- **SQLite Database**: Local data storage
- **Import Functionality**: Basic ChatGPT export import
- **Simple UI**: Basic conversation viewing interface

### Technical
- **Flask Framework**: Web application foundation
- **SQLite Database**: Local data persistence
- **Jinja2 Templates**: HTML templating system
- **Basic Styling**: CSS for interface appearance

---

## Version History Summary

### Major Versions

#### v1.0.0 (Initial Release)
- Basic conversation import and viewing
- Simple web interface
- Local SQLite storage

#### v1.1.0 (Feature Enhancement)
- Improved import functionality
- Better conversation display
- Settings and configuration options

#### v1.2.0 (Major Update)
- Dual view modes (Nice/Dev)
- Theme support (Dark/Light)
- Enhanced conversation threading
- Performance optimizations
- Modern UI redesign

#### Unreleased (Documentation)
- Comprehensive documentation suite
- Installation guides for all platforms
- User and developer guides
- API reference and technical docs

### Key Features by Version

| Version | Import | Viewing | Themes | Threading | Performance | Documentation |
|---------|--------|---------|--------|-----------|-------------|---------------|
| 1.0.0   | Basic  | Basic   | No     | No        | Basic       | Minimal       |
| 1.1.0   | Good   | Good    | No     | No        | Good        | Basic         |
| 1.2.0   | Great  | Dual    | Yes    | Yes       | Excellent   | Good          |
| Unreleased | Great | Dual | Yes | Yes | Excellent | Comprehensive |

### Breaking Changes

#### v1.2.0
- **Database Schema**: Updated schema for conversation threading
  - New tables: `message_children`, `message_metadata`
  - Modified: `conversations`, `messages` tables
  - Migration: Automatic migration for existing databases

#### v1.1.0
- **Settings Storage**: Moved from file-based to database storage
  - Migration: Automatic migration of existing settings

### Deprecation Notices

#### v1.2.0
- **File-based Settings**: Deprecated in favor of database storage
- **Simple View Mode**: Replaced by Nice/Dev mode system

### Security Updates

#### v1.2.0
- **Input Validation**: Enhanced validation for file uploads
- **SQL Injection**: Improved parameterized query usage
- **File Upload**: Better security for imported files

#### v1.1.0
- **Basic Security**: Initial security measures implemented
- **Input Sanitization**: Basic input validation

### Performance Improvements

#### v1.2.0
- **Database Indexing**: Added indexes for better query performance
- **Lazy Loading**: Implemented for large conversations
- **Memory Optimization**: Reduced memory usage for large datasets
- **Caching**: Added conversation caching

#### v1.1.0
- **Query Optimization**: Improved database queries
- **File Processing**: Better import performance

### Known Issues

#### v1.2.0
- **Large Files**: Very large exports (>500MB) may cause memory issues
- **Mobile UI**: Some interface elements need mobile optimization
- **Search**: Basic search functionality, advanced search planned

#### v1.1.0
- **Memory Usage**: High memory usage with large conversation databases
- **Import Speed**: Slow import for very large files
- **UI Responsiveness**: Interface may become unresponsive with large datasets

### Future Plans

#### Planned for v1.3.0
- **Advanced Search**: Full-text search across conversations
- **Export Functionality**: Export conversations in various formats
- **User Authentication**: Multi-user support
- **API Endpoints**: RESTful API for external integrations
- **Mobile App**: Native mobile application

#### Planned for v1.4.0
- **Conversation Analytics**: Insights and statistics
- **Real-time Updates**: Live conversation updates
- **Advanced Filtering**: Date, model, and content filtering
- **Backup/Restore**: Automated backup functionality

---

## Contributing to Changelog

When adding new entries to this changelog:

1. **Use the correct format**: Follow the established structure
2. **Be descriptive**: Explain what changed and why
3. **Include breaking changes**: Clearly mark any breaking changes
4. **Add technical details**: Include relevant technical information
5. **Update version history**: Keep the summary tables current

### Changelog Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes
- **Technical**: Technical improvements and updates

---

For more information about the project, see the [README](README.md) and [documentation](docs/).

- Main Repository: https://github.com/actuallyrizzn/chatGPT-browser 