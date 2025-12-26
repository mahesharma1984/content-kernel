# phase_2/review_messages.py

import json
import sys

def review_message_matrix(messages_path):
    """Display all message angles for review."""
    
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    print("="*60)
    print("MESSAGE MATRIX REVIEW")
    print("="*60)
    
    channels = {}
    for angle in messages['angles']:
        channel = angle['channel']
        if channel not in channels:
            channels[channel] = []
        channels[channel].append(angle)
    
    for channel, angles in sorted(channels.items()):
        print(f"\n{'='*60}")
        print(f"{channel.upper()} ({len(angles)} angles)")
        print('='*60)
        
        for i, angle in enumerate(angles, 1):
            print(f"\n[{channel}-{i}]")
            print(f"Message: {angle['message']}")
            print(f"Hook type: {angle['hook_type']}")
            print(f"Pain point: {angle['pain_point'][:80]}...")
            print(f"Kernel refs: {', '.join(angle['kernel_elements'][:3])}...")
            print(f"Derives: {angle.get('why_this_derives', '')[:100]}...")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(messages['angles'])} angles across {len(channels)} channels")
    print("="*60)

# Usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        messages_path = sys.argv[1]
    else:
        messages_path = "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    
    review_message_matrix(messages_path)
