# validation/validate_stage_4.py

import json
import sys

def validate_and_confirm_winner(evaluations_path, kernel_path):
    """
    Validate thread selection and potentially override with human judgment.
    
    REASONING (Claude): Scored all angles
    PRECISION (Code): Select highest score
    JUDGMENT (Human): Confirm or override
    """
    
    with open(evaluations_path, 'r') as f:
        evals = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    print("="*60)
    print("STAGE 4 VALIDATION: Thread Selection")
    print("="*60)
    
    # Display top 5 scoring angles
    evaluations = evals['evaluations']
    sorted_evals = sorted(evaluations, key=lambda x: x['total_score'], reverse=True)
    
    print("\nTOP 5 SCORING ANGLES:\n")
    for i, angle in enumerate(sorted_evals[:5], 1):
        print(f"{i}. [{angle['angle_id']}] Score: {angle['total_score']}/40")
        print(f"   Message: {angle['message'][:80]}...")
        print(f"   Breakdown: M={angle['scores']['memorable']}, "
              f"D={angle['scores']['differentiating']}, "
              f"P={angle['scores']['pattern_anchored']}, "
              f"F={angle['scores']['funnel_continuous']}")
        print()
    
    # Check winner
    winner = evals['winner']
    highest_scoring = sorted_evals[0]
    
    print("="*60)
    print("WINNER VALIDATION:")
    print("="*60)
    
    # Check: Is winner actually highest scoring?
    if winner['angle_id'] != highest_scoring['angle_id']:
        print("⚠ WARNING: Declared winner is not highest scoring angle")
        print(f"  Declared: {winner['angle_id']} ({winner['total_score']})")
        print(f"  Highest: {highest_scoring['angle_id']} ({highest_scoring['total_score']})")
        print("\n  This may be intentional if other factors matter.")
        print("  Review justification and decide.")
    else:
        print(f"✓ Winner is highest scoring: {winner['angle_id']} ({winner['total_score']}/40)")
    
    # Check: Does winner score >= 7 on all criteria?
    print("\nCRITERIA BREAKDOWN:")
    winner_eval = next(e for e in evaluations if e['angle_id'] == winner['angle_id'])
    
    criteria_ok = True
    for criterion, score in winner_eval['scores'].items():
        status = "✓" if score >= 7 else "⚠"
        print(f"  {status} {criterion}: {score}/10")
        if score < 7:
            print(f"      Justification: {winner_eval['justifications'][criterion][:80]}...")
            criteria_ok = False
    
    if not criteria_ok:
        print("\n⚠ Winner has weak scores on some criteria")
        print("  Consider: Is this the best available, or should we regenerate messages?")
    
    # Check: Pattern reference
    alignment = kernel.get('alignment_pattern', {})
    pattern = alignment.get('pattern_name', 'Not found')
    pattern_ref = winner.get('kernel_pattern_reference', '')
    
    print(f"\nPATTERN CONNECTION:")
    print(f"  Kernel pattern: {pattern}")
    print(f"  Winner references: {pattern_ref}")
    
    if pattern.lower() in pattern_ref.lower() or pattern_ref.lower() in pattern.lower():
        print("  ✓ Pattern referenced")
    else:
        print("  ⚠ Pattern reference may be weak")
    
    # Check: Agitation and solution registers exist
    print(f"\nREGISTERS:")
    if winner.get('agitation_register') and len(winner['agitation_register']) > 20:
        print(f"  ✓ Agitation register defined")
        print(f"    → {winner['agitation_register'][:80]}...")
    else:
        print(f"  ✗ Agitation register missing or weak")
    
    if winner.get('solution_register') and len(winner['solution_register']) > 20:
        print(f"  ✓ Solution register defined")
        print(f"    → {winner['solution_register'][:80]}...")
    else:
        print(f"  ✗ Solution register missing or weak")
    
    # Final decision prompt
    print("\n" + "="*60)
    print("CONFIRM WINNER?")
    print("="*60)
    print("\nReview the winner above. Then:")
    print("  1. Accept as-is → Use this thread for Stage 2")
    print("  2. Override → Manually select different angle")
    print("  3. Regenerate → Go back to Phase 1, create better angles")
    print("\nDocument your decision in stage_4_observations.md")

# Usage
if __name__ == "__main__":
    evaluations_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json"
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    
    validate_and_confirm_winner(evaluations_path, kernel_path)
