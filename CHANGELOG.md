# Changelog

All notable changes to ChatGPT Browser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- Installation guide for multiple operating systems
- User guide with detailed usage instructions
- Contributing guidelines for developers
- API reference documentation
- Database schema documentation

### Changed
- Enhanced main README with better structure and information
- Improved project documentation organization
- Updated installation instructions for clarity

### Fixed
- Documentation links and cross-references
- Installation instructions for Windows users

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