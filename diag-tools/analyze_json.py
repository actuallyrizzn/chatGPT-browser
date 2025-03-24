import json
from collections import defaultdict

def analyze_json_structure(data, path="", structure=None):
    if structure is None:
        structure = defaultdict(int)
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            structure[current_path] += 1
            analyze_json_structure(value, current_path, structure)
    elif isinstance(data, list):
        if data:
            structure[f"{path}[0]"] += 1
            analyze_json_structure(data[0], f"{path}[0]", structure)
    elif isinstance(data, (str, int, float, bool, type(None))):
        structure[f"{path}"] += 1
    
    return structure

def main():
    with open('conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    structure = analyze_json_structure(data)
    
    print("\nJSON Structure Analysis:")
    print("=======================")
    for path, count in sorted(structure.items()):
        print(f"{path}: {count} occurrences")

if __name__ == "__main__":
    main() 