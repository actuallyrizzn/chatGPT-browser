from flask import Blueprint, render_template, jsonify, request, flash, redirect
from ..db.operations import get_conversation
from ..messages.service import MessageService

bp = Blueprint('messages', __name__)

@bp.route("/messages/<conversation_id>")
def messages(conversation_id):
    """Show messages in a conversation."""
    try:
        # Get the conversation details
        conversation = get_conversation(conversation_id)
        if not conversation:
            flash('Conversation not found', 'error')
            return redirect('/')
        
        # Get messages using the message service
        message_service = MessageService()
        messages = message_service.get_canonical_conversation(conversation_id)
        
        if not messages:
            flash('No messages found in this conversation', 'warning')
            return redirect('/')
        
        # Get a clean view for display
        display_messages = message_service.build_conversation_view(conversation_id)
        
        return render_template('pages/messages.html',
                             conversation=conversation,
                             messages=display_messages,
                             all_messages=messages,
                             dev_view=True)  # Enable dev view by default for now
                             
    except Exception as e:
        flash('An error occurred while loading the conversation', 'error')
        return redirect('/')

@bp.route("/api/messages/<conversation_id>")
def api_messages(conversation_id):
    """API endpoint for messages in a conversation."""
    try:
        message_service = MessageService()
        messages = message_service.get_canonical_conversation(conversation_id)
        
        return jsonify({
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.author_role,
                    "content": msg.content,
                    "create_time": msg.create_time,
                    "parent_id": msg.parent_id,
                    "children": msg.children,
                    "metadata": msg.metadata
                }
                for msg in messages
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 