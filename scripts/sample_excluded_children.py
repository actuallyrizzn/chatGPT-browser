#!/usr/bin/env python3
"""Sample excluded message_children links from import; report why they're excluded and what we're losing."""
import json
import sys
import os

# Run from project root; conversations.json path
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = os.path.join(BASE, "chatgpt_export", "conversations.json")


def why_message_skipped(message_id, message_data):
    """Return reason string if this message would be skipped in pass 1."""
    message = message_data.get("message")
    if message is None:
        return "no 'message' key"
    if not message:
        return "empty message dict"
    return None  # would be inserted


def content_preview(parts, max_len=120):
    """First bit of first text part."""
    if not parts:
        return "(no parts)"
    for p in parts:
        if isinstance(p, str) and p.strip():
            return (p.strip()[:max_len] + "…") if len(p.strip()) > max_len else p.strip()
        if isinstance(p, dict) and p.get("content_type") == "text":
            t = (p.get("text") or "").strip()
            if t:
                return (t[:max_len] + "…") if len(t) > max_len else t
    return "(non-text or empty parts)"


def role_of(message):
    if not message:
        return "?"
    return (message.get("author") or {}).get("role") or "?"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    max_conversations = int(os.environ.get("MAX_CONV", "800"))
    max_excluded_samples = int(os.environ.get("MAX_SAMPLES", "30"))

    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {path} (max convs={max_conversations})...", file=sys.stderr)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    conversations = data[:max_conversations]
    print(f"Processing {len(conversations)} conversations...", file=sys.stderr)

    # Same logic as db.import_conversations_data for "would this message be inserted?"
    excluded_child_links = []  # (conv_id, conv_title, parent_id, child_id, why_child_skipped, child_data_preview)
    excluded_parent_links = []  # parent had children but parent was skipped
    total_skipped_child_links = 0
    total_skipped_parent_blocks = 0

    for conv in conversations:
        conversation_id = conv.get("id") or ""
        title = (conv.get("title") or "")[:60]
        mapping = conv.get("mapping") or {}
        inserted_message_ids = set()

        for message_id, message_data in mapping.items():
            reason = why_message_skipped(message_id, message_data)
            if reason is None:
                inserted_message_ids.add(message_id)
            # else: would be skipped in pass 1

        # Pass 2: find excluded links
        for message_id, message_data in mapping.items():
            children = message_data.get("children") or []
            if not children:
                continue
            if message_id not in inserted_message_ids:
                total_skipped_parent_blocks += 1
                if len(excluded_parent_links) < max_excluded_samples:
                    msg = (message_data.get("message") or {})
                    excluded_parent_links.append({
                        "conv_id": conversation_id,
                        "title": title,
                        "parent_id": message_id,
                        "num_children": len(children),
                        "why_parent_skipped": why_message_skipped(message_id, message_data),
                        "parent_role": role_of(msg),
                        "parent_content_preview": content_preview((msg.get("content") or {}).get("parts") or []),
                    })
                continue
            for child_id in children:
                if child_id not in inserted_message_ids:
                    total_skipped_child_links += 1
                    if len(excluded_child_links) < max_excluded_samples:
                        child_data = mapping.get(child_id) or {}
                        child_msg = child_data.get("message") or {}
                        parts = (child_msg.get("content") or {}).get("parts") or []
                        excluded_child_links.append({
                            "conv_id": conversation_id,
                            "title": title,
                            "parent_id": message_id,
                            "child_id": child_id,
                            "why_child_skipped": why_message_skipped(child_id, child_data),
                            "child_role": role_of(child_msg),
                            "child_content_preview": content_preview(parts),
                        })

    # Report
    print()
    print("=== Excluded parent-child links (sample) ===")
    print()
    print(f"Total excluded child links (child not inserted): {total_skipped_child_links}")
    print(f"Total excluded parent blocks (parent not inserted, so all its child links dropped): {total_skipped_parent_blocks}")
    print()

    if excluded_parent_links:
        print("--- Sample: parents that were skipped (so we never add their children) ---")
        for i, r in enumerate(excluded_parent_links[:15], 1):
            print(f"  {i}. conv={r['conv_id'][:20]}… title={r['title'][:40]}…")
            print(f"     parent_id={r['parent_id'][:36]}… why_skipped={r['why_parent_skipped']} role={r['parent_role']}")
            print(f"     content_preview: {r['parent_content_preview'][:80]}")
            print(f"     num_children we dropped: {r['num_children']}")
            print()
    print()

    if excluded_child_links:
        print("--- Sample: child links excluded (parent inserted, child not) ---")
        for i, r in enumerate(excluded_child_links[:15], 1):
            print(f"  {i}. conv={r['conv_id'][:20]}… title={r['title'][:40]}…")
            print(f"     parent_id={r['parent_id'][:36]}… -> child_id={r['child_id'][:36]}…")
            print(f"     why_child_skipped={r['why_child_skipped']} child_role={r['child_role']}")
            print(f"     child_content_preview: {r['child_content_preview'][:80]}")
            print()


if __name__ == "__main__":
    main()
