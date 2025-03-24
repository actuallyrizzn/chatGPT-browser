import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def format_timestamp(ts):
    """Format timestamp or return None if invalid"""
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(ts).isoformat()
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(ts).isoformat()
        except (TypeError, ValueError):
            return str(ts)

def get_conversation_data(conv_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('../athena.db')
        conn.row_factory = sqlite3.Row
        
        # Get conversation details
        conv = conn.execute('''
            SELECT id, title, create_time
            FROM conversations 
            WHERE id = ?
        ''', (conv_id,)).fetchone()
        
        if not conv:
            print(f"Conversation {conv_id} not found!")
            return None
        
        # Get all messages with their metadata and relationships
        messages = conn.execute('''
            WITH RECURSIVE msg_chain AS (
                -- Start with messages that have no parent
                SELECT 
                    m.id,
                    m.author_role,
                    m.content,
                    m.create_time,
                    mm.parent_id,
                    mm.message_type,
                    mm.model_slug,
                    mm.request_id,
                    0 as depth
                FROM messages m
                LEFT JOIN message_metadata mm ON m.id = mm.id
                WHERE m.conversation_id = ? AND mm.parent_id IS NULL
                
                UNION ALL
                
                -- Get all children recursively
                SELECT 
                    m.id,
                    m.author_role,
                    m.content,
                    m.create_time,
                    mm.parent_id,
                    mm.message_type,
                    mm.model_slug,
                    mm.request_id,
                    mc.depth + 1
                FROM messages m
                JOIN message_metadata mm ON m.id = mm.id
                JOIN msg_chain mc ON mm.parent_id = mc.id
                WHERE m.conversation_id = ?
            )
            SELECT 
                mc.*,
                GROUP_CONCAT(mch.child_id) as children
            FROM msg_chain mc
            LEFT JOIN message_children mch ON mc.id = mch.parent_id
            GROUP BY mc.id
            ORDER BY mc.depth ASC, mc.create_time ASC
        ''', (conv_id, conv_id)).fetchall()
        
        # Build message relationships
        message_map = {}
        children_map = defaultdict(list)
        
        for msg in messages:
            # Convert row to dict and process children
            msg_dict = dict(msg)
            children = msg_dict.pop('children')
            if children:
                msg_dict['children'] = children.split(',')
            else:
                msg_dict['children'] = []
                
            # Format timestamps
            msg_dict['create_time'] = format_timestamp(msg_dict['create_time'])
            
            # Store in maps
            message_map[msg_dict['id']] = msg_dict
            if msg_dict['parent_id']:
                children_map[msg_dict['parent_id']].append(msg_dict['id'])
        
        # Add child info to messages
        for msg_id, children in children_map.items():
            if msg_id in message_map:
                message_map[msg_id]['children'] = children
        
        # Convert to final format
        conversation_data = {
            'id': conv['id'],
            'title': conv['title'],
            'create_time': format_timestamp(conv['create_time']),
            'messages': list(message_map.values())
        }
        
        return conversation_data
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def analyze_message_chains(data):
    """Analyze message chains and variations"""
    if not data or 'messages' not in data:
        return
        
    # Build parent-child tree
    children = defaultdict(list)
    messages = {msg['id']: msg for msg in data['messages']}
    
    # First, build the complete parent-child relationships
    for msg in data['messages']:
        if msg['parent_id']:
            children[msg['parent_id']].append(msg['id'])
    
    # Find root messages (no parent)
    roots = [msg for msg in data['messages'] if not msg['parent_id']]
    roots.sort(key=lambda m: m['create_time'] if m['create_time'] else '')
    
    print("\nMessage Chains Analysis:")
    for root in roots:
        if not root['content'].strip():  # Skip empty messages
            continue
            
        print(f"\nChain starting with: {root['id']}")
        print(f"Role: {root['author_role']}")
        print(f"Time: {root['create_time']}")
        print(f"Content: {root['content'][:100]}...")
        
        # Follow the chain
        current = root
        chain = [current]
        variations = []
        responses = []
        
        # Process immediate children
        if current['id'] in children:
            child_msgs = [messages[child_id] for child_id in children[current['id']]]
            # Split into variations (same role) and responses (different role)
            variations = [m for m in child_msgs if m['author_role'] == current['author_role']]
            responses = [m for m in child_msgs if m['author_role'] != current['author_role']]
            
            if variations:
                print(f"\nVariations ({len(variations)}):")
                for i, var in enumerate(variations, 1):
                    print(f"  {i}. [{var['create_time']}] {var['content'][:100]}...")
            
            if responses:
                print(f"\nResponses ({len(responses)}):")
                for i, resp in enumerate(responses, 1):
                    print(f"  {i}. [{resp['create_time']}] {resp['content'][:100]}...")
                    # Check for variations of the response
                    if resp['id'] in children:
                        resp_variations = [messages[child_id] for child_id in children[resp['id']]
                                        if messages[child_id]['author_role'] == resp['author_role']]
                        if resp_variations:
                            print(f"     Response variations ({len(resp_variations)}):")
                            for j, var in enumerate(resp_variations, 1):
                                print(f"     {j}. [{var['create_time']}] {var['content'][:100]}...")
        
        print("-" * 80)

def main():
    conv_id = "678743d8-7910-8001-8b6f-056364b32f3f"
    data = get_conversation_data(conv_id)
    
    if data:
        # Save to JSON file with pretty printing
        output_file = f'conversation_{conv_id}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Conversation data saved to {output_file}")
        
        # Print basic stats
        print("\nConversation Summary:")
        print(f"Title: {data['title']}")
        print(f"Created: {data['create_time']}")
        print(f"Number of messages: {len(data['messages'])}")
        
        # Count messages by role
        role_counts = {}
        for msg in data['messages']:
            role = msg['author_role']
            role_counts[role] = role_counts.get(role, 0) + 1
        print("\nMessages by role:")
        for role, count in role_counts.items():
            print(f"{role}: {count}")
        
        # Analyze message chains and variations
        analyze_message_chains(data)
        
        # Print metadata summary
        print("\nMetadata Summary:")
        model_counts = defaultdict(int)
        message_types = defaultdict(int)
        for msg in data['messages']:
            if msg['model_slug']:
                model_counts[msg['model_slug']] += 1
            if msg['message_type']:
                message_types[msg['message_type']] += 1
        
        if model_counts:
            print("\nModel usage:")
            for model, count in model_counts.items():
                print(f"  {model}: {count}")
        
        if message_types:
            print("\nMessage types:")
            for msg_type, count in message_types.items():
                print(f"  {msg_type}: {count}")
    else:
        print("Failed to retrieve conversation data")

if __name__ == "__main__":
    main() 