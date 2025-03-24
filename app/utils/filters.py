import json
import markdown
from datetime import datetime
from markupsafe import Markup

def register_filters(app):
    """Register custom Jinja filters."""
    
    @app.template_filter('tojson')
    def tojson_filter(obj, indent=None):
        """Convert object to JSON string."""
        return json.dumps(obj, indent=indent)

    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown to HTML."""
        return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables']))

    @app.template_filter('format_timestamp')
    def format_timestamp(timestamp):
        """Format Unix timestamp to readable date/time."""
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return timestamp  # Return as is if conversion fails 