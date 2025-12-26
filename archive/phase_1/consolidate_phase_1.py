# phase_1/consolidate_phase_1.py
# Version: 1.0
# Date: December 17, 2025
# Purpose: Consolidate stages 1, 3, 5A into single phase 1 kernel

import json
import os
import sys
from datetime import datetime

def consolidate_phase_1(book_code, stage_1_path, stage_3_path, stage_5a_path, text_kernel_path, output_dir):
    """Consolidate Phase 1 stages into single kernel."""
    
    # Load stage outputs
    with open(stage_1_path, 'r') as f:
        stage_1 = json.load(f)
    
    with open(stage_3_path, 'r') as f:
        stage_3 = json.load(f)
    
    with open(stage_5a_path, 'r') as f:
        stage_5a = json.load(f)
    
    # Get book title from text kernel
    with open(text_kernel_path, 'r') as f:
        text_kernel = json.load(f)
    book_title = text_kernel.get('metadata', {}).get('title', book_code)
    
    # Assemble phase 1 kernel
    phase_1_kernel = {
        "metadata": {
            "book_title": book_title,
            "book_code": book_code,
            "kernel_type": "content_kernel",
            "kernel_version": "1.0",
            "phase": "1",
            "source_text_kernel": os.path.basename(text_kernel_path),
            "created": datetime.now().strftime("%Y-%m-%d"),
            "stages_included": ["1", "3", "5A"]
        },
        "stage_1_audience": {
            "segments": stage_1.get('segments', []),
            "high_intent_searches": stage_1.get('high_intent_searches', []),
            "observations": stage_1.get('observations', '')
        },
        "stage_3_messages": {
            "angles": stage_3.get('angles', []),
            "observations": stage_3.get('observations', '')
        },
        "stage_5a_drafts": {
            "selection_rationale": stage_5a.get('selection_rationale', {}),
            "drafts": stage_5a.get('drafts', []),
            "observations": stage_5a.get('observations', {})
        }
    }
    
    # Save kernel
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{book_code}_content_kernel_phase_1.json")
    
    with open(output_path, 'w') as f:
        json.dump(phase_1_kernel, f, indent=2)
    
    print(f"✓ Phase 1 kernel saved: {output_path}")
    return phase_1_kernel

# Usage
if __name__ == "__main__":
    book_code = sys.argv[1] if len(sys.argv) > 1 else "TKAM"
    
    consolidate_phase_1(
        book_code=book_code,
        stage_1_path=f"outputs/manual_exploration/phase_1/{book_code}_stage_1_audience.json",
        stage_3_path=f"outputs/manual_exploration/phase_1/{book_code}_stage_3_messages.json",
        stage_5a_path=f"outputs/manual_exploration/phase_1/{book_code}_stage_5a_drafts.json",
        text_kernel_path="To_Kill_a_Mockingbird_kernel_v5_1.json",
        output_dir="outputs/kernels"
    )


