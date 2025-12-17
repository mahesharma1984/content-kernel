# validation/validate_stage_5a.py

"""
Stage 5A validation with proper reasoning/precision split.

PRECISION (code validates):
- All angles have drafts
- All drafts have 2+ variations
- Structural completeness

REASONING (human validates):
- Kernel reference accuracy
- Draft quality
- Which angles produce best content
"""

import json
import sys

def validate_stage_5a(drafts_path, kernel_path, messages_path):
    """Validate Stage 5A drafts using reasoning/precision split."""
    
    # Load files
    with open(drafts_path, 'r') as f:
        drafts = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    # Build reference sets for validation (v5.1 structure)
    devices = kernel.get('micro_devices', [])
    device_names = {d['name'].lower() for d in devices}
    
    alignment = kernel.get('alignment_pattern', {})
    pattern_name = alignment.get('pattern_name', '').lower()
    
    print("="*60)
    print("STAGE 5A VALIDATION")
    print("="*60)
    
    # PRECISION checks
    precision_issues = []
    
    # Check: Do we have drafts for all angles?
    angles = messages.get('angles', [])
    angle_count = len(angles)
    draft_list = drafts.get('drafts', [])
    draft_count = len(draft_list)
    
    if draft_count < angle_count:
        precision_issues.append(f"Missing drafts: {angle_count} angles, only {draft_count} drafted")
    
    # Check: Does each draft have variations?
    for draft in draft_list:
        angle_idx = draft.get('angle_index', '?')
        variations = draft.get('variations', [])
        if len(variations) < 2:
            precision_issues.append(f"Angle {angle_idx}: Less than 2 variations (has {len(variations)})")
    
    print("\nPRECISION CHECKS:")
    if precision_issues:
        for issue in precision_issues:
            print(f"  ✗ {issue}")
        print("\nStatus: PRECISION ISSUES FOUND")
    else:
        print("  ✓ All angles have drafts")
        print("  ✓ All drafts have 2+ variations")
        print("\nStatus: PRECISION PASSED")
    
    # REASONING flags (for manual review)
    reasoning_flags = []
    
    for draft in draft_list:
        angle_idx = draft.get('angle_index', '?')
        channel = draft.get('channel', 'Unknown')
        
        for i, var in enumerate(draft.get('variations', []), 1):
            # Flag kernel references for review
            refs = var.get('kernel_references', [])
            for ref in refs:
                ref_str = str(ref).lower()
                # Check if it's an exact device name match or pattern match
                if ref_str not in device_names and ref_str != pattern_name:
                    # Check for partial matches in device names
                    is_partial_match = any(ref_str in name or name in ref_str for name in device_names)
                    if not is_partial_match:
                        reasoning_flags.append({
                            'angle': angle_idx,
                            'variation': i,
                            'channel': channel,
                            'reference': ref,
                            'check': 'Verify this references kernel accurately'
                        })
    
    print("\nREASONING FLAGS (manual review):")
    if reasoning_flags:
        # Show first 15 flags
        for flag in reasoning_flags[:15]:
            print(f"  → Angle {flag['angle']}, Var {flag['variation']} ({flag['channel']}): '{flag['reference']}'")
        if len(reasoning_flags) > 15:
            print(f"  ... and {len(reasoning_flags) - 15} more")
        print(f"\nTotal items for manual review: {len(reasoning_flags)}")
    else:
        print("  ✓ All references are exact device/pattern matches")
    
    # Summary statistics
    total_variations = sum(len(d.get('variations', [])) for d in draft_list)
    channels = {}
    for draft in draft_list:
        ch = draft.get('channel', 'Unknown')
        channels[ch] = channels.get(ch, 0) + 1
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total angles: {angle_count}")
    print(f"Total drafts: {draft_count}")
    print(f"Total variations: {total_variations}")
    print(f"Average variations per draft: {total_variations / draft_count if draft_count > 0 else 0:.1f}")
    print("\nChannel distribution:")
    for ch, count in sorted(channels.items()):
        print(f"  - {ch}: {count} drafts")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review flagged references for semantic accuracy")
    print("2. Note which drafts are strongest (for Phase 2)")
    print("3. Document observations in stage_5a_observations.md")
    print("4. Proceed to Phase 2 (Selection)")
    print("="*60)
    
    return {
        'precision_pass': len(precision_issues) == 0,
        'precision_issues': precision_issues,
        'reasoning_flags': reasoning_flags,
        'total_variations': total_variations
    }

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_stage_5a.py <drafts_path> [kernel_path] [messages_path]")
        print("  drafts_path: Path to stage 5a drafts JSON")
        print("  kernel_path: Path to kernel JSON (default: To_Kill_a_Mockingbird_kernel_v5_1.json)")
        print("  messages_path: Path to stage 3 messages JSON (default: outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json)")
        sys.exit(1)
    
    drafts_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    messages_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    
    result = validate_stage_5a(drafts_path, kernel_path, messages_path)
    
    sys.exit(0 if result['precision_pass'] else 1)

