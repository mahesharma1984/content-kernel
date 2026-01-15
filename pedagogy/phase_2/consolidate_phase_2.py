# phase_2/consolidate_phase_2.py
# Version: 1.0
# Date: December 17, 2025
# Purpose: Consolidate stages 4, 2, 5B into single phase 2 kernel

import json
import os
import sys
from datetime import datetime

def consolidate_phase_2(book_code, stage_4_eval_path, stage_4_thread_path, stage_2_path, stage_5b_path, phase_1_kernel_path, output_dir):
    """Consolidate Phase 2 stages into single kernel."""
    
    # Load stage outputs
    with open(stage_4_eval_path, 'r') as f:
        stage_4_eval = json.load(f)
    
    with open(stage_4_thread_path, 'r') as f:
        stage_4_thread = json.load(f)
    
    with open(stage_2_path, 'r') as f:
        stage_2 = json.load(f)
    
    with open(stage_5b_path, 'r') as f:
        stage_5b = json.load(f)
    
    # Get book title from phase 1 kernel
    with open(phase_1_kernel_path, 'r') as f:
        phase_1 = json.load(f)
    book_title = phase_1.get('metadata', {}).get('book_title', book_code)
    
    # Assemble phase 2 kernel
    phase_2_kernel = {
        "metadata": {
            "book_title": book_title,
            "book_code": book_code,
            "kernel_type": "content_kernel",
            "kernel_version": "1.0",
            "phase": "2",
            "source_phase_1": os.path.basename(phase_1_kernel_path),
            "created": datetime.now().strftime("%Y-%m-%d"),
            "stages_included": ["4", "2", "5B"],
            "human_review_complete": False  # Set to True after review
        },
        "stage_4_selection": {
            "evaluations": stage_4_eval.get('evaluations', []),
            "winning_thread": {
                "core_message": stage_4_thread.get('core_message', ''),
                "agitation_register": stage_4_thread.get('agitation_register', ''),
                "solution_register": stage_4_thread.get('solution_register', ''),
                "selection_rationale": stage_4_thread.get('selection_rationale', ''),
                "total_score": stage_4_thread.get('total_score', 0),
                "source_angle": stage_4_thread.get('source_angle', ''),
                "kernel_pattern_reference": stage_4_thread.get('kernel_pattern_reference', '')
            }
        },
        "stage_2_channels": {
            "thread_summary": stage_2.get('thread_summary', ''),
            "social": stage_2.get('social', {}),
            "youtube": stage_2.get('youtube', {}),
            "seo": stage_2.get('seo', {}),
            "guide": stage_2.get('guide', {})
        },
        "stage_5b_content": {
            "content_blocks": stage_5b.get('content_blocks', {}),
            "overall_validation": stage_5b.get('overall_validation', {})
        }
    }
    
    # Save kernel
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{book_code}_content_kernel_phase_2.json")
    
    with open(output_path, 'w') as f:
        json.dump(phase_2_kernel, f, indent=2)
    
    print(f"✓ Phase 2 kernel saved: {output_path}")
    return phase_2_kernel

# Usage
if __name__ == "__main__":
    book_code = sys.argv[1] if len(sys.argv) > 1 else "TKAM"
    
    consolidate_phase_2(
        book_code=book_code,
        stage_4_eval_path=f"outputs/manual_exploration/phase_2/{book_code}_v6_1_stage_4_evaluations.json",
        stage_4_thread_path=f"outputs/manual_exploration/phase_2/{book_code}_v6_1_stage_4_thread.json",
        stage_2_path=f"outputs/manual_exploration/phase_2/{book_code}_v6_1_stage_2_channels.json",
        stage_5b_path=f"outputs/manual_exploration/phase_2/{book_code}_v6_1_stage_5b_content.json",
        phase_1_kernel_path=f"outputs/kernels/{book_code}_content_kernel_phase_1.json",
        output_dir="outputs/kernels"
    )


