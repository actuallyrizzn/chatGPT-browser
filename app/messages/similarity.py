from typing import Set
import re

def normalize_text(text: str) -> str:
    """Normalize text for comparison by converting to lowercase and removing special characters."""
    return re.sub(r'[^\w\s]', '', text.lower())

def get_words(text: str) -> Set[str]:
    """Get a set of words from text, ignoring common words."""
    common_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
                   'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
    words = set(normalize_text(text).split())
    return words - common_words

def is_similar_content(content1: str, content2: str, threshold: float = 0.7) -> bool:
    """Check if two messages are similar based on content."""
    # Convert to lowercase and get first 100 chars for quick comparison
    c1 = content1.lower()[:100]
    c2 = content2.lower()[:100]
    
    # If one is a prefix of the other, they're similar
    if c1.startswith(c2[:50]) or c2.startswith(c1[:50]):
        return True
    
    # Get word sets for each content
    words1 = get_words(content1)
    words2 = get_words(content2)
    
    if not words1 or not words2:
        return False
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return False
    
    similarity = intersection / union
    return similarity >= threshold

def find_best_match(content: str, candidates: list[str]) -> tuple[int, float]:
    """Find the best matching content from a list of candidates.
    Returns (index, similarity_score)."""
    if not candidates:
        return (-1, 0.0)
    
    best_score = 0.0
    best_index = -1
    
    for i, candidate in enumerate(candidates):
        # Get word sets
        words1 = get_words(content)
        words2 = get_words(candidate)
        
        if not words1 or not words2:
            continue
        
        # Calculate similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union > 0:
            score = intersection / union
            if score > best_score:
                best_score = score
                best_index = i
    
    return (best_index, best_score) 