# phase_2/review_5b_inputs.py

import json
import sys

def review_5b_inputs(starting_path, channels_path, thread_path):
    """Display all inputs for 5B refinement."""
    
    with open(starting_path, 'r') as f:
        starting = json.load(f)
    
    with open(channels_path, 'r') as f:
        channels = json.load(f)
    
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    print("="*60)
    print("STAGE 5B INPUTS")
    print("="*60)
    
    print("\n--- CORE THREAD ---")
    print(f"Message: {thread['core_message']}")
    print(f"Agitation: {thread['agitation_register'][:80]}...")
    print(f"Solution: {thread['solution_register'][:80]}...")
    
    print("\n--- CHANNEL CONSTRAINTS ---")
    for channel, strategy in channels.items():
        print(f"\n{channel.upper()}:")
        print(f"  Job: {strategy['job']}")
        must_do = strategy.get('must_do', [])
        must_not_do = strategy.get('must_not_do', [])
        if must_do:
            print(f"  Must do: {must_do[:2]}")
        if must_not_do:
            print(f"  Must not: {must_not_do[:2]}")
    
    print("\n--- STARTING DRAFTS ---")
    drafts = starting.get('starting_drafts', {})
    if not drafts:
        print("  No drafts found!")
    else:
        for channel, draft in drafts.items():
            content = draft.get('content', '')
            if isinstance(content, str):
                preview = content[:100]
            elif isinstance(content, dict):
                preview = str(content)[:100]
            else:
                preview = str(content)[:100]
            print(f"\n{channel.upper()}:")
            print(f"  {preview}...")
            refs = draft.get('kernel_references', [])
            if refs:
                print(f"  Kernel refs: {', '.join(refs[:3])}...")

# Usage
if __name__ == "__main__":
    starting_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_starting_drafts.json"
    channels_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    thread_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    
    review_5b_inputs(starting_path, channels_path, thread_path)


