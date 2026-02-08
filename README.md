# ChatGPT Browser

A powerful Flask web application for browsing and analyzing ChatGPT conversation history. This tool allows you to import your ChatGPT conversation exports and view them in either a clean, focused mode or a detailed developer mode with full metadata.

## 🚀 Features

- **Dual View Modes**:
  - **Nice Mode**: Clean, distraction-free view showing only the canonical conversation path
  - **Dev Mode**: Full technical view with metadata, message IDs, and conversation branches

- **Theme Support**: Toggle between dark and light themes for comfortable viewing

- **Advanced Conversation Analysis**:
  - Automatic identification of canonical conversation paths
  - Message metadata inspection in developer mode
  - Timestamps and conversation structure visualization
  - Support for complex conversation trees and branching

- **Import Functionality**:
  - Import conversations from ChatGPT JSON export files
  - Maintains full conversation history and metadata
  - Handles conversation threading and parent-child relationships

- **Customization**:
  - Customizable user and assistant display names
  - Persistent settings across sessions
  - Session-based view mode overrides

## 📋 Prerequisites

Before installing ChatGPT Browser, ensure you have:

- **Python 3.8 or higher** (Python 3.11+ recommended)
- **Git** (for cloning the repository)
- **pip** (Python package installer)

### System Requirements

- **Minimum**: 2GB RAM, 1GB free disk space
- **Recommended**: 4GB RAM, 5GB free disk space (for large conversation databases)
- **Operating Systems**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)

## 🛠️ Installation

### Method 1: Clone and Install (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/actuallyrizzn/chatGPT-browser.git
   cd chatGPT-browser
   ```

2. **Create a virtual environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

### Method 2: Using pip (if published)

```bash
pip install chatgpt-browser
```

## 🚀 Quick Start

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Import your conversations**:
   - Go to **Settings** (gear icon)
   - Use the **Import JSON** section to upload your ChatGPT export file
   - Wait for the import to complete

4. **Browse your conversations**:
   - Click on any conversation to view it
   - Use **Nice Mode** for clean reading
   - Switch to **Dev Mode** for technical details
   - Toggle themes as needed

## 📖 Detailed Usage Guide

### Importing Conversations

1. **Export from ChatGPT**:
   - Go to ChatGPT settings
   - Click "Export data"
   - Download the JSON file

2. **Import to ChatGPT Browser**:
   - Navigate to Settings page
   - Click "Choose File" in the Import section
   - Select your exported JSON file
   - Click "Import Conversations"
   - Wait for processing to complete

### View Modes

#### Nice Mode (Default)
- **Purpose**: Clean, focused conversation reading
- **Features**:
  - Shows only the canonical conversation path
  - Distraction-free interface
  - Perfect for reviewing conversation flow
  - Markdown rendering for code and formatting

#### Dev Mode
- **Purpose**: Technical analysis and debugging
- **Features**:
  - Shows all messages and conversation branches
  - Displays message metadata and IDs
  - Technical timestamps and model information
  - Useful for understanding conversation structure

### Navigation

- **Conversation List**: View all imported conversations
- **Conversation View**: Read individual conversations
- **Settings**: Configure display options and import data
- **Theme Toggle**: Switch between dark and light themes

### Settings Configuration

- **User Name**: Customize how your messages are displayed
- **Assistant Name**: Customize how AI responses are displayed
- **View Mode**: Set default viewing mode (Nice/Dev)
- **Verbose Mode**: Show additional technical details in Dev mode
- **Dark Mode**: Enable/disable dark theme

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root for custom configuration:

```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_PATH=./chatgpt.db
SECRET_KEY=your-secret-key-here
```

### Database Configuration

The application uses SQLite by default. For production use, you can modify the database connection in `app.py`:

```python
# For PostgreSQL
import psycopg2
conn = psycopg2.connect("postgresql://user:password@localhost/dbname")

# For MySQL
import mysql.connector
conn = mysql.connector.connect(host="localhost", user="user", password="password", database="dbname")
```

## 🐛 Troubleshooting

### Common Issues

#### Import Fails
**Problem**: "Import failed" or "Invalid file format"
**Solution**:
- Ensure you're using the correct ChatGPT export format
- Check that the JSON file is not corrupted
- Verify the file size is reasonable (< 1GB)

#### Database Errors
**Problem**: "Database locked" or "Permission denied"
**Solution**:
- Ensure the application has write permissions to the directory
- Close any other applications that might be accessing the database
- Restart the application

#### Performance Issues
**Problem**: Slow loading or high memory usage
**Solution**:
- Consider splitting large conversation exports
- Increase system RAM if available
- Use Nice Mode for better performance

#### Port Already in Use
**Problem**: "Address already in use" error
**Solution**:
```bash
# Find and kill the process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Set environment variable
export FLASK_DEBUG=1

# Or modify app.py
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📁 Project Structure

```
chatGPT-browser/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── schema.sql            # Database schema definition
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Conversation list page
│   ├── conversation.html # Dev mode conversation view
│   ├── nice_conversation.html # Nice mode conversation view
│   └── settings.html     # Settings and import page
├── static/               # Static assets
│   └── style.css         # Application styles
├── docs/                 # Documentation
│   ├── README.md         # Documentation overview
│   ├── CODE_DOCUMENTATION.md # Technical documentation
│   ├── API_REFERENCE.md  # API endpoint reference
│   └── DATABASE_SCHEMA.md # Database design docs
└── diag-tools/           # Diagnostic tools (future use)
```

## 🔒 Security Considerations

- **Local Development**: The application runs locally by default
- **No Authentication**: Currently no user authentication implemented
- **File Upload**: Import files are processed locally
- **Database**: SQLite database stored locally

For production deployment, consider:
- Implementing user authentication
- Using HTTPS
- Setting up proper file upload validation
- Configuring database security

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Include type hints where appropriate

## 📄 License

**Dual licensing — conspicuous notice:**

- **Source code** (application and tests): Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](LICENSE) for the full text. You may use, modify, and distribute the code under the same license; if you run a modified version as a network service, you must offer the corresponding source to users.
- **Documentation and other non-code materials** (e.g. `docs/`, README text, screenshots): Licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)**. See [LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt) and [LICENSES/DOCUMENTATION](LICENSES/DOCUMENTATION). Summary: https://creativecommons.org/licenses/by-sa/4.0/

A short notice for both licenses is in [NOTICE](NOTICE). Details: [LICENSES/README.md](LICENSES/README.md).

## 📞 Support

### Getting Help

- **Documentation**: Check the [docs/](./docs/) directory for detailed documentation
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

### Useful Links

- [API Reference](./docs/API_REFERENCE.md)
- [Code Documentation](./docs/CODE_DOCUMENTATION.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🗺️ Roadmap

### Planned Features

- [ ] User authentication and multi-user support
- [ ] Conversation search and filtering
- [ ] Export functionality (PDF, Markdown)
- [ ] Conversation analytics and insights
- [ ] API endpoints for external integrations
- [ ] Mobile-responsive design improvements
- [ ] Real-time conversation updates
- [ ] Advanced conversation tree visualization

### Version History

- **v1.0.0**: Initial release with basic conversation browsing
- **v1.1.0**: Added dual view modes and theme support
- **v1.2.0**: Enhanced import functionality and metadata support

---

**Made with ❤️ for the ChatGPT community** 