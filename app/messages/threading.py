from typing import List, Dict, Set
from ..db.models import Message

def find_root_messages(messages: List[Message]) -> Set[str]:
    """Find all root messages (messages with no parent)."""
    return {msg.id for msg in messages if not msg.parent_id}

def build_canonical_chain(messages: Dict[str, Message], start_id: str) -> List[Message]:
    """Build a canonical chain of messages starting from a given message ID."""
    result = []
    processed_ids = set()
    current_id = start_id

    while current_id and current_id not in processed_ids:
        if current_id not in messages:
            break

        current_msg = messages[current_id]
        result.append(current_msg)
        processed_ids.add(current_id)

        # Find the next message in the chain
        next_id = None

        # First try to find an unprocessed child
        if current_msg.children:
            for child_id in current_msg.children:
                if child_id not in processed_ids and child_id in messages:
                    next_id = child_id
                    break

        # If no unprocessed child found, try to find a message that has this as parent
        if not next_id:
            for msg_id, msg in messages.items():
                if msg.parent_id == current_id and msg_id not in processed_ids:
                    next_id = msg_id
                    break

        current_id = next_id

    return result

def find_message_chain(messages: Dict[str, Message], message_id: str) -> List[Message]:
    """Find the complete chain of messages leading to and from a given message."""
    if message_id not in messages:
        return []

    # First, find all ancestors
    ancestors = []
    current_id = messages[message_id].parent_id
    while current_id and current_id in messages:
        ancestors.insert(0, messages[current_id])
        current_id = messages[current_id].parent_id

    # Then get the message itself and its descendants
    chain = build_canonical_chain(messages, message_id)

    # Combine ancestors with the rest of the chain
    return ancestors + chain

def get_message_depth(messages: Dict[str, Message], message_id: str) -> int:
    """Get the depth of a message in its chain (number of ancestors)."""
    if message_id not in messages:
        return 0

    depth = 0
    current_id = messages[message_id].parent_id
    while current_id and current_id in messages:
        depth += 1
        current_id = messages[current_id].parent_id

    return depth 