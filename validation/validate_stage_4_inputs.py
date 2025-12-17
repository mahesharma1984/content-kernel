# validation/validate_stage_4_inputs.py

import json
import sys

def validate_stage_4_inputs(messages_path, drafts_5a_path):
    """
    PRECISION validation: Verify Stage 4 will evaluate only drafted angles.
    
    This is a pre-execution check. Call before running Stage 4.
    """
    
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(drafts_5a_path, 'r') as f:
        drafts_5a = json.load(f)
    
    total_angles = len(messages['angles'])
    drafted_count = len(drafts_5a['drafts'])
    drafted_indices = {d['angle_index'] for d in drafts_5a['drafts']}
    
    print("="*60)
    print("STAGE 4 INPUT VALIDATION")
    print("="*60)
    
    print(f"\nStage 3: {total_angles} total angles")
    print(f"Stage 5A: {drafted_count} angles drafted")
    print(f"Drafted indices: {sorted(drafted_indices)}")
    
    # Check 1: Some angles were drafted
    if drafted_count == 0:
        print("\n✗ ERROR: No angles drafted in Stage 5A")
        print("  Cannot run Stage 4 with empty draft set")
        return False
    
    # Check 2: Drafted count <= total count
    if drafted_count > total_angles:
        print(f"\n✗ ERROR: More drafts ({drafted_count}) than angles ({total_angles})")
        print("  Stage 5A data may be corrupted")
        return False
    
    # Check 3: All drafted indices are valid
    max_index = max(drafted_indices)
    if max_index > total_angles:
        print(f"\n✗ ERROR: Draft references angle {max_index} but only {total_angles} exist")
        print("  Index mismatch between Stage 3 and Stage 5A")
        return False
    
    # Check 4: Indices are unique
    if len(drafted_indices) != drafted_count:
        print(f"\n✗ ERROR: Duplicate angle indices in Stage 5A")
        print(f"  {drafted_count} drafts but {len(drafted_indices)} unique indices")
        return False
    
    print(f"\n✓ VALIDATION PASSED")
    print(f"  Stage 4 will evaluate {drafted_count} drafted angles")
    print(f"  Winner will be from this set of {drafted_count} angles")
    
    return True

# Usage
if __name__ == "__main__":
    messages_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    drafts_5a_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_1/TKAM_stage_5a_drafts.json"
    
    valid = validate_stage_4_inputs(messages_path, drafts_5a_path)
    sys.exit(0 if valid else 1)

