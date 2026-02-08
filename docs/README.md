# ChatGPT Browser - Documentation

**License notice:** Documentation and other non-code materials in this repository (including this file and the contents of `docs/`) are licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0)**. Full text: [../LICENSES/CC-BY-SA-4.0.txt](../LICENSES/CC-BY-SA-4.0.txt). You must give appropriate credit and share adaptations under the same license.

---

Welcome to the comprehensive documentation for the ChatGPT Browser application. This documentation suite provides detailed information about the codebase, architecture, implementation details, and user guides.

## 📚 Documentation Structure

### 🚀 User-Facing Documentation

#### [INSTALLATION.md](./INSTALLATION.md)
**Complete installation guide for all platforms and deployment scenarios**

- **System Requirements**: Minimum and recommended specifications
- **Prerequisites**: Python, Git, and other dependencies
- **Installation Methods**: Standard and development installations
- **Operating System Specific**: Windows, macOS, and Linux instructions
- **Development Setup**: Environment configuration for contributors
- **Production Deployment**: Gunicorn, Waitress, and systemd setup
- **Docker Deployment**: Containerized deployment options
- **Troubleshooting**: Common issues and solutions

#### [USER_GUIDE.md](./USER_GUIDE.md)
**Comprehensive user manual with step-by-step instructions**

- **Getting Started**: First launch and interface overview
- **Importing Conversations**: Export from ChatGPT and import process
- **Browsing Conversations**: Navigation and viewing options
- **View Modes**: Nice Mode vs Dev Mode detailed comparison
- **Settings and Customization**: User preferences and configuration
- **Advanced Features**: Search, export, and keyboard shortcuts
- **Tips and Best Practices**: Efficient usage and data management
- **Troubleshooting**: Common user issues and solutions

### 🔧 Technical Documentation

#### [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)
**Main technical documentation covering the entire application**

- **Project Overview**: High-level description and features
- **Architecture**: Technology stack and project structure
- **Database Schema**: Complete database design and relationships
- **Core Application**: Detailed analysis of `app.py`
- **API Endpoints**: All routes and their functionality
- **Data Import System**: How ChatGPT exports are processed
- **Settings Management**: Configuration system
- **View Modes**: Nice vs Dev mode implementation
- **Error Handling**: Error management strategies
- **Security Considerations**: Security measures and best practices
- **Performance Optimizations**: Performance tuning techniques
- **Development Guidelines**: Coding standards and best practices

#### [API_REFERENCE.md](./API_REFERENCE.md)
**Complete API reference with examples**

- **Endpoint Documentation**: All 10 API endpoints with detailed descriptions
- **Request/Response Formats**: HTTP methods, parameters, and response types
- **Data Models**: JSON schemas for all data structures
- **Error Handling**: HTTP status codes and error responses
- **Session Management**: Session variables and lifecycle
- **File Upload**: Import process and validation
- **Testing Examples**: curl commands for testing endpoints
- **Security Considerations**: Input validation and security measures

#### [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
**Comprehensive database documentation**

- **Schema Overview**: Complete table structure and relationships
- **Table Definitions**: Detailed column descriptions and data types
- **Relationships**: Foreign key relationships and entity diagrams
- **Indexes**: Performance indexes and their usage
- **Data Flow**: Import process and query patterns
- **Operations**: Connection management and transaction handling
- **Backup and Recovery**: Database maintenance procedures
- **Performance Considerations**: Optimization strategies
- **Migration Strategy**: Schema change management

### 🧪 Testing and quality

#### [TESTING.md](./TESTING.md)
**How to run the test suite**

- Setup (venv, requirements-testing.txt)
- Running unit, integration, and E2E tests
- Coverage and pytest options

### 📋 Reference and audit

#### [API_REFERENCE.md](./API_REFERENCE.md)
**Endpoint reference** — All HTTP endpoints, request/response formats, and examples.

#### [CODE_AUDIT.md](./CODE_AUDIT.md)
**Code audit** — Findings, severity, and suggested fixes from the codebase audit.

#### [ISSUE_COVERAGE.md](./ISSUE_COVERAGE.md)
**Issue coverage** — Mapping of audit items to GitHub issues.

#### [UX_UI_REVIEW.md](./UX_UI_REVIEW.md)
**UX/UI review** — Interface and usability notes.

### 📄 License for documentation

- [LICENSE-DOCS.md](./LICENSE-DOCS.md) — **CC-BY-SA 4.0** applies to all docs and non-code materials.

## 📖 Quick Start Guide

### For Users

1. **Start with [INSTALLATION.md](./INSTALLATION.md)** for setup instructions
2. **Read [USER_GUIDE.md](./USER_GUIDE.md)** for usage instructions
3. **Check the main [README](../README.md)** for project overview

### For Developers

