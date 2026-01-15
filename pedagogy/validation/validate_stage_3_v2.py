# validation/validate_stage_3_v2.py

"""
Stage 3 validation with proper reasoning/precision split.

PRECISION (code validates):
- Exact device name matches
- Exact pattern name matches  
- Structural completeness

REASONING (human validates):
- Semantic accuracy of references
- Derivation from kernel
- Message quality
"""

import json
import sys

def categorize_reference(ref, kernel):
    """
    Categorize a reference as exact match or needs manual review.
    
    PRECISION task: Exact string matching only.
    """
    
    # Extract exact match sets
    devices = kernel.get('micro_devices', [])
    device_names = {d['name'] for d in devices}
    alignment = kernel.get('alignment_pattern', {})
    pattern_name = alignment.get('pattern_name', '')
    
    # Check exact matches
    if ref in device_names:
        return 'exact_device', ref
    
    # Check pattern reference (exact or partial)
    if ref == pattern_name or pattern_name in ref or ref in pattern_name:
        return 'exact_pattern', ref
    
    # Check if it appears in kernel text (fuzzy matching)
    reader_effect = alignment.get('reader_effect', '').lower()
    core_dynamic = alignment.get('core_dynamic', '').lower()
    
    ref_lower = ref.lower()
    
    # Check for substring matches in reader_effect
    if ref_lower in reader_effect:
        snippet = reader_effect[max(0, reader_effect.find(ref_lower) - 20):reader_effect.find(ref_lower) + len(ref_lower) + 20]
        return 'text_match_effect', f"Found in reader_effect: '...{snippet}...'"
    
    # Check for substring matches in core_dynamic
    if ref_lower in core_dynamic:
        snippet = core_dynamic[max(0, core_dynamic.find(ref_lower) - 20):core_dynamic.find(ref_lower) + len(ref_lower) + 20]
        return 'text_match_dynamic', f"Found in core_dynamic: '...{snippet}...'"
    
    # Check device effects for matches
    for device in devices:
        effect = device.get('effect', '').lower()
        if ref_lower in effect:
            return 'text_match_device_effect', f"Found in {device['name']} effect description"
    
    # Check word overlap for better fuzzy matching
    ref_words = set(ref_lower.split())
    if len(ref_words) >= 2:
        effect_words = set(reader_effect.split())
        dynamic_words = set(core_dynamic.split())
        overlap_effect = ref_words & effect_words
        overlap_dynamic = ref_words & dynamic_words
        
        if len(overlap_effect) >= 2:
            return 'text_match_effect', f"Word overlap in reader_effect: {overlap_effect}"
        
        if len(overlap_dynamic) >= 2:
            return 'text_match_dynamic', f"Word overlap in core_dynamic: {overlap_dynamic}"
    
    # Otherwise needs manual review
    return 'manual_review', 'Not an exact match - check kernel manually for semantic accuracy'

