# validation/validate_stage_3.py

import json
import sys

def validate_message_matrix(messages_path, kernel_path, audience_path):
    """
    Validate that messages derive from kernel and address real pain points.
    
    PRECISION task: Check references exist.
    REASONING task (manual): Check if derivation makes sense.
    """
    
    # Load files
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    with open(audience_path, 'r') as f:
        audience = json.load(f)
    
    # Extract valid elements (PRECISION)
    # v5.1 structure
    devices = kernel.get('micro_devices', [])
    valid_devices = {d['name'] for d in devices}
    alignment = kernel.get('alignment_pattern', {})
    valid_pattern = alignment.get('pattern_name', '')
    
    # Get pain points from audience profile
    segments = audience.get('segments', [])
    valid_pain_points = {s.get('pain_point', '') for s in segments if s.get('pain_point')}
    
    print("="*60)
    print("STAGE 3 VALIDATION: Message Matrix")
    print("="*60)
    
    issues = []
    channel_counts = {}
    
    angles = messages.get('angles', [])
    if not angles:
        print("ERROR: No angles found in message matrix")
        return False
    
    for i, angle in enumerate(angles, 1):
        channel = angle.get('channel', 'Unknown')
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        hook_type = angle.get('hook_type', 'Unknown')
        print(f"\n[{i}] {channel} - {hook_type}")
        message = angle.get('message', 'No message')
        print(f"  Message: {message[:80]}{'...' if len(message) > 80 else ''}")
        
        # Validate kernel references (PRECISION)
        kernel_refs = angle.get('kernel_elements', [])
        valid_refs = True
        
        if not kernel_refs:
            issues.append(f"Angle {i}: No kernel_elements provided")
            print(f"  ✗ No kernel elements")
            valid_refs = False
        else:
            for ref in kernel_refs:
                # Check if it's a device (allow partial matches)
                device_match = False
                for valid_device in valid_devices:
                    if ref.lower() in valid_device.lower() or valid_device.lower() in ref.lower():
                        device_match = True
                        print(f"  ✓ Device: {ref} (matches {valid_device})")
                        break
                
                # Check if it mentions the pattern
                if not device_match:
                    if valid_pattern and (any(word in ref.lower() for word in valid_pattern.lower().split()) or 
                                          ref.lower() in valid_pattern.lower()):
                        print(f"  ✓ Pattern reference: {ref}")
                        device_match = True
                
                if not device_match:
                    issues.append(f"Angle {i}: May reference non-existent element '{ref}'")
                    print(f"  ⚠ Unknown reference: {ref}")
                    valid_refs = False
        
        # Check pain point exists (PRECISION)
        pain_point = angle.get('pain_point', '')
        if not pain_point:
            issues.append(f"Angle {i}: No pain point specified")
            print(f"  ✗ No pain point")
        else:
            # Fuzzy match - check if pain point relates to any segment
            pain_match = False
            for valid_pain in valid_pain_points:
                # Simple overlap check
                pain_words = set(pain_point.lower().split())
                valid_words = set(valid_pain.lower().split())
                if len(pain_words & valid_words) >= 2:  # At least 2 words overlap
                    pain_match = True
                    break
            
            if pain_match:
                print(f"  → Pain: {pain_point[:60]}{'...' if len(pain_point) > 60 else ''}")
            else:
                print(f"  ⚠ Pain point may not match audience segments: {pain_point[:60]}")
        
        # Check derivation explanation exists (for manual review)
        derivation = angle.get('why_this_derives', '')
        if not derivation:
            print(f"  ⚠ No derivation explanation")
        else:
            print(f"  → Derives: {derivation[:60]}{'...' if len(derivation) > 60 else ''}")
    
    # Check distribution across channels
    print(f"\n{'='*60}")
    print("CHANNEL DISTRIBUTION:")
    for channel, count in sorted(channel_counts.items()):
        status = "✓" if count >= 3 else "⚠"
        print(f"  {status} {channel}: {count} angles")
        if count < 3:
            issues.append(f"{channel} has only {count} angles (need 3+)")
    
    # Summary
    print(f"\n{'='*60}")
    if issues:
        print("VALIDATION ISSUES:")
        for issue in issues:
            print(f"  • {issue}")
        print(f"\nStatus: NEEDS REVIEW")
        return False
    else:
        print("✓ ALL PRECISION CHECKS PASSED")
        print("\nNext: Manual review of message quality")
        print("  - Do angles feel derived or imposed?")
        print("  - Are angles within channels differentiated?")
        print("  - Do kernel references make sense?")
        return True

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_stage_3.py <messages_path> [kernel_path] [audience_path]")
        print("  messages_path: Path to message matrix JSON")
        print("  kernel_path: Path to text kernel JSON (default: To_Kill_a_Mockingbird_kernel_v5_1.json)")
        print("  audience_path: Path to audience profile JSON (default: outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json)")
        sys.exit(1)
    
    messages_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    audience_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json"
    
    is_valid = validate_message_matrix(messages_path, kernel_path, audience_path)
    
    sys.exit(0 if is_valid else 1)


