# phase_1/review_drafts.py

import json
import sys

def review_draft_quality(drafts_path):
    """Quick review of draft quality before validation."""
    
    with open(drafts_path, 'r') as f:
        drafts = json.load(f)
    
    print("="*60)
    print("DRAFT QUALITY REVIEW")
    print("="*60)
    
    # Show selection rationale if present
    if 'selection_rationale' in drafts:
        print("\nSELECTION RATIONALE:")
        for channel, rationale in drafts.get('selection_rationale', {}).items():
            print(f"\n{channel.upper()}:")
            print(f"  {rationale}")
    
    draft_list = drafts.get('drafts', [])
    if not draft_list:
        print("\nERROR: No drafts found in file")
        return
    
    print("\n" + "="*60)
    print("DRAFTS BY CHANNEL:")
    print("="*60)
    
    # Group by channel
    by_channel = {}
    for draft in draft_list:
        channel = draft.get('channel', 'Unknown')
        if channel not in by_channel:
            by_channel[channel] = []
        by_channel[channel].append(draft)
    
    for channel, channel_drafts in sorted(by_channel.items()):
        print(f"\n--- {channel.upper()} ({len(channel_drafts)} drafts) ---")
        for draft in channel_drafts:
            angle_idx = draft.get('angle_index', '?')
            message = draft.get('angle_message', 'No message')
            print(f"\n  Angle {angle_idx}: {message[:60]}...")
            
            selection_reason = draft.get('selection_reason', '')
            if selection_reason:
                print(f"  Selection reason: {selection_reason[:80]}...")
            
            variations = draft.get('variations', [])
            print(f"  Variations: {len(variations)}")
            
            for i, var in enumerate(variations, 1):
                content = var.get('content', '')
                if isinstance(content, str):
                    content_preview = content[:80]
                else:
                    content_preview = str(content)[:80]
                
                print(f"\n    Variation {i}: {content_preview}...")
                
                refs = var.get('kernel_references', [])
                if refs:
                    print(f"    Refs: {', '.join(str(r) for r in refs[:5])}")
                
                notes = var.get('notes', '')
                if notes:
                    print(f"    Notes: {notes[:60]}...")
    
    print("\n" + "="*60)
    print("OBSERVATIONS FROM CLAUDE:")
    obs = drafts.get('observations', {})
    
    strongest = obs.get('strongest_angles', [])
    if strongest:
        print(f"\nStrongest: {', '.join(str(s) for s in strongest)}")
    else:
        print("\nStrongest: Not noted")
    
    weakest = obs.get('weakest_angles', [])
    if weakest:
        print(f"Weakest: {', '.join(str(w) for w in weakest)}")
    else:
        print("Weakest: Not noted")
    
    cross_channel = obs.get('cross_channel_potential', [])
    if cross_channel:
        print(f"Cross-channel: {', '.join(str(c) for c in cross_channel)}")
    else:
        print("Cross-channel: Not noted")
    
    thread_candidates = obs.get('thread_candidates', [])
    if thread_candidates:
        print(f"Thread candidates: {', '.join(str(t) for t in thread_candidates)}")
    
    print("="*60)

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_drafts.py <drafts_path>")
        print("  drafts_path: Path to stage 5a drafts JSON")
        sys.exit(1)
    
    drafts_path = sys.argv[1]
    review_draft_quality(drafts_path)

