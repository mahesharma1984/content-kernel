# validation/validate_stage_5a.py

"""
Stage 5A validation with proper reasoning/precision split.

PRECISION (code validates):
- Selection rationale present
- Draft count is 8-12 (2-3 per channel × 4 channels)
- All drafts have 2+ variations
- Structural completeness

REASONING (human validates):
- Selection quality (did best angles get selected?)
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
    
    # Check: Selection rationale present
    if 'selection_rationale' not in drafts:
        precision_issues.append("Missing selection_rationale field")
    else:
        rationale = drafts.get('selection_rationale', {})
        expected_channels = {'social', 'youtube', 'seo', 'guide'}
        missing_channels = expected_channels - set(rationale.keys())
        if missing_channels:
            precision_issues.append(f"Missing selection_rationale for channels: {', '.join(missing_channels)}")
    
    # Check: Draft count is reasonable (8-12 total, 2-3 per channel)
    draft_list = drafts.get('drafts', [])
    draft_count = len(draft_list)
    
    if draft_count < 8:
        precision_issues.append(f"Too few drafts: {draft_count} (expected 8-12)")
    elif draft_count > 12:
        precision_issues.append(f"Too many drafts: {draft_count} (expected 8-12)")
    
    # Check: Channel distribution (2-3 per channel)
    by_channel = {}
    for draft in draft_list:
        channel = draft.get('channel', 'Unknown').lower()
        by_channel[channel] = by_channel.get(channel, 0) + 1
    
    for channel, count in by_channel.items():
        if count < 2:
            precision_issues.append(f"{channel} has only {count} drafts (need 2-3)")
        elif count > 3:
            precision_issues.append(f"{channel} has {count} drafts (should be 2-3)")
    
    # Check: Does each draft have variations?
    for draft in draft_list:
        angle_idx = draft.get('angle_index', '?')
        variations = draft.get('variations', [])
        if len(variations) < 2:
            precision_issues.append(f"Angle {angle_idx}: Less than 2 variations (has {len(variations)})")
    
    # Check: Selection reason present
    for draft in draft_list:
        if 'selection_reason' not in draft:
            precision_issues.append(f"Angle {draft.get('angle_index', '?')}: Missing selection_reason field")
    
    print("\nPRECISION CHECKS:")
    if precision_issues:
        for issue in precision_issues:
            print(f"  ✗ {issue}")
        print("\nStatus: PRECISION ISSUES FOUND")
    else:
        print("  ✓ Selection rationale present")
        print(f"  ✓ Draft count in range: {draft_count} (target: 8-12)")
        print("  ✓ Channel distribution correct (2-3 per channel)")
        print("  ✓ All drafts have 2+ variations")
        print("  ✓ All drafts have selection_reason")
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
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total angles available: {len(messages.get('angles', []))}")
    print(f"Total drafts selected: {draft_count}")
    print(f"Total variations: {total_variations}")
    print(f"Average variations per draft: {total_variations / draft_count if draft_count > 0 else 0:.1f}")
    print("\nChannel distribution:")
    for ch, count in sorted(by_channel.items()):
        status = "✓" if 2 <= count <= 3 else "⚠"
        print(f"  {status} {ch}: {count} drafts")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review selection rationale (did best angles get selected?)")
    print("2. Review flagged references for semantic accuracy")
    print("3. Note which drafts are strongest (for Phase 2)")
    print("4. Document observations in stage_5a_observations.md")
    print("5. Proceed to Phase 2 (Selection)")
    print("="*60)
    
    return {
        'precision_pass': len(precision_issues) == 0,
        'precision_issues': precision_issues,
        'reasoning_flags': reasoning_flags,
        'total_variations': total_variations,
        'draft_count': draft_count
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


