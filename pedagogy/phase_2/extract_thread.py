# phase_2/extract_thread.py

import json
import sys
import os

def extract_core_thread(evaluations_path, output_path):
    """
    Extract the winning thread for use in Stage 2.
    
    PRECISION task: Code does this.
    """
    
    with open(evaluations_path, 'r') as f:
        evals = json.load(f)
    
    winner = evals['winner']
    
    # Assemble core_thread object
    core_thread = {
        "core_message": winner['core_message'],
        "agitation_register": winner['agitation_register'],
        "solution_register": winner['solution_register'],
        "selection_rationale": winner['why_it_wins'],
        "kernel_pattern_reference": winner.get('kernel_pattern_reference', ''),
        "total_score": winner['total_score'],
        "source_angle": winner['angle_id']
    }
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(core_thread, f, indent=2)
    
    print(f"✓ Core thread extracted to: {output_path}")
    print(f"\nThread: {core_thread['core_message']}")
    
    return core_thread

# Usage
if __name__ == "__main__":
    evaluations_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    
    thread = extract_core_thread(evaluations_path, output_path)
