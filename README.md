# ChatGPT Browser

A Flask web application for browsing and analyzing ChatGPT conversations. This tool allows you to import your ChatGPT conversation history and view it in either a clean, focused mode or a detailed developer mode.

## Features

- **Two View Modes**:
  - **Nice Mode**: A clean view showing only the canonical conversation path
  - **Dev Mode**: Full conversation view with technical details and metadata

- **Dark/Light Theme**: Toggle between dark and light themes for comfortable viewing

- **Conversation Analysis**:
  - Automatic identification of canonical conversation paths
  - Message metadata inspection in developer mode
  - Timestamps and conversation structure visualization

- **Import Functionality**:
  - Import conversations from ChatGPT JSON export files
  - Maintains full conversation history and metadata

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd chatgpt-browser
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix or MacOS:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Import your ChatGPT conversation history:
   - Go to Settings
   - Use the Import JSON section to upload your conversation export file

4. Browse your conversations:
   - Use Nice Mode for a clean, focused view
   - Switch to Dev Mode for technical details and metadata
   - Toggle dark/light theme as needed

## View Modes

### Nice Mode
- Shows only the canonical path of conversations
- Clean, distraction-free interface
- Perfect for reviewing conversation flow

### Dev Mode
- Shows all messages and technical details
- Includes message metadata and IDs
- Useful for debugging and development

## Settings

- **User/Assistant Names**: Customize display names
- **View Mode**: Toggle between Nice and Dev modes
- **Verbose Mode**: Show additional details in Dev mode
- **Dark Mode**: Toggle dark/light theme

## Technical Details

- Built with Flask
- Uses SQLite for data storage
- Supports markdown rendering
- Handles complex conversation trees

## License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0). This means you are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original

For more information, visit: https://creativecommons.org/licenses/by-sa/4.0/ 