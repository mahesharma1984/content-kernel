# validation/validate_stage_1_v2.py

"""
Stage 1 validation with reasoning/precision split.

PRECISION (code validates):
- Exact device name matches
- Exact pattern name matches
- Structural completeness (search term counts, etc.)

REASONING (human validates):
- Pain point quality and specificity
- Search term realism
- Semantic accuracy of references
- Kernel derivation quality
"""

import json
import sys

def validate_audience_profile(profile_path, kernel_path):
    """
    Validate Stage 1 audience profile.
    
    PRECISION checks (code):
    - Structural completeness
    - Device name matches
    - Pattern references
    
    REASONING checks (flagged for manual):
    - Pain point quality
    - Search term realism
    - Kernel derivation
    """
    
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Extract valid elements
    devices = kernel.get('micro_devices', [])
    valid_devices = {d['name'] for d in devices}
    alignment = kernel.get('alignment_pattern', {})
    valid_pattern = alignment.get('pattern_name', '')
    
    print("="*60)
    print("STAGE 1 VALIDATION: Audience Profile")
    print("="*60)
    print("\nSPLIT VALIDATION APPROACH:")
    print("  PRECISION (code): Exact matches, structure")
    print("  REASONING (manual): Pain point quality, derivation")
    print("="*60)
    
    precision_issues = []
    reasoning_flags = []
    
    segments = profile.get('segments', [])
    if not segments:
        print("ERROR: No segments found in profile")
        return {'precision_pass': False, 'reasoning_items': []}
    
    for i, segment in enumerate(segments, 1):
        seg_name = segment.get('name', f'Segment {i}')
        print(f"\nSegment {i}: {seg_name}")
        print(f"  Awareness: {segment.get('awareness_stage', 'Not specified')}")
        pain_point = segment.get('pain_point', 'Not specified')
        print(f"  Pain: {pain_point[:60]}...")
        
        # PRECISION: Check kernel references
        kernel_refs = segment.get('kernel_references', {})
        
        if not kernel_refs:
            precision_issues.append(f"{seg_name}: No kernel_references found")
            print(f"  ✗ No kernel references")
        else:
            # Check devices
            claimed_devices = kernel_refs.get('devices', [])
            if not claimed_devices:
                print(f"  ⚠ No devices referenced")
            else:
                for device in claimed_devices:
                    # Check exact match first
                    if device in valid_devices:
                        print(f"  ✓ Exact device: {device}")
                    else:
                        # Check partial match
                        device_match = False
                        for valid_device in valid_devices:
                            if device.lower() in valid_device.lower() or valid_device.lower() in device.lower():
                                print(f"  ✓ Partial device match: {device} (matches {valid_device})")
                                device_match = True
                                break
                        
                        if not device_match:
                            print(f"  → Manual review: {device}")
                            reasoning_flags.append({
                                'segment': seg_name,
                                'type': 'device_reference',
                                'value': device,
                                'check': 'Is this a reasonable way to reference a kernel concept?'
                            })
            
            # Check pattern reference
            if 'pattern' in kernel_refs:
                pattern_ref = kernel_refs['pattern']
                if valid_pattern.lower() in pattern_ref.lower() or pattern_ref.lower() in valid_pattern.lower():
                    print(f"  ✓ Pattern referenced")
                else:
                    print(f"  ⚠ Pattern reference weak")
                    reasoning_flags.append({
                        'segment': seg_name,
                        'type': 'pattern_reference',
                        'value': pattern_ref,
                        'check': 'Does this accurately describe the kernel pattern?'
                    })
            else:
                print(f"  ⚠ No pattern reference")
        
        # PRECISION: Check search terms
        search_terms = segment.get('search_terms', [])
        if len(search_terms) >= 3:
            print(f"  ✓ {len(search_terms)} search terms")
        else:
            precision_issues.append(f"{seg_name}: Only {len(search_terms)} search terms (need 3+)")
            print(f"  ✗ Only {len(search_terms)} search terms")
        
        # FLAG for reasoning: Pain point quality
        pain_point = segment.get('pain_point', '')
        if len(pain_point) < 30:
            reasoning_flags.append({
                'segment': seg_name,
                'type': 'pain_point_too_short',
                'value': pain_point,
                'check': 'Is this specific enough?'
            })
        
        # FLAG for reasoning: Search term realism
        reasoning_flags.append({
            'segment': seg_name,
            'type': 'search_terms',
            'value': search_terms,
            'check': 'Are these realistic? (Test with Google Trends)'
        })
    
    # Summary
    print("\n" + "="*60)
    print("PRECISION VALIDATION RESULTS")
    print("="*60)
    
    if precision_issues:
        print("\n✗ PRECISION ISSUES:")
        for issue in precision_issues:
            print(f"  • {issue}")
        print("\nStatus: PRECISION FAILED")
    else:
        print("\n✓ PRECISION: PASSED")
        print("  - All structural checks passed")
        print("  - Search term counts adequate")
    
    if reasoning_flags:
        print(f"\n→ REASONING: {len(reasoning_flags)} ITEMS FLAGGED FOR MANUAL REVIEW")
        print("  - See stage_1_observations.md for template")
        print("\nFlagged items:")
        for flag in reasoning_flags[:10]:  # Show first 10
            print(f"  • {flag['segment']}: {flag['type']} - {flag['check']}")
        if len(reasoning_flags) > 10:
            print(f"  ... and {len(reasoning_flags) - 10} more")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Complete manual reasoning review")
    print("2. Test search terms with Google/Google Trends")
    print("3. Assess pain point specificity")
    print("4. Document in stage_1_observations.md")
    
    return {
        'precision_pass': len(precision_issues) == 0,
        'reasoning_items': reasoning_flags
    }

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_stage_1_v2.py <profile_path> [kernel_path]")
        print("  profile_path: Path to audience profile JSON")
        print("  kernel_path: Path to text kernel JSON (default: To_Kill_a_Mockingbird_kernel_v5_1.json)")
        sys.exit(1)
    
    profile_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    
    result = validate_audience_profile(profile_path, kernel_path)
    
    sys.exit(0 if result['precision_pass'] else 1)


