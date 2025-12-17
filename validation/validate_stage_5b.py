# validation/validate_stage_5b.py

import json
import sys

def validate_stage_5b(content_path, channels_path, kernel_path):
    """Validate Stage 5B output with reasoning/precision split."""
    
    with open(content_path, 'r') as f:
        content = json.load(f)
    
    with open(channels_path, 'r') as f:
        channels = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Get device names from kernel (v5.1 structure)
    devices = kernel.get('micro_devices', [])
    device_names = {d['name'].lower() for d in devices}
    
    print("="*60)
    print("STAGE 5B VALIDATION")
    print("="*60)
    
    # PRECISION checks
    precision_issues = []
    
    content_blocks = content.get('content_blocks', {})
    expected_channels = ['social', 'youtube', 'seo', 'guide']
    
    for channel in expected_channels:
        # Normalize channel name (case-insensitive)
        block = None
        for key in content_blocks:
            if key.lower() == channel.lower():
                block = content_blocks[key]
                break
        
        if not block:
            precision_issues.append(f"Missing content block: {channel}")
            continue
        
        if not block.get('final_content'):
            precision_issues.append(f"{channel}: No final content")
        
        if not block.get('constraint_validation'):
            precision_issues.append(f"{channel}: No constraint validation")
    
    print("\nPRECISION CHECKS:")
    if precision_issues:
        for issue in precision_issues:
            print(f"  ✗ {issue}")
        print("\nStatus: PRECISION ISSUES")
    else:
        print("  ✓ All channels have content blocks")
        print("  ✓ All blocks have final content")
        print("  ✓ All blocks have validation")
        print("\nStatus: PRECISION PASSED")
    
    # REASONING flags (manual review)
    reasoning_flags = []
    
    for channel, block in content_blocks.items():
        validation = block.get('constraint_validation', {})
        
        # Check self-reported validation
        if not validation.get('job_accomplished'):
            reasoning_flags.append({
                'channel': channel,
                'issue': 'Job not accomplished (self-reported)',
                'check': 'Review if content does the channel job'
            })
        
        if not validation.get('thread_visible'):
            reasoning_flags.append({
                'channel': channel,
                'issue': 'Thread not visible (self-reported)',
                'check': 'Review if core message is recognizable'
            })
        
        # Check kernel references
        refs = block.get('kernel_references', [])
        for ref in refs:
            if isinstance(ref, str) and ref.lower() not in device_names:
                # Check if it's a partial match or pattern reference
                matched = False
                for device_name in device_names:
                    if ref.lower() in device_name or device_name in ref.lower():
                        matched = True
                        break
                if not matched:
                    reasoning_flags.append({
                        'channel': channel,
                        'reference': ref,
                        'check': 'Verify this kernel reference'
                    })
    
    print("\nREASONING FLAGS (manual review):")
    if reasoning_flags:
        for flag in reasoning_flags:
            print(f"  → {flag['channel']}: {flag.get('issue', flag.get('reference', 'Check needed'))}")
        print(f"\nTotal flags: {len(reasoning_flags)}")
    else:
        print("  ✓ No issues flagged")
    
    # Overall status
    overall = content.get('overall_validation', {})
    print("\n" + "="*60)
    print("OVERALL STATUS:")
    print(f"  All constraints met: {overall.get('all_constraints_met', 'Unknown')}")
    print(f"  Ready for rendering: {overall.get('ready_for_rendering', 'Unknown')}")
    
    if not overall.get('all_constraints_met'):
        print("\n  Issues reported:")
        for issue in overall.get('issues_found', ['None listed']):
            print(f"    - {issue}")
    
    print("\nNEXT STEPS:")
    if overall.get('ready_for_rendering'):
        print("  → Proceed to asset rendering (Layer 1)")
    else:
        print("  → Address flagged issues")
        print("  → Re-run 5B refinement if needed")
    print("="*60)

# Usage
if __name__ == "__main__":
    content_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_content.json"
    channels_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    kernel_path = sys.argv[3] if len(sys.argv) > 3 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    
    validate_stage_5b(content_path, channels_path, kernel_path)

