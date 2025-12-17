# phase_1/stage_5a_generate.py

import os
import json
import sys
from anthropic import Anthropic
from pathlib import Path

def load_prompt_template(template_path):
    """Load prompt template from file."""
    with open(template_path, 'r') as f:
        return f.read()

def prepare_kernel_context(kernel):
    """Extract key kernel elements for prompt."""
    
    # Pattern info (v5.1 structure)
    alignment = kernel.get('alignment_pattern', {})
    pattern = alignment.get('pattern_name', 'Not found')
    core_dynamic = alignment.get('core_dynamic', 'Not found')
    reader_effect = alignment.get('reader_effect', 'Not found')
    
    # Get devices (v5.1 uses 'micro_devices')
    devices = kernel.get('micro_devices', [])
    
    # Get priority devices first
    device_priorities = alignment.get('device_priorities', [])
    shown_devices = set()
    device_list_items = []
    
    # Show prioritized devices with effect
    for device_name in device_priorities[:8]:
        if len(device_list_items) >= 8:
            break
        for device in devices:
            if device['name'] == device_name and device_name not in shown_devices:
                effect = device.get('effect', 'No effect listed')
                # Truncate effect to ~100 chars
                effect_preview = effect[:100] + '...' if len(effect) > 100 else effect
                device_list_items.append(f"- {device['name']}: {effect_preview}")
                shown_devices.add(device_name)
                break
    
    # Add remaining devices if needed
    for device in devices:
        if device['name'] not in shown_devices and len(device_list_items) < 8:
            effect = device.get('effect', 'No effect listed')
            effect_preview = effect[:100] + '...' if len(effect) > 100 else effect
            device_list_items.append(f"- {device['name']}: {effect_preview}")
            shown_devices.add(device['name'])
    
    device_list = "\n".join(device_list_items)
    
    # Sample quotes (first 5 devices with anchor_phrase)
    quotes = []
    quote_count = 0
    for device_name in device_priorities[:5]:
        if quote_count >= 5:
            break
        for device in devices:
            if device['name'] == device_name and 'anchor_phrase' in device:
                quote = device['anchor_phrase']
                # Truncate quote to ~80 chars
                quote_preview = quote[:80] + '...' if len(quote) > 80 else quote
                quotes.append(f'"{quote_preview}" — {device["name"]}')
                quote_count += 1
                break
    
    # Add more quotes from remaining devices if needed
    for device in devices:
        if quote_count >= 5:
            break
        if device['name'] not in [q.split(' — ')[1] for q in quotes] and 'anchor_phrase' in device:
            quote = device['anchor_phrase']
            quote_preview = quote[:80] + '...' if len(quote) > 80 else quote
            quotes.append(f'"{quote_preview}" — {device["name"]}')
            quote_count += 1
    
    quote_list = "\n".join(quotes) if quotes else "See device entries for quotes"
    
    return {
        'kernel_pattern': pattern,
        'core_dynamic': core_dynamic,
        'reader_effect': reader_effect,
        'device_list_with_effects': device_list,
        'sample_quotes': quote_list
    }

def generate_exploratory_drafts(messages_path, kernel_path, prompt_path, output_path):
    """Generate Stage 5A exploratory drafts."""
    
    # Load inputs
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Get book title from kernel metadata
    metadata = kernel.get('metadata', {})
    book_title = metadata.get('title', 'Unknown Book')
    
    # Prepare prompt
    template = load_prompt_template(prompt_path)
    kernel_context = prepare_kernel_context(kernel)
    
    # Format angles JSON
    angles = messages.get('angles', [])
    
    # Format template (book_title will be replaced after due to escaping)
    prompt = template.format(
        angles_json=json.dumps(angles, indent=2),
        **kernel_context
    )
    # Replace the placeholder with actual book title
    prompt = prompt.replace("___BOOK_TITLE_PLACEHOLDER___", book_title)
    
    # Call API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Generating exploratory drafts...")
    print(f"Processing {len(angles)} angles...")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract JSON from response
        response_text = response.content[0].text
        
        # Save raw response
        raw_path = output_path.replace('.json', '.raw')
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(raw_path, 'w') as f:
            f.write(response_text)
        print(f"Raw response saved: {raw_path}")
        
        # Parse JSON
        try:
            # Handle markdown fences
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end]
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end]
            
            # Try to find JSON object if not in code block
            if not response_text.strip().startswith('{'):
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
            
            drafts = json.loads(response_text.strip())
            
            # Save parsed output
            with open(output_path, 'w') as f:
                json.dump(drafts, f, indent=2)
            
            print(f"Drafts saved: {output_path}")
            print(f"Total angle drafts: {len(drafts.get('drafts', []))}")
            
            return drafts
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print("Check the .raw file and extract JSON manually")
            return None
            
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        print("Check:")
        print("  1. ANTHROPIC_API_KEY is set")
        print("  2. Prompt length < 100k tokens")
        print("  3. Internet connection working")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    messages_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    prompt_path = sys.argv[3] if len(sys.argv) > 3 else "prompts/phase_1/stage_5a_exploratory.txt"
    output_path = sys.argv[4] if len(sys.argv) > 4 else "outputs/manual_exploration/phase_1/TKAM_stage_5a_drafts.json"
    
    drafts = generate_exploratory_drafts(messages_path, kernel_path, prompt_path, output_path)

