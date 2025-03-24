import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Message:
    id: str
    role: str
    content: str
    create_time: int
    parent_id: Optional[str]
    children: List[str]
    metadata: dict

def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect('athena.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_messages_for_conversation(conn: sqlite3.Connection, conversation_id: str) -> Dict[str, Message]:
    """Fetch all messages for a conversation and return them as a dict keyed by message ID."""
    messages = {}
    
    # First get all messages with their metadata
    cursor = conn.execute('''
        SELECT 
            m.id,
            m.author_role as role,
            m.content,
            m.create_time,
            mm.parent_id,
            mm.model_slug,
            mm.finish_details,
            mm.citations,
            mm.content_references
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.id
        WHERE m.conversation_id = ?
        ORDER BY m.create_time ASC
    ''', (conversation_id,))
    
    for row in cursor:
        messages[row['id']] = Message(
            id=row['id'],
            role=row['role'],
            content=row['content'],
            create_time=row['create_time'] or 0,  # Default to 0 if None
            parent_id=row['parent_id'],  # This will be None if no metadata
            children=[],
            metadata={
                'model': row['model_slug'],
                'finish_details': json.loads(row['finish_details']) if row['finish_details'] else None,
                'citations': json.loads(row['citations']) if row['citations'] else None,
                'content_references': json.loads(row['content_references']) if row['content_references'] else None
            }
        )
    
    # Build child relationships
    for msg_id, msg in messages.items():
        if msg.parent_id and msg.parent_id in messages:
            if msg_id not in messages[msg.parent_id].children:
                messages[msg.parent_id].children.append(msg_id)
    
    return messages

def find_root_messages(messages: Dict[str, Message]) -> Set[str]:
    """Find all messages that have no parent (root nodes)."""
    return {msg_id for msg_id, msg in messages.items() 
            if not msg.parent_id and msg.role == 'user'}

def find_leaf_messages(messages: Dict[str, Message]) -> Set[str]:
    """Find all messages that have no children (leaf nodes)."""
    has_children = set()
    for msg in messages.values():
        has_children.update(msg.children)
    
    # Only consider messages that have no children and are not system messages
    return {msg_id for msg_id in messages.keys() 
            if msg_id not in has_children and messages[msg_id].role != 'system'}

def find_canonical_path(messages: Dict[str, Message], msg_id: str, direction: str = 'backward') -> List[Message]:
    """
    Find the canonical path from a message.
    direction: 'backward' to trace to root, 'forward' to trace to leaves, 'both' for full chain
    """
    path = []
    visited = set()
    
    def trace_backward(current_id):
        current_path = []
        while current_id and current_id not in visited:
            if current_id not in messages:
                break
            visited.add(current_id)
            msg = messages[current_id]
            if msg.role != 'system':
                current_path.append(msg)
            current_id = msg.parent_id
        return list(reversed(current_path))
    
    def trace_forward(current_id):
        current_path = []
        while current_id and current_id not in visited:
            if current_id not in messages:
                break
            visited.add(current_id)
            msg = messages[current_id]
            if msg.role != 'system':
                current_path.append(msg)
            # For forward tracing, we take the first child (if any)
            current_id = msg.children[0] if msg.children else None
        return current_path
    
    if direction == 'backward':
        path = trace_backward(msg_id)
    elif direction == 'forward':
        path = trace_forward(msg_id)
    else:  # both
        # First trace back to root
        root_path = trace_backward(msg_id)
        visited.clear()  # Reset visited set
        # Then trace forward from the original message
        forward_path = trace_forward(msg_id)
        # Combine paths, excluding the duplicate middle message
        path = root_path + forward_path[1:] if forward_path else root_path
    
    return path

def print_conversation_path(path: List[Message]):
    """Pretty print a conversation path."""
    print(f"\nPath length: {len(path)} messages")
    for i, msg in enumerate(path, 1):
        timestamp = datetime.fromtimestamp(msg.create_time)
        print(f"\n{i}. [{timestamp.strftime('%H:%M:%S')}] {msg.role.upper()}:")
        print(f"   ID: {msg.id}")
        print(f"   Parent: {msg.parent_id or 'None'}")
        print(f"   Content: {msg.content[:100]}...")
        if msg.children:
            print(f"   Children: {len(msg.children)} ({', '.join(c[:8] + '...' for c in msg.children)})")
        if msg.metadata.get('model'):
            print(f"   Model: {msg.metadata['model']}")

def analyze_conversation_structure(messages: Dict[str, Message]):
    """Analyze and print statistics about the conversation structure."""
    total_msgs = len(messages)
    root_nodes = find_root_messages(messages)
    leaf_nodes = find_leaf_messages(messages)
    
    # Count messages by role
    roles = defaultdict(int)
    for msg in messages.values():
        roles[msg.role] += 1
    
    # Find all complete chains (from root to leaf)
    all_chains = []
    max_depth = 0
    
    for root_id in root_nodes:
        # Trace forward from each root to find complete chains
        chain = find_canonical_path(messages, root_id, 'forward')
        if chain:
            all_chains.append(chain)
            max_depth = max(max_depth, len(chain))
    
    # Sort chains by length (descending)
    all_chains.sort(key=len, reverse=True)
    
    print("\nConversation Analysis:")
    print(f"Total messages: {total_msgs}")
    print(f"Root nodes (conversation starters): {len(root_nodes)}")
    print(f"Leaf nodes (endpoints): {len(leaf_nodes)}")
    print(f"Messages by role: {dict(roles)}")
    print(f"Maximum thread depth: {max_depth}")
    print(f"Number of complete chains: {len(all_chains)}")
    
    # Print details of the longest chains
    print("\nLongest conversation chains:")
    for i, chain in enumerate(all_chains[:3], 1):
        print(f"\nChain {i} (length: {len(chain)}):")
        for j, msg in enumerate(chain, 1):
            print(f"  {j}. {msg.role}: {msg.content[:50]}...")
    
    return root_nodes, leaf_nodes, all_chains

def main():
    CONVERSATION_ID = "678743d8-7910-8001-8b6f-056364b32f3f"
    
    conn = connect_db()
    messages = get_messages_for_conversation(conn, CONVERSATION_ID)
    
    if not messages:
        print("No messages found for this conversation")
        return
    
    print(f"\nAnalyzing conversation: {CONVERSATION_ID}")
    root_nodes, leaf_nodes, all_chains = analyze_conversation_structure(messages)
    
    if all_chains:
        # Find the longest chain
        longest_chain = max(all_chains, key=len)
        print("\nLongest canonical chain:")
        print_conversation_path(longest_chain)
        
        # Also show an example of a complete chain from root to leaf
        print("\nExample of tracing a complete chain:")
        example_root = next(iter(root_nodes))
        complete_chain = find_canonical_path(messages, example_root, 'both')
        print_conversation_path(complete_chain)
    else:
        print("\nNo valid conversation chains found.")
    
    conn.close()

if __name__ == "__main__":
    main() 