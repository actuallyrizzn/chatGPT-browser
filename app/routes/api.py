from flask import Blueprint, jsonify, request
from ..db.operations import get_message_details
from ..messages.service import MessageService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/messages/<conversation_id>/<message_id>/details")
def message_details(conversation_id, message_id):
    """API endpoint for getting detailed message information."""
    try:
        message = get_message_details(message_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
            
        # Verify the message belongs to the conversation
        if str(message.get('conversation_id')) != conversation_id:
            return jsonify({'error': 'Message does not belong to this conversation'}), 403
            
        return jsonify(message)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/messages/<conversation_id>/chain/<message_id>")
def message_chain(conversation_id, message_id):
    """API endpoint for getting a message chain."""
    try:
        message_service = MessageService()
        messages = message_service.get_canonical_conversation(conversation_id)
        
        # Create a lookup dictionary
        message_dict = {msg.id: msg for msg in messages}
        
        # Find the chain for this message
        from ..messages.threading import find_message_chain
        chain = find_message_chain(message_dict, message_id)
        
        return jsonify({
            "chain": [
                {
                    "id": msg.id,
                    "role": msg.author_role,
                    "content": msg.content,
                    "create_time": msg.create_time,
                    "parent_id": msg.parent_id,
                    "children": msg.children,
                    "metadata": msg.metadata
                }
                for msg in chain
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 