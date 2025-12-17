# phase_1/review_for_drafts.py

import json
import sys

def review_angles_for_drafting(messages_path, kernel_path):
    """Display message angles ready for draft generation."""
    
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    print("="*60)
    print("MESSAGE ANGLES FOR EXPLORATORY DRAFTS")
    print("="*60)
    
    angles = messages.get('angles', [])
    if not angles:
        print("ERROR: No angles found in messages file")
        return
    
    for i, angle in enumerate(angles, 1):
        print(f"\n--- ANGLE {i} ---")
        print(f"Channel: {angle.get('channel', 'Unknown')}")
        message = angle.get('message', 'No message')
        print(f"Message: {message[:100]}...")
        print(f"Hook type: {angle.get('hook_type', 'Unknown')}")
        
        # Handle different possible field names for kernel references
        kernel_refs = angle.get('kernel_references', []) or angle.get('kernel_elements', [])
        if kernel_refs:
            print(f"Kernel refs: {', '.join(str(r) for r in kernel_refs[:3])}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {len(angles)} angles to draft")
    print("="*60)

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_for_drafts.py <messages_path> [kernel_path]")
        print("  messages_path: Path to stage 3 messages JSON")
        print("  kernel_path: Path to kernel JSON (optional, for reference)")
        sys.exit(1)
    
    messages_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    
    review_angles_for_drafting(messages_path, kernel_path)

