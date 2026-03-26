import json
import re

def remove_links(text):
    """Remove URLs/links from text."""
    url_pattern = r'https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/\S*'
    if not isinstance(text, str):
        return ''
    return re.sub(url_pattern, '', text).strip()

def preprocess_context(input_file, output_file=None):
    """
    Preprocess the context field in JSON by removing links.
    """
    if output_file is None:
        output_file = str(input_file).replace('.json', '_cleaned.json')
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    def clean_item(item):
        if not isinstance(item, dict):
            return
        if 'context' in item:
            item['context'] = remove_links(item.get('context'))
        if 'message' in item:
            item['message'] = remove_links(item.get('message'))

    if isinstance(data, list):
        for item in data:
            clean_item(item)
    elif isinstance(data, dict) and 'data' in data:
        for item in data['data']:
            clean_item(item)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"   Preprocessed file saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    pass # Removed hardcoded path execution