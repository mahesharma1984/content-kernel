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
    
    draft_list = drafts.get('drafts', [])
    if not draft_list:
        print("ERROR: No drafts found in file")
        return
    
    for draft in draft_list:
        print(f"\n--- ANGLE {draft.get('angle_index', '?')}: {draft.get('channel', 'Unknown').upper()} ---")
        message = draft.get('angle_message', 'No message')
        print(f"Message: {message[:60]}...")
        
        variations = draft.get('variations', [])
        print(f"Variations: {len(variations)}")
        
        for i, var in enumerate(variations, 1):
            content = var.get('content', '')
            if isinstance(content, str):
                content_preview = content[:100]
            else:
                content_preview = str(content)[:100]
            
            print(f"\n  Variation {i}: {content_preview}...")
            
            refs = var.get('kernel_references', [])
            if refs:
                print(f"  Refs: {', '.join(str(r) for r in refs[:5])}")
            
            notes = var.get('notes', '')
            if notes:
                print(f"  Notes: {notes[:80]}...")
    
    print("\n" + "="*60)
    print("OBSERVATIONS FROM CLAUDE:")
    obs = drafts.get('observations', {})
    
    strongest = obs.get('strongest_angles', [])
    if strongest:
        print(f"Strongest: {', '.join(str(s) for s in strongest)}")
    else:
        print("Strongest: Not noted")
    
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
    
    print("="*60)

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_drafts.py <drafts_path>")
        print("  drafts_path: Path to stage 5a drafts JSON")
        sys.exit(1)
    
    drafts_path = sys.argv[1]
    review_draft_quality(drafts_path)

