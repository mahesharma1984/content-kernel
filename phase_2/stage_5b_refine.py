# phase_2/stage_5b_refine.py

import json
import os
import sys
from anthropic import Anthropic

def load_prompt_template(path):
    with open(path, 'r') as f:
        return f.read()

def refine_with_constraints(starting_path, channels_path, thread_path, prompt_path, output_path):
    """Apply Stage 5B refinement."""
    
    # Load inputs
    with open(starting_path, 'r') as f:
        starting = json.load(f)
    
    with open(channels_path, 'r') as f:
        channels = json.load(f)
    
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    template = load_prompt_template(prompt_path)
    
    # Extract drafts
    drafts = starting.get('starting_drafts', {})
    
    # Helper to get channel data with case-insensitive lookup
    def get_channel_data(channel_key):
        for k, v in channels.items():
            if k.lower() == channel_key.lower():
                return v
        return {}
    
    def get_draft(channel_key):
        for k, v in drafts.items():
            if k.lower() == channel_key.lower():
                return v
        return {}
    
    # Prepare prompt
    social_channel = get_channel_data('social')
    youtube_channel = get_channel_data('youtube')
    seo_channel = get_channel_data('seo')
    guide_channel = get_channel_data('guide')
    
    social_draft_data = get_draft('social')
    youtube_draft_data = get_draft('youtube')
    seo_draft_data = get_draft('seo')
    guide_draft_data = get_draft('guide')
    
    prompt = template.format(
        core_message=thread['core_message'],
        agitation_register=thread['agitation_register'],
        solution_register=thread['solution_register'],
        starting_drafts_json=json.dumps(drafts, indent=2),
        channel_strategy_json=json.dumps(channels, indent=2),
        social_draft=json.dumps(social_draft_data, indent=2),
        social_job=social_channel.get('job', 'Not defined'),
        social_must_do=json.dumps(social_channel.get('must_do', [])),
        social_must_not_do=json.dumps(social_channel.get('must_not_do', [])),
        youtube_draft=json.dumps(youtube_draft_data, indent=2),
        youtube_job=youtube_channel.get('job', 'Not defined'),
        youtube_must_do=json.dumps(youtube_channel.get('must_do', [])),
        youtube_must_not_do=json.dumps(youtube_channel.get('must_not_do', [])),
        seo_draft=json.dumps(seo_draft_data, indent=2),
        seo_job=seo_channel.get('job', 'Not defined'),
        seo_must_do=json.dumps(seo_channel.get('must_do', [])),
        seo_must_not_do=json.dumps(seo_channel.get('must_not_do', [])),
        guide_draft=json.dumps(guide_draft_data, indent=2),
        guide_job=guide_channel.get('job', 'Not defined'),
        guide_must_do=json.dumps(guide_channel.get('must_do', [])),
        guide_must_not_do=json.dumps(guide_channel.get('must_not_do', []))
    )
    
    # Call API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Refining content with constraints...")
    print("(This may take 60-90 seconds)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        # Save raw
        raw_path = output_path.replace('.json', '.raw')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(raw_path, 'w') as f:
            f.write(response_text)
        print(f"Raw response saved: {raw_path}")
        
        # Parse JSON
        json_text = response_text
        
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            if json_end > json_start:
                json_text = response_text[json_start:json_end].strip()
        
        # Try to find JSON object if not in code block
        if not json_text.strip().startswith('{'):
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
        
        try:
            refined = json.loads(json_text.strip())
            
            with open(output_path, 'w') as f:
                json.dump(refined, f, indent=2)
            
            print(f"✓ Refined content saved: {output_path}")
            
            # Quick validation summary
            overall = refined.get('overall_validation', {})
            print(f"\nAll constraints met: {overall.get('all_constraints_met', 'Unknown')}")
            print(f"Ready for rendering: {overall.get('ready_for_rendering', 'Unknown')}")
            
            if overall.get('issues_found'):
                print(f"Issues: {overall['issues_found']}")
            
            return refined
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print("Check the .raw file")
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
    starting_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_starting_drafts.json"
    channels_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    thread_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    prompt_path = sys.argv[4] if len(sys.argv) > 4 else "prompts/phase_2/stage_5b_constrained.txt"
    output_path = sys.argv[5] if len(sys.argv) > 5 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_content.json"
    
    refine_with_constraints(starting_path, channels_path, thread_path, prompt_path, output_path)

