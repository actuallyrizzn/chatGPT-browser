# Contributing to ChatGPT Browser

Thank you for your interest in contributing to ChatGPT Browser! This guide will help you get started with contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style and Standards](#code-style-and-standards)
4. [Testing](#testing)
5. [Submitting Changes](#submitting-changes)
6. [Issue Reporting](#issue-reporting)
7. [Feature Requests](#feature-requests)
8. [Documentation](#documentation)
9. [Code Review Process](#code-review-process)
10. [Release Process](#release-process)

## Getting Started

### Before You Begin

1. **Read the Documentation**
   - [README.md](README.md) - Project overview and user guide
   - [docs/CODE_DOCUMENTATION.md](docs/CODE_DOCUMENTATION.md) - Technical implementation details
   - [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - API endpoint documentation

2. **Check Existing Issues**
   - Look for existing issues that match your contribution
   - Comment on issues you plan to work on
   - Check if there are any related pull requests

3. **Join the Community**
   - Star the repository if you find it useful
   - Follow the project for updates
   - Participate in discussions

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix issues and improve stability
- **Feature Development**: Add new functionality
- **Documentation**: Improve guides and technical docs
- **Testing**: Add tests and improve test coverage
- **Performance**: Optimize code and improve speed
- **UI/UX**: Enhance user interface and experience
- **Security**: Identify and fix security issues

## Development Setup

### Prerequisites

- **Python 3.8+** (3.11+ recommended)
- **Git** for version control
- **pip** for package management
- **Virtual environment** (recommended)

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/actuallyrizzn/chatGPT-browser.git
   cd chatGPT-browser
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/actuallyrizzn/chatGPT-browser.git
   ```

3. **Create Development Environment**
   ```bash
   cd chatGPT-browser
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

5. **Install Development Tools**
   ```bash
   pip install pytest pytest-cov black flake8 mypy pre-commit
   ```

6. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

7. **Initialize Database**
   ```bash
   python init_db.py
   ```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make Your Changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   python -m pytest

   # Run with coverage
   python -m pytest --cov=app

   # Run code quality checks
   pre-commit run --all-files
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Submit for review

## Code Style and Standards

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

#### Formatting
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **String Quotes**: Double quotes for strings, single quotes for characters
- **Import Order**: Standard library, third-party, local imports

#### Naming Conventions
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Methods**: `_leading_underscore`

#### Code Examples

```python
# Good
def get_conversation_by_id(conversation_id: str) -> Optional[dict]:
    """Retrieve a conversation by its ID.
    
    Args:
        conversation_id: The unique identifier of the conversation
        
    Returns:
        Conversation data or None if not found
    """
    try:
        conn = get_db()
        conversation = conn.execute(
            'SELECT * FROM conversations WHERE id = ?', 
            (conversation_id,)
        ).fetchone()
        return dict(conversation) if conversation else None
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {e}")
        return None
    finally:
        conn.close()

# Bad
def getConv(id):
    conn = get_db()
    c = conn.execute('SELECT * FROM conversations WHERE id = ?', (id,)).fetchone()
    return c
```

### Documentation Standards

#### Docstrings
Use Google-style docstrings for all public functions and classes:

```python
def import_conversations(file_path: str) -> dict:
    """Import conversations from a ChatGPT export file.
    
    Args:
        file_path: Path to the JSON export file
        
    Returns:
        Dictionary with import results:
            - success: Boolean indicating success
            - imported_count: Number of conversations imported
            - errors: List of error messages
            
    Raises:
        FileNotFoundError: If the file doesn't exist
        JSONDecodeError: If the file is not valid JSON
    """
    pass
```

#### Comments
- Write clear, concise comments
- Explain "why" not "what"
- Use comments for complex logic
- Keep comments up to date

### Database Standards

#### SQL Style
- Use UPPERCASE for SQL keywords
- Use snake_case for table and column names
- Include proper indentation
- Use parameterized queries to prevent SQL injection

```sql
-- Good
SELECT 
    c.id,
    c.title,
    c.create_time,
    COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.update_time > ?
GROUP BY c.id
ORDER BY c.update_time DESC;

-- Bad
select c.id,c.title,c.create_time,count(m.id) as message_count from conversations c left join messages m on c.id=m.conversation_id where c.update_time>? group by c.id order by c.update_time desc;
```

#### Database Operations
- Always use transactions for multiple operations
- Handle database errors gracefully
- Close connections properly
- Use appropriate indexes for performance

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_app.py             # Main application tests
├── test_database.py        # Database operation tests
├── test_import.py          # Import functionality tests
├── test_api.py             # API endpoint tests
└── test_templates.py       # Template rendering tests
```

### Writing Tests

#### Test Naming
- Use descriptive test names
- Follow the pattern: `test_<function>_<scenario>`
- Group related tests in classes

```python
class TestConversationImport:
    def test_import_valid_conversation_success(self):
        """Test successful import of valid conversation data."""
        pass
        
    def test_import_invalid_json_raises_error(self):
        """Test that invalid JSON raises appropriate error."""
        pass
        
    def test_import_empty_file_returns_empty_result(self):
        """Test that empty file returns empty import result."""
        pass
```

#### Test Coverage
- Aim for at least 80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions
- Mock external dependencies

#### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_app.py

# Run with verbose output
python -m pytest -v

# Run tests in parallel
python -m pytest -n auto
```

### Test Data

#### Fixtures
Use pytest fixtures for common test data:

```python
import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_conversation():
    """Provide sample conversation data for testing."""
    return {
        'id': 'test-conversation-123',
        'title': 'Test Conversation',
        'create_time': '1640995200.0',
        'update_time': '1640995800.0'
    }
```

## Submitting Changes

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples
```bash
feat: add conversation search functionality
fix: resolve database connection timeout issue
docs: update installation guide for Windows
style: format code with Black
refactor: extract database connection logic
test: add tests for import functionality
chore: update dependencies
```

### Pull Request Process

1. **Create Pull Request**
   - Use the provided PR template
   - Fill out all required sections
   - Link related issues

2. **PR Template Sections**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Other (please describe)

   ## Testing
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes
   - [ ] Self-review completed
   ```

3. **Review Process**
   - Address review comments
   - Make requested changes
   - Update PR description if needed
   - Request re-review when ready

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Clear Description**
   - What you expected to happen
   - What actually happened
   - Steps to reproduce

2. **Environment Information**
   - Operating system and version
   - Python version
   - Browser (if applicable)
   - Application version

3. **Error Details**
   - Full error message
   - Stack trace (if available)
   - Screenshots (if applicable)

4. **Additional Context**
   - When the issue started
   - Any recent changes
   - Workarounds tried

### Issue Template

```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: [e.g., Windows 11, macOS 12.1, Ubuntu 20.04]
- Python: [e.g., 3.11.0]
- Browser: [e.g., Chrome 96.0.4664.110]
- App Version: [e.g., 1.2.0]

## Error Details
[Error message and stack trace]

## Additional Information
[Any other relevant information]
```

## Feature Requests

### Before Submitting

1. **Check Existing Issues**
   - Search for similar feature requests
   - Check if the feature is already planned
   - Review existing discussions

2. **Consider Impact**
   - How many users would benefit?
   - Is it within the project scope?
   - What's the implementation complexity?

### Feature Request Template

```markdown
## Feature Description
[Clear description of the feature]

## Use Case
[Why this feature is needed]

## Proposed Solution
[How you think it should work]

## Alternatives Considered
[Other approaches you considered]

## Additional Information
[Any other relevant details]
```

## Documentation

### Documentation Standards

#### Writing Style
- Use clear, concise language
- Write for the target audience
- Include examples where helpful
- Keep content up to date

#### Documentation Types
- **User Documentation**: Installation, usage, troubleshooting
- **Developer Documentation**: API reference, code structure
- **Contributor Documentation**: Development setup, contribution guidelines

#### Documentation Structure
```
docs/
├── README.md                    # Documentation overview
├── INSTALLATION.md             # Installation guide
├── USER_GUIDE.md               # User manual
├── API_REFERENCE.md            # API documentation
├── CODE_DOCUMENTATION.md       # Technical documentation
└── DATABASE_SCHEMA.md          # Database documentation
```

### Updating Documentation

When making code changes:

1. **Update Related Docs**
   - API changes → Update API_REFERENCE.md
   - Database changes → Update DATABASE_SCHEMA.md
   - New features → Update USER_GUIDE.md

2. **Check Links**
   - Ensure internal links work
   - Update cross-references
   - Verify external links

3. **Review Content**
   - Check for accuracy
   - Update examples if needed
   - Ensure consistency

## Code Review Process

### Review Guidelines

#### For Contributors
- **Self-Review**: Review your own code before submitting
- **Test Thoroughly**: Ensure all tests pass
- **Document Changes**: Update documentation as needed
- **Respond Promptly**: Address review comments quickly

#### For Reviewers
- **Be Constructive**: Provide helpful, specific feedback
- **Check Quality**: Ensure code meets standards
- **Test Functionality**: Verify the changes work as expected
- **Consider Impact**: Assess the broader impact of changes

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Security considerations addressed
- [ ] Performance impact considered
- [ ] Error handling is appropriate

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Prepare Release**
   - Update version numbers
   - Update changelog
   - Create release branch

2. **Testing**
   - Run full test suite
   - Manual testing
   - Performance testing

3. **Documentation**
   - Update release notes
   - Update installation guide
   - Review all documentation

4. **Release**
   - Create GitHub release
   - Tag the release
   - Announce to community

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New conversation search feature
- Dark mode support
- Export functionality

### Changed
- Improved import performance
- Updated UI design

### Fixed
- Database connection timeout issue
- Memory leak in large conversations
```

## Getting Help

### Resources

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Search existing issues on GitHub
- **Discussions**: Join community discussions
- **Code**: Review the source code

### Contact

- **GitHub Issues**: [Report bugs and request features](https://github.com/actuallyrizzn/chatGPT-browser/issues)
- **Discussions**: [Community help and tips](https://github.com/actuallyrizzn/chatGPT-browser/discussions)
- **Email**: [Contact maintainers](mailto:maintainers@example.com)

### Community Guidelines

- **Be Respectful**: Treat others with respect and kindness
- **Be Helpful**: Help other contributors when possible
- **Be Patient**: Maintainers are volunteers
- **Be Constructive**: Provide helpful, specific feedback

---

Thank you for contributing to ChatGPT Browser! Your contributions help make the project better for everyone. 