# validation/validate_stage_1.py

import json
import sys

def validate_audience_profile(profile_path, kernel_path):
    """
    Validate that audience profile references real kernel elements.
    
    This is a PRECISION task (code does this, not Claude).
    """
    
    # Load files
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Extract all valid kernel element names (PRECISION)
    # v5.1 structure uses 'micro_devices'
    devices = kernel.get('micro_devices', [])
    valid_devices = {d['name'] for d in devices}
    
    alignment = kernel.get('alignment_pattern', {})
    valid_pattern = alignment.get('pattern_name', '')
    
    print("="*60)
    print("STAGE 1 VALIDATION: Audience Profile")
    print("="*60)
    
    issues = []
    
    segments = profile.get('segments', [])
    if not segments:
        print("ERROR: No segments found in profile")
        return False
    
    # Check each segment
    for i, segment in enumerate(segments, 1):
        seg_name = segment.get('name', f'Segment {i}')
        print(f"\nSegment {i}: {seg_name}")
        print(f"  Awareness: {segment.get('awareness_stage', 'Not specified')}")
        pain_point = segment.get('pain_point', 'Not specified')
        print(f"  Pain point: {pain_point[:60]}{'...' if len(pain_point) > 60 else ''}")
        
        # Validate kernel references (PRECISION)
        kernel_refs = segment.get('kernel_references', {})
        
        if not kernel_refs:
            issues.append(f"{seg_name}: No kernel_references found")
            print(f"  ✗ No kernel references")
        else:
            # Check device references
            claimed_devices = kernel_refs.get('devices', [])
            if not claimed_devices:
                issues.append(f"{seg_name}: No devices referenced")
                print(f"  ⚠ No devices referenced")
            else:
                for device in claimed_devices:
                    # Allow partial matches for device names
                    device_match = False
                    for valid_device in valid_devices:
                        if device.lower() in valid_device.lower() or valid_device.lower() in device.lower():
                            device_match = True
                            print(f"  ✓ Valid device reference: {device} (matches {valid_device})")
                            break
                    
                    if not device_match:
                        issues.append(f"{seg_name}: References non-existent device '{device}'")
                        print(f"  ✗ Invalid device reference: {device}")
            
            # Check pattern reference
            pattern_ref = kernel_refs.get('pattern', '')
            if pattern_ref:
                if valid_pattern.lower() in pattern_ref.lower() or pattern_ref.lower() in valid_pattern.lower():
                    print(f"  ✓ Pattern referenced")
                else:
                    print(f"  ⚠ Pattern reference may be weak")
                    print(f"     Expected: {valid_pattern}")
                    print(f"     Got: {pattern_ref[:60]}")
            else:
                print(f"  ⚠ No pattern reference")
        
        # Check search terms are present
        search_terms = segment.get('search_terms', [])
        if len(search_terms) < 3:
            issues.append(f"{seg_name}: Only {len(search_terms)} search terms (need 3+)")
            print(f"  ⚠ Only {len(search_terms)} search terms")
        else:
            print(f"  ✓ {len(search_terms)} search terms provided")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print("VALIDATION ISSUES:")
        for issue in issues:
            print(f"  ✗ {issue}")
        print("\nStatus: NEEDS REVISION")
        return False
    else:
        print("✓ ALL CHECKS PASSED")
        print("\nStatus: VALIDATED")
        return True

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_stage_1.py <profile_path> [kernel_path]")
        print("  profile_path: Path to audience profile JSON")
        print("  kernel_path: Path to text kernel JSON (default: To_Kill_a_Mockingbird_kernel_v5_1.json)")
        sys.exit(1)
    
    profile_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    
    is_valid = validate_audience_profile(profile_path, kernel_path)
    
    if not is_valid:
        print("\n⚠ Review the audience profile and revise as needed.")
        sys.exit(1)