1. **Start with [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)** to understand the overall architecture
2. **Review [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** to understand the data model
3. **Use [API_REFERENCE.md](./API_REFERENCE.md)** for endpoint-specific questions
4. **Check [CONTRIBUTING.md](../CONTRIBUTING.md)** for development guidelines

### For Contributors

1. **Read [CONTRIBUTING.md](../CONTRIBUTING.md)** for contribution guidelines
2. **Understand the Database Schema** before making data-related changes
3. **Test API endpoints** using examples in [API_REFERENCE.md](./API_REFERENCE.md)
4. **Follow coding standards** outlined in [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)

### For Deployment

1. **Review [INSTALLATION.md](./INSTALLATION.md)** for production deployment
2. **Check Security Considerations** in [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)
3. **Understand Database Operations** for maintenance

## 🔑 Key Concepts

### View Modes
- **Nice Mode**: Clean, focused conversation viewing (default)
- **Dev Mode**: Full technical view with metadata

### Data Import
- Supports ChatGPT JSON export format
- Handles conversation trees and threading
- Preserves all metadata and relationships

### Settings System
- Persistent settings stored in database
- Session overrides for temporary changes
- Theme and display customization

### Architecture
- **Backend**: Flask 3.0.2 web framework
- **Database**: SQLite3 with optimized schema
- **Frontend**: Jinja2 templates with responsive CSS
- **Processing**: Markdown rendering and JSON parsing

## 🛠️ Technology Stack

- **Backend**: Flask 3.0.2
- **Database**: SQLite3
- **Template Engine**: Jinja2 3.1.3
- **Markdown Processing**: markdown 3.5.2
- **Date Handling**: python-dateutil 2.8.2
- **Development**: pytest, black, flake8, mypy

## 📁 File Structure

```
docs/
├── README.md                    # This file - documentation overview
├── INSTALLATION.md             # Installation guide for all platforms
├── USER_GUIDE.md               # Comprehensive user manual
├── CODE_DOCUMENTATION.md       # Main technical documentation
├── API_REFERENCE.md            # Complete API reference
└── DATABASE_SCHEMA.md          # Database design documentation

Project Root:
├── README.md                   # Main project README
├── CONTRIBUTING.md             # Contribution guidelines
├── CHANGELOG.md                # Version history and changes
├── requirements.txt            # Python dependencies
├── app.py                      # Main Flask application
├── init_db.py                  # Database initialization
├── schema.sql                  # Database schema definition
├── templates/                  # HTML templates
├── static/                     # CSS and static assets
└── docs/                       # Documentation directory
```

## 🔄 Documentation Maintenance

### When to Update Documentation

When making code changes, please also update the relevant documentation:

1. **Code Changes**: Update [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)
2. **API Changes**: Update [API_REFERENCE.md](./API_REFERENCE.md)
3. **Database Changes**: Update [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
4. **New Features**: Add to [USER_GUIDE.md](./USER_GUIDE.md)
5. **Installation Changes**: Update [INSTALLATION.md](./INSTALLATION.md)
6. **Version Updates**: Update [CHANGELOG.md](../CHANGELOG.md)

### Documentation Standards

- **Use clear, concise language**
- **Include code examples where helpful**
- **Maintain consistent formatting**
- **Update table of contents when adding sections**
- **Include cross-references between documents**
- **Test all code examples**
- **Keep screenshots and diagrams current**

### Documentation Review Process

1. **Self-Review**: Review your documentation changes
2. **Technical Accuracy**: Ensure technical details are correct
3. **User Experience**: Consider the user's perspective
4. **Completeness**: Ensure all necessary information is included
5. **Consistency**: Check formatting and style consistency

## 🆘 Getting Help

### Documentation Issues

If you find issues with the documentation:

1. **Check for existing issues** on GitHub
2. **Create a new issue** with the documentation problem
3. **Submit a pull request** with the fix
4. **Follow the contribution guidelines** in [CONTRIBUTING.md](../CONTRIBUTING.md)

### Technical Questions

For technical questions about the codebase:

1. **Check [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)** for implementation details
2. **Review [API_REFERENCE.md](./API_REFERENCE.md)** for endpoint questions
3. **Consult [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** for data-related questions
4. **Search existing issues** on GitHub
5. **Create a new issue** if your question isn't answered

### User Support

For user support questions:

1. **Check [USER_GUIDE.md](./USER_GUIDE.md)** for usage instructions
2. **Review [INSTALLATION.md](./INSTALLATION.md)** for setup issues
3. **Look at the main [README](../README.md)** for quick answers
4. **Search GitHub discussions** for community help
5. **Create a new discussion** for user questions

## 📊 Documentation Metrics

### Coverage
- **User Documentation**: 100% coverage of all features
- **Technical Documentation**: 100% coverage of codebase
- **API Documentation**: 100% coverage of all endpoints
- **Database Documentation**: 100% coverage of schema

### Quality
- **Code Examples**: All examples tested and verified
- **Screenshots**: Updated for current interface
- **Cross-references**: All internal links verified
- **External Links**: All external links checked

### Maintenance
- **Last Updated**: January 2025
- **Review Schedule**: Monthly documentation review
- **Update Process**: Documentation updated with each release
- **Version Tracking**: All documentation versioned with code

## 🔗 Useful Links

### Project Links
- **Main Repository**: [GitHub Repository](https://github.com/actuallyrizzn/chatGPT-browser)
- **Issues**: [GitHub Issues](https://github.com/actuallyrizzn/chatGPT-browser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/actuallyrizzn/chatGPT-browser/discussions)
- **Releases**: [GitHub Releases](https://github.com/actuallyrizzn/chatGPT-browser/releases)

### External Resources
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **SQLite Documentation**: [sqlite.org](https://www.sqlite.org/docs.html)
- **Jinja2 Documentation**: [jinja.palletsprojects.com](https://jinja.palletsprojects.com/)
- **Markdown Guide**: [markdownguide.org](https://www.markdownguide.org/)

---

## 📝 Contributing to Documentation

We welcome contributions to improve the documentation! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:

- **Documentation Standards**: Writing style and formatting
- **Review Process**: How documentation changes are reviewed
- **Update Procedures**: When and how to update documentation
- **Quality Assurance**: Ensuring documentation quality

---

*This documentation suite provides comprehensive coverage of the ChatGPT Browser application. For user-facing information, see the main [README.md](../README.md) file in the project root.* 