# phase_1/stage_1_generate.py

import os
import json
import sys
from anthropic import Anthropic

def generate_audience_profile(kernel_path, prompt_path, output_path):
    """Generate Stage 1 audience profile using Claude."""
    
    # Load kernel
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Load prompt template
    with open(prompt_path, 'r') as f:
        prompt_template = f.read()
    
    # Extract kernel elements (v5.1 structure)
    metadata = kernel.get('metadata', {})
    alignment = kernel.get('alignment_pattern', {})
    devices = kernel.get('micro_devices', [])
    
    # Prepare device list (top 8 devices)
    device_priorities = alignment.get('device_priorities', [])
    shown_devices = set()
    device_list_items = []
    
    # First show prioritized devices
    for device_name in device_priorities[:5]:
        if len(device_list_items) >= 8:
            break
        # Find device details
        for device in devices:
            if device['name'] == device_name and device_name not in shown_devices:
                operational_layer = device.get('assigned_section', 'N/A')
                device_list_items.append(f"- {device['name']} ({operational_layer})")
                shown_devices.add(device_name)
                break
    
    # Then show remaining devices if needed
    for device in devices:
        if device['name'] not in shown_devices and len(device_list_items) < 8:
            operational_layer = device.get('assigned_section', 'N/A')
            device_list_items.append(f"- {device['name']} ({operational_layer})")
            shown_devices.add(device['name'])
    
    device_list = "\n".join(device_list_items)
    
    # Fill in kernel details
    prompt = prompt_template.format(
        pattern_from_kernel=alignment.get('pattern_name', 'Not found'),
        core_dynamic_from_kernel=alignment.get('core_dynamic', 'Not found'),
        reader_effect_from_kernel=alignment.get('reader_effect', 'Not found'),
        list_of_device_names_and_layers=device_list
    )
    
    # Call Claude API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Calling Claude API for Stage 1: Audience Mapping...")
    print("(This may take 30-60 seconds)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON (handle markdown fences)
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            json_text = response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            json_text = response_text[start:end].strip()
        else:
            json_text = response_text.strip()
        
        # Try to find JSON object if not in code block
        if not json_text.startswith('{'):
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
        
        try:
            audience_profile = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON")
            print(f"JSONDecodeError: {e}")
            print(f"\nResponse text (first 500 chars): {response_text[:500]}...")
            print(f"\nSaving raw response to {output_path}.raw")
            with open(f"{output_path}.raw", 'w') as f:
                f.write(response_text)
            raise e
        
        # Save result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(audience_profile, f, indent=2)
        
        print(f"✓ Audience profile saved to: {output_path}")
        print(f"\nFound {len(audience_profile.get('segments', []))} segments:")
        for seg in audience_profile.get('segments', []):
            print(f"  - {seg.get('name', 'Unnamed')} ({seg.get('awareness_stage', 'Unknown')})")
        
        return audience_profile
        
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        print("Check:")
        print("  1. ANTHROPIC_API_KEY is set")
        print("  2. Prompt length < 100k tokens")
        print("  3. Internet connection working")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    kernel_path = sys.argv[1] if len(sys.argv) > 1 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    prompt_path = sys.argv[2] if len(sys.argv) > 2 else "prompts/phase_1/stage_1_audience.txt"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json"
    
    audience = generate_audience_profile(kernel_path, prompt_path, output_path)



