import sqlite3
import difflib

def get_canonical_thread(conn, conversation_id):
    # Get total count of messages
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM messages m
        WHERE m.conversation_id = ?
        AND m.content NOT LIKE '%<%'
        AND m.content NOT LIKE '%<function_results>%'
        AND m.content NOT LIKE '%*%'
        AND m.content NOT LIKE '%...%'
        AND m.content NOT LIKE '%((ooc%'
        AND m.content NOT LIKE '%[ooc%'
        AND m.content NOT LIKE '%meta%'
        AND m.content NOT LIKE '%meatspace%'
        AND m.content NOT LIKE '%chakra%'
        AND m.content NOT LIKE '%energy%'
        AND m.content NOT LIKE '%duality%'
        AND LENGTH(m.content) < 500
    """, (conversation_id,))
    total_count = cursor.fetchone()[0]
    print(f"\n=== Message Analysis ===")
    print(f"Total filtered messages: {total_count}")

    # Process messages in batches
    batch_size = 50
    offset = 0
    user_messages = []
    assistant_messages = []
    
    while offset < total_count:
        cursor.execute("""
            SELECT m.role, m.content, m.timestamp
            FROM messages m
            WHERE m.conversation_id = ?
            AND m.content NOT LIKE '%<%'
            AND m.content NOT LIKE '%<function_results>%'
            AND m.content NOT LIKE '%*%'
            AND m.content NOT LIKE '%...%'
            AND m.content NOT LIKE '%((ooc%'
            AND m.content NOT LIKE '%[ooc%'
            AND m.content NOT LIKE '%meta%'
            AND m.content NOT LIKE '%meatspace%'
            AND m.content NOT LIKE '%chakra%'
            AND m.content NOT LIKE '%energy%'
            AND m.content NOT LIKE '%duality%'
            AND LENGTH(m.content) < 500
            ORDER BY m.timestamp
            LIMIT ? OFFSET ?
        """, (conversation_id, batch_size, offset))
        
        for role, content, timestamp in cursor.fetchall():
            if role == 'user':
                user_messages.append((content, timestamp))
            else:
                assistant_messages.append((content, timestamp))
        
        offset += batch_size

    # Group similar user messages
    user_groups = []
    current_group = []
    
    for msg, ts in user_messages:
        if not current_group:
            current_group = [(msg, ts)]
        else:
            # Compare with first message in group
            similarity = difflib.SequenceMatcher(None, 
                current_group[0][0][:100], 
                msg[:100]).ratio()
            
            if similarity > 0.8:
                current_group.append((msg, ts))
            else:
                user_groups.append(current_group)
                current_group = [(msg, ts)]
    
    if current_group:
        user_groups.append(current_group)

    # Print detailed analysis
    print(f"\nTotal user messages: {len(user_messages)}")
    print(f"Total assistant messages: {len(assistant_messages)}")
    print(f"Number of user message groups: {len(user_groups)}")
    
    # Analyze message patterns
    print("\nMessage Pattern Analysis:")
    print(f"Average messages per group: {len(user_messages) / len(user_groups):.2f}")
    print(f"Assistant response ratio: {len(assistant_messages) / len(user_messages):.2f}")
    
    # Build canonical thread
    canonical_thread = []
    
    for group in user_groups:
        # Use first message as canonical
        canonical_msg, ts = group[0]
        canonical_thread.append(('user', canonical_msg))
        
        # Find closest assistant response
        closest_response = None
        min_time_diff = float('inf')
        
        for a_msg, a_ts in assistant_messages:
            time_diff = abs(a_ts - ts)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_response = a_msg
        
        if closest_response:
            canonical_thread.append(('assistant', closest_response))

    return canonical_thread

def main():
    conn = sqlite3.connect('../messages.db')
    thread = get_canonical_thread(conn, "678743d8-7910-8001-8b6f-056364b32f3f")
    
    print("\n=== Canonical Thread ===")
    for role, msg in thread:
        if len(msg) > 100:
            print(f"\n{role}: {msg[:100]}...")
        else:
            print(f"\n{role}: {msg}")
    
    conn.close()

if __name__ == '__main__':
    main() 