# phase_2/select_winning_drafts.py

import json
import sys
import os

def select_winning_drafts(thread_path, drafts_5a_path, messages_path):
    """Find drafts for the winning angle."""
    
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    with open(drafts_5a_path, 'r') as f:
        drafts_5a = json.load(f)
    
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    print("="*60)
    print("SELECTING WINNING ANGLE'S DRAFTS")
    print("="*60)
    
    print(f"\nWinning thread: {thread['core_message'][:60]}...")
    
    # Find winning angle index - check if thread has angle_id or we need to match
    source_angle_id = thread.get('source_angle', '')
    
    # Try to find matching angle in messages
    winning_index = None
    if source_angle_id:
        # Extract index from angle_id (e.g., "Social-3" -> need to find in messages)
        print(f"\nSource angle ID: {source_angle_id}")
        # Find the angle index
        for i, angle in enumerate(messages['angles']):
            channel = angle.get('channel', '')
            # Simple matching: check if message matches or angle_id matches
            angle_num = i + 1
            expected_id = f"{channel}-{angle_num}"
            if expected_id == source_angle_id or angle['message'] == thread['core_message']:
                winning_index = i
                break
    
    if winning_index is None:
        # Manual identification needed
        print("\nCould not auto-match angle. Please select manually:")
        print("\nMatching angles by message similarity:")
        for i, angle in enumerate(messages['angles'], 1):
            similarity = "✓" if angle['message'][:50] in thread['core_message'][:100] or thread['core_message'][:50] in angle['message'][:100] else " "
            channel = angle.get('channel', 'Unknown')
            print(f"  [{i}] {similarity} [{channel}] {angle['message'][:60]}...")
        
        try:
            winning_index = int(input("\nEnter angle number (1-based): ")) - 1
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(1)
    
    print(f"\n✓ Selected angle index: {winning_index}")
    print(f"  Message: {messages['angles'][winning_index]['message'][:80]}...")
    
    # Extract drafts for winning angle
    winning_drafts = {}
    
    # Handle different draft structures
    drafts_list = drafts_5a.get('drafts', [])
    if not drafts_list:
        # Try alternative structure
        drafts_list = drafts_5a.get('content_blocks', [])
    
    for draft in drafts_list:
        # Handle different index fields
        draft_index = draft.get('angle_index') or draft.get('index') or draft.get('angle_id')
        if draft_index is None:
            # Try to match by channel and message content
            continue
        
        # Convert to int if needed
        if isinstance(draft_index, str):
            # Try to extract number
            try:
                draft_index = int(''.join(filter(str.isdigit, draft_index)))
            except:
                continue
        
        if draft_index == winning_index:
            channel = draft.get('channel', '').lower()
            # Take best variation (first one, or manually select)
            if 'variations' in draft and draft['variations']:
                winning_drafts[channel] = {
                    'content': draft['variations'][0].get('content', draft['variations'][0]),
                    'kernel_references': draft['variations'][0].get('kernel_references', []),
                    'all_variations': draft['variations']
                }
            elif 'content' in draft:
                winning_drafts[channel] = {
                    'content': draft['content'],
                    'kernel_references': draft.get('kernel_references', []),
                    'all_variations': []
                }
    
    print(f"\nFound drafts for channels: {list(winning_drafts.keys())}")
    
    # Save
    output_path = "outputs/manual_exploration/phase_2/TKAM_stage_5b_starting_drafts.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            'winning_angle_index': winning_index,
            'winning_angle_id': source_angle_id,
            'thread_summary': thread['core_message'],
            'starting_drafts': winning_drafts
        }, f, indent=2)
    
    print(f"✓ Starting drafts saved: {output_path}")
    return winning_drafts

# Usage
if __name__ == "__main__":
    thread_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    drafts_5a_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_1/TKAM_stage_5a_drafts.json"
    messages_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    
    select_winning_drafts(thread_path, drafts_5a_path, messages_path)

