# phase_2/stage_2_generate.py

import os
import json
import sys
from anthropic import Anthropic

def generate_channel_strategy(thread_path, prompt_path, output_path):
    """Generate Stage 2 channel strategy from thread."""
    
    # Load thread
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    # Load prompt
    with open(prompt_path, 'r') as f:
        prompt_template = f.read()
    
    # Fill prompt
    prompt = prompt_template.format(
        core_message=thread['core_message'],
        agitation_register=thread['agitation_register'],
        solution_register=thread['solution_register'],
        kernel_pattern_reference=thread.get('kernel_pattern_reference', '')
    )
    
    # Call Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Calling Claude API for Stage 2: Channel Strategy...")
    print("(This may take 45-60 seconds)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse
        response_text = response.content[0].text
        
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
            channels = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON")
            print(f"JSONDecodeError: {e}")
            with open(f"{output_path}.raw", 'w') as f:
                f.write(response_text)
            raise e
        
        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(channels, f, indent=2)
        
        print(f"✓ Channel strategy saved to: {output_path}")
        print(f"\nDefined jobs for {len(channels)} channels:")
        for channel, strategy in channels.items():
            print(f"\n{channel}:")
            print(f"  Job: {strategy['job']}")
        
        return channels
        
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        print("Check:")
        print("  1. ANTHROPIC_API_KEY is set")
        print("  2. Prompt length < 100k tokens")
        print("  3. Internet connection working")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    thread_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    prompt_path = sys.argv[2] if len(sys.argv) > 2 else "prompts/phase_2/stage_2_channels.txt"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    
    channels = generate_channel_strategy(thread_path, prompt_path, output_path)

