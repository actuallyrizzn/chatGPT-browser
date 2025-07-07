# ChatGPT Browser - API Reference

## Overview

This document provides a comprehensive reference for all API endpoints in the ChatGPT Browser application. The application uses Flask's routing system to provide a RESTful interface for managing ChatGPT conversations.

## Base URL

All endpoints are relative to the application root. When running locally:
```
http://localhost:5000
```

## Authentication

Currently, the application does not implement authentication. All endpoints are publicly accessible.

## Response Formats

### Success Responses
- **HTML Responses**: Most endpoints return HTML pages for browser viewing
- **JSON Responses**: Toggle endpoints return JSON for AJAX requests
- **Redirects**: Some endpoints redirect to other pages after processing

### Error Responses
- **400 Bad Request**: Invalid input data or file uploads
- **404 Not Found**: Requested resource doesn't exist
- **500 Internal Server Error**: Server-side processing errors

## Endpoints

### 1. Index Page

**Endpoint**: `GET /`

**Description**: Displays the main conversation list page.

**Response**: HTML page showing all conversations in chronological order.

**Template**: `index.html`

**Query Parameters**: None

**Example Request**:
```bash
curl http://localhost:5000/
```

**Response**: HTML page with conversation list

### 2. Conversation View (Dev Mode)

**Endpoint**: `GET /conversation/<conversation_id>`

**Description**: Displays a conversation in full developer mode with all metadata.

**Parameters**:
- `conversation_id` (path): The unique identifier of the conversation

**Response**: HTML page with complete conversation data

**Template**: `conversation.html`

**Redirects**: 
- If dev mode is disabled, redirects to nice view
- If conversation not found, returns 404

**Example Request**:
```bash
curl http://localhost:5000/conversation/abc123
```

**Response**: HTML page with full conversation in dev mode

### 3. Nice Conversation View

**Endpoint**: `GET /conversation/<conversation_id>/nice`

**Description**: Displays only the canonical conversation path in a clean interface.

**Parameters**:
- `conversation_id` (path): The unique identifier of the conversation

**Response**: HTML page with canonical conversation path

**Template**: `nice_conversation.html`

**Example Request**:
```bash
curl http://localhost:5000/conversation/abc123/nice
```

**Response**: HTML page with clean conversation view

### 4. Full Conversation View (Override)

**Endpoint**: `GET /conversation/<conversation_id>/full`

**Description**: Temporarily enables dev mode for viewing a conversation.

**Parameters**:
- `conversation_id` (path): The unique identifier of the conversation

**Response**: Redirects to conversation view with dev mode enabled

**Session Variables**: Sets `override_dev_mode = True`

**Example Request**:
```bash
curl http://localhost:5000/conversation/abc123/full
```

**Response**: Redirect to `/conversation/abc123` with dev mode enabled

### 5. Settings Page

**Endpoint**: `GET /settings`

**Description**: Displays the application settings page.

**Response**: HTML page with current settings

**Template**: `settings.html`

**Example Request**:
```bash
curl http://localhost:5000/settings
```

**Response**: HTML page with settings form

### 6. Update Names

**Endpoint**: `POST /update_names`

**Description**: Updates the display names for user and assistant messages.

**Content-Type**: `application/x-www-form-urlencoded`

**Form Data**:
- `user_name` (string): Display name for user messages
- `assistant_name` (string): Display name for assistant messages

**Response**: Redirects to index page

**Example Request**:
```bash
curl -X POST http://localhost:5000/update_names \
  -d "user_name=John&assistant_name=AI Assistant"
```

**Response**: Redirect to `/`

### 7. Toggle View Mode

**Endpoint**: `GET /toggle_view_mode`

**Description**: Toggles between nice mode and dev mode.

**Response**: JSON response with new mode status

**Content-Type**: `application/json`

**Example Request**:
```bash
curl http://localhost:5000/toggle_view_mode
```

**Example Response**:
```json
{
  "success": true,
  "dev_mode": true
}
```

### 8. Toggle Dark Mode

**Endpoint**: `GET /toggle_dark_mode`

**Description**: Toggles between dark and light themes.

**Response**: Redirects to previous page or index

**Example Request**:
```bash
curl http://localhost:5000/toggle_dark_mode
```

**Response**: Redirect to previous page with theme changed

### 9. Toggle Verbose Mode

**Endpoint**: `GET /toggle_verbose_mode`

**Description**: Toggles verbose mode for additional technical details.

**Query Parameters**:
- `temp` (optional): If "true", creates temporary session override

**Response**: JSON response with new verbose status

**Content-Type**: `application/json`

**Example Request**:
```bash
# Permanent toggle
curl http://localhost:5000/toggle_verbose_mode

# Temporary toggle
curl http://localhost:5000/toggle_verbose_mode?temp=true
```

