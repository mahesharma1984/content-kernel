# phase_1/stage_3_generate.py

import os
import json
import sys
from anthropic import Anthropic

def generate_message_matrix(kernel_path, audience_path, prompt_path, output_path):
    """Generate Stage 3 message matrix using Claude."""
    
    # Load inputs
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    with open(audience_path, 'r') as f:
        audience = json.load(f)
    
    with open(prompt_path, 'r') as f:
        prompt_template = f.read()
    
    # Prepare kernel summary (v5.1 structure)
    alignment = kernel.get('alignment_pattern', {})
    devices = kernel.get('micro_devices', [])
    
    # Get priority devices first
    device_priorities = alignment.get('device_priorities', [])
    shown_devices = set()
    device_list_items = []
    
    # Show prioritized devices with effect
    for device_name in device_priorities[:8]:
        for device in devices:
            if device['name'] == device_name and device_name not in shown_devices:
                operational_layer = device.get('assigned_section', 'N/A')
                effect = device.get('effect', '')[:80]
                device_list_items.append(f"- {device['name']} ({operational_layer}): {effect}")
                shown_devices.add(device_name)
                break
    
    # Add remaining devices if needed
    for device in devices:
        if device['name'] not in shown_devices and len(device_list_items) < 8:
            operational_layer = device.get('assigned_section', 'N/A')
            effect = device.get('effect', '')[:80]
            device_list_items.append(f"- {device['name']} ({operational_layer}): {effect}")
            shown_devices.add(device['name'])
    
    device_list = "\n".join(device_list_items)
    
    # Prepare audience summary
    segments = audience.get('segments', [])
    audience_summary = "\n".join([
        f"- {s.get('name', 'Unnamed')} ({s.get('awareness_stage', 'Unknown')}): {s.get('pain_point', 'No pain point')}"
        for s in segments
    ])
    
    # Get high-intent searches
    high_intent = audience.get('high_intent_searches', [])
    if not high_intent:
        # Fall back to search terms from segments
        search_terms_list = []
        for seg in segments:
            search_terms_list.extend(seg.get('search_terms', []))
        high_intent = search_terms_list[:10]
    
    search_terms = "\n".join([
        f"- {term}"
        for term in high_intent[:10]
    ])
    
    # Fill prompt
    prompt = prompt_template.format(
        pattern=alignment.get('pattern_name', 'Not found'),
        core_dynamic=alignment.get('core_dynamic', 'Not found'),
        reader_effect=alignment.get('reader_effect', 'Not found'),
        device_list=device_list,
        audience_segments_summary=audience_summary,
        search_terms=search_terms
    )
    
    # Call Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Calling Claude API for Stage 3: Message Derivation...")
    print("(This may take 60-90 seconds for 12-20 angles)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON
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
            message_matrix = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON")
            print(f"JSONDecodeError: {e}")
            print(f"\nSaving raw response to {output_path}.raw")
            with open(f"{output_path}.raw", 'w') as f:
                f.write(response_text)
            raise e
        
        # Save result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(message_matrix, f, indent=2)
        
        print(f"✓ Message matrix saved to: {output_path}")
        
        # Summary
        angles = message_matrix.get('angles', [])
        channels = {}
        for angle in angles:
            channel = angle.get('channel', 'Unknown')
            channels[channel] = channels.get(channel, 0) + 1
        
        print(f"\nGenerated {len(angles)} message angles:")
        for channel, count in sorted(channels.items()):
            print(f"  - {channel}: {count} angles")
        
        return message_matrix
        
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
    audience_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json"
    prompt_path = sys.argv[3] if len(sys.argv) > 3 else "prompts/phase_1/stage_3_messages.txt"
    output_path = sys.argv[4] if len(sys.argv) > 4 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    
    messages = generate_message_matrix(kernel_path, audience_path, prompt_path, output_path)


