# User Guide

Welcome to the ChatGPT Browser User Guide! This comprehensive guide will help you get the most out of the application, from initial setup to advanced features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Importing Conversations](#importing-conversations)
3. [Browsing Conversations](#browsing-conversations)
4. [View Modes](#view-modes)
5. [Settings and Customization](#settings-and-customization)
6. [Advanced Features](#advanced-features)
7. [Tips and Best Practices](#tips-and-best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch

1. **Start the Application**
   ```bash
   python app.py
   ```

2. **Open Your Browser**
   Navigate to `http://localhost:5000`

3. **Initial Setup**
   - You'll see an empty conversation list
   - Click the **Settings** icon (gear) in the top navigation
   - Configure your preferences (optional)
   - Import your first conversation

### Understanding the Interface

#### Navigation Bar
- **Home Icon**: Return to conversation list
- **Settings Icon**: Access settings and import functions
- **Theme Toggle**: Switch between dark and light themes
- **View Mode Toggle**: Switch between Nice and Dev modes

#### Main Areas
- **Conversation List**: Shows all imported conversations
- **Conversation View**: Displays individual conversations
- **Settings Panel**: Configuration and import options

## Importing Conversations

### Step 1: Export from ChatGPT

1. **Access ChatGPT Settings**
   - Log into ChatGPT at [chat.openai.com](https://chat.openai.com)
   - Click your profile picture in the bottom left
   - Select "Settings"

2. **Request Data Export**
   - Click "Data controls" in the left sidebar
   - Click "Export data"
   - Choose "Chat history" option
   - Click "Confirm export"

3. **Download Your Data**
   - Wait for the export to complete (may take several minutes)
   - Download the ZIP file when ready
   - Extract the ZIP file to access your data

### Step 2: Import to ChatGPT Browser

1. **Navigate to Settings**
   - Click the settings icon in the navigation bar
   - Scroll to the "Import Conversations" section

2. **Select Your Export File**
   - Click "Choose File"
   - Navigate to your extracted ChatGPT data
   - Select the `conversations.json` file
   - Click "Open"

3. **Start Import**
   - Click "Import Conversations"
   - Wait for the import to complete
   - You'll see a success message when done

### Import Options

#### File Types Supported
- **Primary**: `conversations.json` (ChatGPT export format)
- **Alternative**: Any JSON file with ChatGPT conversation structure

#### Import Behavior
- **Incremental**: New conversations are added, existing ones are updated
- **Metadata Preserved**: All conversation metadata is maintained
- **Threading**: Parent-child relationships are preserved

### Import Troubleshooting

#### Common Issues
- **File Too Large**: Split large exports or increase system memory
- **Invalid Format**: Ensure you're using the correct ChatGPT export
- **Import Fails**: Check file permissions and disk space

#### Best Practices
- **Backup First**: Keep your original export files
- **Test Small**: Import a few conversations first
- **Monitor Progress**: Large imports may take several minutes

## Browsing Conversations

### Conversation List

#### Viewing Options
- **Chronological**: Conversations sorted by last update time
- **Title Display**: Shows conversation titles or first message
- **Quick Access**: Click any conversation to open it

#### List Features
- **Search**: Use browser search (Ctrl+F) to find conversations
- **Sorting**: Automatically sorted by most recent first
- **Pagination**: Handles large numbers of conversations efficiently

### Conversation View

#### Navigation
- **Back Button**: Return to conversation list
- **View Mode Toggle**: Switch between Nice and Dev modes
- **Theme Toggle**: Change appearance theme

#### Reading Experience
- **Message Flow**: Clear user/assistant message distinction
- **Markdown Support**: Code blocks, formatting, and links rendered
- **Timestamps**: Message creation times displayed
- **Responsive Design**: Works on desktop and mobile devices

## View Modes

### Nice Mode (Default)

#### Purpose
Clean, distraction-free conversation reading optimized for content consumption.

#### Features
- **Canonical Path**: Shows only the main conversation thread
- **Clean Interface**: Minimal visual clutter
- **Focus on Content**: Emphasizes message content over metadata
- **Fast Loading**: Optimized for performance

#### When to Use
- **Reading Conversations**: General conversation review
- **Content Analysis**: Studying AI responses and explanations
- **Quick Reference**: Finding specific information
- **Mobile Browsing**: Better performance on mobile devices

#### Interface Elements
- **User Messages**: Clearly labeled with your name
- **Assistant Messages**: Marked with assistant name
- **Code Blocks**: Syntax-highlighted and properly formatted
- **Links**: Clickable URLs and references

### Dev Mode

#### Purpose
Technical analysis and debugging with full metadata and conversation structure.

#### Features
- **Complete Data**: Shows all messages and conversation branches
- **Metadata Display**: Technical details for each message
- **Message IDs**: Unique identifiers for debugging
- **Timestamps**: Precise creation and update times
- **Model Information**: AI model used for each response

#### When to Use
- **Debugging**: Troubleshooting conversation issues
- **Development**: Understanding conversation structure
- **Analysis**: Studying AI model behavior
- **Technical Review**: Examining metadata and timestamps

#### Interface Elements
- **Message Metadata**: Expandable technical details
- **Conversation Tree**: Visual representation of message relationships
- **Model Information**: AI model and version details
- **Request IDs**: Unique request identifiers
- **Completion Status**: Whether responses are complete

### Switching Between Modes

#### Global Toggle
- **Settings**: Change default mode for all conversations
- **Navigation Bar**: Quick toggle button
- **Session Override**: Temporary mode change for current session

#### Per-Conversation Override
- **URL Parameter**: Add `/full` to conversation URL for dev mode
- **Session Storage**: Remembers mode preference per conversation
- **Automatic Reset**: Returns to default mode on page refresh

## Settings and Customization

### Accessing Settings

1. **Navigation**: Click the settings icon in the top bar
2. **Direct URL**: Navigate to `/settings`
3. **Keyboard Shortcut**: Press `S` key (if implemented)

### User Preferences

#### Display Names
- **User Name**: How your messages are displayed
  - Default: "User"
  - Custom: Any name you prefer
  - Examples: "John", "Developer", "Student"

- **Assistant Name**: How AI responses are displayed
  - Default: "Assistant"
  - Custom: Any name you prefer
  - Examples: "AI", "ChatGPT", "Claude"

#### View Mode Preferences
- **Default Mode**: Choose between Nice and Dev modes
- **Session Override**: Allow temporary mode changes
- **Auto-switch**: Automatically switch modes based on context

#### Theme Settings
- **Dark Mode**: Dark background with light text
  - Better for low-light environments
  - Reduces eye strain
  - Modern appearance

- **Light Mode**: Light background with dark text
  - Better for bright environments
  - Traditional appearance
  - Higher contrast

### Advanced Settings

#### Verbose Mode
- **Purpose**: Show additional technical details in Dev mode
- **Usage**: Enable for detailed debugging
- **Impact**: May slow down interface with large conversations

#### Performance Options
- **Message Limit**: Maximum messages to display at once
- **Lazy Loading**: Load messages as needed
- **Cache Settings**: Conversation caching preferences

### Settings Persistence

#### Storage
- **Database**: Settings stored in SQLite database
- **Session**: Temporary settings stored in browser session
- **Backup**: Settings included in database backups

#### Synchronization
- **Local Only**: Settings are device-specific
- **No Cloud Sync**: Settings don't sync across devices
- **Manual Backup**: Export settings if needed

## Advanced Features

### Conversation Analysis

#### Canonical Path Detection
- **Automatic**: System identifies main conversation thread
- **Algorithm**: Based on message relationships and timestamps
- **Manual Override**: Option to manually select path

#### Message Relationships
- **Parent-Child**: Messages that branch from others
- **Threading**: Conversation tree structure
- **Branches**: Alternative conversation paths

### Search and Filtering

#### Browser Search
- **Ctrl+F**: Standard browser search functionality
- **Highlight**: Matches highlighted in conversation
- **Navigation**: Jump between search results

#### Advanced Search (Future Feature)
- **Content Search**: Search within message content
- **Date Filtering**: Filter by conversation date
- **Model Filtering**: Filter by AI model used

### Export and Sharing

#### Conversation Export
- **Format Options**: JSON, Markdown, Plain Text
- **Selection**: Export individual conversations or all
- **Metadata**: Include or exclude technical details

#### Sharing Features
- **URL Sharing**: Direct links to conversations
- **Embedding**: Embed conversations in other applications
- **API Access**: Programmatic access to conversation data

### Keyboard Shortcuts

#### Navigation
- **Home**: Return to conversation list
- **Back**: Go back to previous page
- **Settings**: Open settings page

#### View Controls
- **Toggle Mode**: Switch between Nice and Dev modes
- **Toggle Theme**: Switch between dark and light themes
- **Full Screen**: Maximize conversation view

#### Content Interaction
- **Copy**: Copy selected text or message
- **Search**: Open search dialog
- **Refresh**: Reload current conversation

## Tips and Best Practices

### Efficient Browsing

#### Organization
- **Regular Imports**: Import conversations regularly to keep data current
- **Clean Titles**: Use descriptive conversation titles
- **Archive Old**: Move old conversations to archive if needed

#### Performance
- **Use Nice Mode**: For better performance with large conversations
- **Close Tabs**: Close unused conversation tabs
- **Clear Cache**: Clear browser cache if performance degrades

### Data Management

#### Backup Strategy
- **Regular Backups**: Backup your database regularly
- **Export Files**: Keep original ChatGPT export files
- **Multiple Copies**: Store backups in different locations

#### Storage Optimization
- **Database Size**: Monitor database file size
- **Cleanup**: Remove unnecessary conversations
- **Compression**: Consider database compression for large datasets

### Privacy and Security

#### Local Storage
- **No Cloud**: All data stored locally on your device
- **No Sharing**: Conversations not shared with external services
- **Full Control**: Complete control over your data

#### Best Practices
- **Secure Device**: Keep your device secure
- **Regular Updates**: Update the application regularly
- **Backup Encryption**: Encrypt backup files if needed

## Troubleshooting

### Common Issues

#### Import Problems
**Problem**: Import fails or shows errors
**Solutions**:
- Verify file format is correct ChatGPT export
- Check file size isn't too large
- Ensure sufficient disk space
- Try importing smaller batches

#### Display Issues
**Problem**: Conversations don't display correctly
**Solutions**:
- Clear browser cache and cookies
- Try different browser
- Check browser console for errors
- Restart the application

#### Performance Issues
**Problem**: Application is slow or unresponsive
**Solutions**:
- Switch to Nice Mode
- Close other applications
- Restart the application
- Check system resources

### Getting Help

#### Self-Help Resources
- **This Guide**: Comprehensive usage instructions
- **API Reference**: Technical endpoint documentation
- **Code Documentation**: Developer-focused documentation

#### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community help and tips
- **Documentation**: Additional guides and tutorials

#### Contact Information
- **Repository**: [GitHub Repository](https://github.com/actuallyrizzn/chatGPT-browser)
- **Issues**: [GitHub Issues](https://github.com/actuallyrizzn/chatGPT-browser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/actuallyrizzn/chatGPT-browser/discussions)

### Reporting Issues

#### What to Include
- **Description**: Clear description of the problem
- **Steps**: Step-by-step reproduction instructions
- **Environment**: Operating system, browser, Python version
- **Error Messages**: Copy of any error messages
- **Screenshots**: Visual evidence if applicable

#### Issue Templates
Use the provided issue templates for:
- **Bug Reports**: Application problems and errors
- **Feature Requests**: New functionality suggestions
- **Documentation**: Documentation improvements
- **General Questions**: Usage and configuration help

---

**Need more help?** Check the [Installation Guide](./INSTALLATION.md) for setup issues or the [API Reference](./API_REFERENCE.md) for technical details. 