**Example Response**:
```json
{
  "success": true,
  "verbose_mode": true
}
```

### 10. Import JSON

**Endpoint**: `POST /import`

**Description**: Imports ChatGPT conversation data from a JSON file.

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file` (file): JSON file containing ChatGPT export data

**Response**: Redirects to index page on success, error message on failure

**Error Responses**:
- `400 Bad Request`: No file uploaded, empty file, or invalid JSON

**Example Request**:
```bash
curl -X POST http://localhost:5000/import \
  -F "file=@conversations.json"
```

**Response**: Redirect to `/` on success

## Data Models

### Conversation Object

```json
{
  "id": "string",
  "create_time": "string",
  "update_time": "string",
  "title": "string"
}
```

### Message Object

```json
{
  "id": "string",
  "conversation_id": "string",
  "role": "string",
  "content": "string",
  "create_time": "string",
  "update_time": "string",
  "parent_id": "string",
  "metadata": {
    "message_type": "string",
    "model_slug": "string",
    "citations": "string",
    "content_references": "string",
    "finish_details": "string",
    "is_complete": "boolean",
    "request_id": "string",
    "timestamp_": "string",
    "message_source": "string",
    "serialization_metadata": "string"
  }
}
```

### Settings Object

```json
{
  "user_name": "string",
  "assistant_name": "string",
  "dev_mode": "boolean",
  "dark_mode": "boolean",
  "verbose_mode": "boolean"
}
```

## Error Handling

### Common Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 400 | Bad Request | Invalid file upload, malformed JSON |
| 404 | Not Found | Conversation ID doesn't exist |
| 500 | Internal Server Error | Database errors, processing failures |

### Error Response Format

For JSON endpoints:
```json
{
  "error": "Error message description"
}
```

For HTML endpoints:
```html
<div class="error">Error message description</div>
```

## Session Management

### Session Variables

The application uses Flask sessions to store temporary state:

- `override_dev_mode` (boolean): Temporarily override dev mode setting
- `override_verbose_mode` (boolean): Temporarily override verbose mode setting

### Session Lifecycle

- Sessions are created automatically on first request
- Session data persists across requests within the same browser session
- Sessions are cleared when the browser is closed or session expires

## File Upload

### Supported File Types

- **Content-Type**: `application/json`
- **File Extension**: `.json`
- **Size Limit**: Determined by Flask configuration (default: 16MB)

### Upload Process

1. File is validated for JSON format
2. Content is parsed and validated against ChatGPT export schema
3. Data is processed and stored in database
4. User is redirected to conversation list

### Import Schema Validation

The import system expects the following JSON structure:

```json
[
  {
    "id": "conversation_id",
    "create_time": "timestamp",
    "update_time": "timestamp",
    "title": "Conversation Title",
    "mapping": {
      "message_id": {
        "id": "message_id",
        "message": {
          "id": "message_id",
          "author": {"role": "user|assistant"},
          "content": {"parts": ["message content"]},
          "create_time": "timestamp",
          "update_time": "timestamp",
          "metadata": {}
        },
        "parent": "parent_message_id",
        "children": ["child_message_ids"]
      }
    }
  }
]
```

## Rate Limiting

Currently, the application does not implement rate limiting. All endpoints are accessible without restrictions.

## CORS Policy

The application does not implement CORS headers. It is designed for same-origin requests from the web interface.

## Security Considerations

### Input Validation

- All user inputs are validated before processing
- File uploads are checked for valid JSON format
- SQL injection is prevented through parameterized queries

### File Upload Security

- Only JSON files are accepted
- File content is validated before processing
- Upload size is limited by Flask configuration

### Session Security

- Sessions use cryptographically secure random keys
- Session data is stored server-side
- Sessions expire automatically

## Performance Considerations

### Database Queries

- All queries use parameterized statements
- Indexes are created on frequently queried columns
- Connections are properly managed and closed

### File Processing

- Large files are processed in memory
- Import process continues even if individual records fail
- Database transactions ensure data consistency

## Testing

### Manual Testing

Test each endpoint with various inputs:

```bash
# Test conversation list
curl http://localhost:5000/

# Test conversation view
curl http://localhost:5000/conversation/test-id

# Test settings
curl http://localhost:5000/settings

# Test toggle endpoints
curl http://localhost:5000/toggle_view_mode
curl http://localhost:5000/toggle_dark_mode
curl http://localhost:5000/toggle_verbose_mode
```

### Error Testing

Test error conditions:

```bash
# Test invalid conversation ID
curl http://localhost:5000/conversation/invalid-id

# Test invalid file upload
curl -X POST http://localhost:5000/import -F "file=@invalid.txt"
```

---

*This API reference covers all endpoints and their usage. For implementation details, see the main code documentation.* 