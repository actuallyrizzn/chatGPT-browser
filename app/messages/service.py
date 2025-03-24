from typing import List, Optional, Dict
from ..db.models import Message
from ..db.operations import get_messages_for_conversation
from .threading import build_canonical_chain, find_root_messages
from .similarity import is_similar_content

class MessageService:
    @staticmethod
    def get_canonical_conversation(conversation_id: str) -> List[Message]:
        """Get the canonical conversation path for a given conversation."""
        messages = get_messages_for_conversation(conversation_id)
        if not messages:
            return []

        # Create a lookup dictionary for messages
        message_dict = {msg.id: msg for msg in messages}
        
        # Find root messages and sort by creation time
        root_messages = find_root_messages(messages)
        if not root_messages:
            return sorted(messages, key=lambda x: x.create_time)

        # Get the first root message chronologically
        first_root = min(root_messages, key=lambda msg_id: message_dict[msg_id].create_time)
        
        # Build the canonical chain
        return build_canonical_chain(message_dict, first_root)

    @staticmethod
    def group_similar_messages(messages: List[Message]) -> List[List[Message]]:
        """Group messages by similarity."""
        groups = []
        current_group = []

        for msg in messages:
            if msg.author_role == 'user':
                if not current_group or is_similar_content(msg.content, current_group[0].content):
                    current_group.append(msg)
                else:
                    if current_group:
                        groups.append(current_group)
                    current_group = [msg]
            else:  # assistant message
                if current_group:
                    groups.append(current_group)
                    current_group = []
                groups.append([msg])

        if current_group:
            groups.append(current_group)

        return groups

    @staticmethod
    def get_best_message_from_group(messages: List[Message]) -> Message:
        """Get the most complete message from a group of similar messages."""
        if not messages:
            return None
        return max(messages, key=lambda m: len(m.content))

    @staticmethod
    def build_conversation_view(conversation_id: str) -> List[Message]:
        """Build a clean conversation view, grouping similar messages."""
        messages = get_messages_for_conversation(conversation_id)
        if not messages:
            return []

        # Group similar messages
        groups = MessageService.group_similar_messages(messages)
        
        # Select best message from each group
        result = []
        for group in groups:
            best_msg = MessageService.get_best_message_from_group(group)
            if best_msg:
                result.append(best_msg)

        return result 