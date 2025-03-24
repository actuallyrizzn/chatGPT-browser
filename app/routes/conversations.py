from flask import Blueprint, render_template, jsonify, request
from ..db.operations import get_conversations, get_conversation
from ..messages.service import MessageService

bp = Blueprint('conversations', __name__)

@bp.route("/")
def index():
    """Show conversations list."""
    conversations = get_conversations()
    return render_template("pages/index.html", conversations=conversations)

@bp.route("/api/conversations")
def api_conversations():
    """API endpoint for server-side paginated conversations."""
    # Get pagination parameters
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 50))
    
    # Get all conversations and paginate in memory
    # (In a real app, we'd paginate at the database level)
    all_conversations = get_conversations()
    total_count = len(all_conversations)
    
    # Slice for pagination
    paginated = all_conversations[start:start + length]
    
    # Format for DataTables
    return jsonify({
        "recordsTotal": total_count,
        "recordsFiltered": total_count,
        "data": [
            {
                "id": conv.id,
                "title": conv.title,
                "create_time": conv.create_time
            }
            for conv in paginated
        ]
    }) 