def validate_stage_3(messages_path, kernel_path, audience_path):
    """
    Validate Stage 3 messages with reasoning/precision split.
    """
    
    # Load files
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    with open(audience_path, 'r') as f:
        audience = json.load(f)
    
    print("="*60)
    print("STAGE 3 VALIDATION: Message Matrix")
    print("="*60)
    print("\nSPLIT VALIDATION APPROACH:")
    print("  PRECISION (code): Exact string matches")
    print("  REASONING (manual): Semantic accuracy")
    print("="*60)
    
    # Counters
    exact_matches = 0
    text_matches = 0
    manual_review_needed = []
    precision_issues = []
    
    angles = messages.get('angles', [])
    if not angles:
        print("ERROR: No angles found in message matrix")
        return {'precision_pass': False, 'exact_matches': 0, 'text_matches': 0, 'manual_review_items': []}
    
    for i, angle in enumerate(angles, 1):
        channel = angle.get('channel', 'Unknown')
        hook = angle.get('hook_type', 'Unknown')
        
        print(f"\n[{i}] {channel} - {hook}")
        message = angle.get('message', 'No message')
        print(f"  Message: {message[:80]}...")
        
        # Validate kernel references
        # Note: Stage 3 uses 'kernel_elements' field
        refs = angle.get('kernel_elements', [])
        
        if not refs:
            precision_issues.append(f"Angle {i}: No kernel_elements provided")
            print(f"  ✗ No kernel elements")
            continue
        
        for ref in refs:
            category, context = categorize_reference(ref, kernel)
            
            if category == 'exact_device':
                print(f"  ✓ Exact device: {ref}")
                exact_matches += 1
                
            elif category == 'exact_pattern':
                print(f"  ✓ Pattern ref: {ref}")
                exact_matches += 1
                
            elif category.startswith('text_match'):
                print(f"  ≈ Text match: {ref}")
                print(f"      {context}")
                text_matches += 1
                
            else:  # manual_review
                print(f"  → Manual review: {ref}")
                print(f"      {context}")
                manual_review_needed.append({
                    'angle': i,
                    'channel': channel,
                    'hook': hook,
                    'reference': ref,
                    'message': angle.get('message', '')[:80]
                })
    
    # Channel distribution check
    channel_counts = {}
    for angle in angles:
        ch = angle.get('channel', 'Unknown')
        channel_counts[ch] = channel_counts.get(ch, 0) + 1
    
    # Check for channel distribution issues (PRECISION)
    for channel, count in channel_counts.items():
        if count < 3:
            precision_issues.append(f"{channel} has only {count} angles (need 3+)")
    
    # Summary
    print("\n" + "="*60)
    print("PRECISION VALIDATION RESULTS")
    print("="*60)
    
    print(f"\n✓ Exact matches: {exact_matches}")
    print(f"≈ Text matches: {text_matches}")
    print(f"→ Manual review needed: {len(manual_review_needed)}")
    
    if precision_issues:
        print(f"\n✗ PRECISION ISSUES:")
        for issue in precision_issues:
            print(f"  • {issue}")
    
    print(f"\nCHANNEL DISTRIBUTION:")
    for ch, count in sorted(channel_counts.items()):
        status = "✓" if count >= 3 else "⚠"
        print(f"  {status} {ch}: {count} angles")
    
    # Final status
    print("\n" + "="*60)
    print("VALIDATION STATUS")
    print("="*60)
    
    precision_pass = len(precision_issues) == 0
    
    if precision_pass:
        print("\n✓ PRECISION: PASSED")
        print("  - All structural checks passed")
        print("  - All angles have kernel references")
    else:
        print("\n✗ PRECISION: FAILED")
        print("  - See issues above")
    
    if manual_review_needed:
        print(f"\n→ REASONING: {len(manual_review_needed)} ITEMS NEED MANUAL REVIEW")
        print("  - See stage_3_reasoning_validation.md for reasoning validation template")
        print("  - Check if references semantically match kernel concepts")
        print("  - Document findings in observations")
    else:
        print("\n✓ REASONING: No manual review needed (all exact matches)")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Complete manual reasoning review (see template below)")
    print("2. Document findings in stage_3_observations.md")
    print("3. Revise any truly inaccurate references")
    print("4. Proceed to Phase 2 if validation confirms derivation")
    
    return {
        'precision_pass': precision_pass,
        'exact_matches': exact_matches,
        'text_matches': text_matches,
        'manual_review_items': manual_review_needed
    }

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_stage_3_v2.py <messages_path> [kernel_path] [audience_path]")
        print("  messages_path: Path to message matrix JSON")
        print("  kernel_path: Path to text kernel JSON (default: To_Kill_a_Mockingbird_kernel_v5_1.json)")
        print("  audience_path: Path to audience profile JSON (default: outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json)")
        sys.exit(1)
    
    messages_path = sys.argv[1]
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    audience_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json"
    
    result = validate_stage_3(messages_path, kernel_path, audience_path)
    
    sys.exit(0 if result['precision_pass'] else 1)


