# utils/build_content_kernel.py
# Version: 1.0
# Date: December 17, 2025

import json
import os
import sys
from datetime import datetime

def build_content_kernel(book_code, checkpoint_dir, text_kernel_path, output_dir):
    """Build single content kernel from stage checkpoints."""
    
    # Load checkpoints
    def load_checkpoint(stage):
        patterns = [
            f"{checkpoint_dir}/{book_code}_stage_{stage}.json",
            f"{checkpoint_dir}/{book_code}_v6_1_stage_{stage}.json",
            f"{checkpoint_dir}/stage_{stage}.json"
        ]
        for path in patterns:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        print(f"WARNING: Checkpoint for stage {stage} not found")
        return {}
    
    stage_4_thread = load_checkpoint("4_thread")
    stage_2 = load_checkpoint("2_channels")
    stage_5b = load_checkpoint("5b_content")
    
    # Get book title
    with open(text_kernel_path, 'r') as f:
        text_kernel = json.load(f)
    book_title = text_kernel.get('metadata', {}).get('title', book_code)
    
    # Build kernel
    content_kernel = {
        "metadata": {
            "book_title": book_title,
            "book_code": book_code,
            "version": "1.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "source_text_kernel": os.path.basename(text_kernel_path)
        },
        "thread": {
            "core_message": stage_4_thread.get('core_message', ''),
            "agitation_register": stage_4_thread.get('agitation_register', ''),
            "solution_register": stage_4_thread.get('solution_register', ''),
            "kernel_pattern_reference": stage_4_thread.get('kernel_pattern_reference', ''),
            "selection_rationale": stage_4_thread.get('selection_rationale', ''),
            "source_angle": stage_4_thread.get('source_angle', '')
        },
        "channels": {
            "social": extract_channel(stage_2, 'social'),
            "youtube": extract_channel(stage_2, 'youtube'),
            "seo": extract_channel(stage_2, 'seo'),
            "guide": extract_channel(stage_2, 'guide')
        },
        "content_blocks": stage_5b.get('content_blocks', {})
    }
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{book_code}_content_kernel_v1_0.json"
    
    with open(output_path, 'w') as f:
        json.dump(content_kernel, f, indent=2)
    
    print(f"✓ Content kernel: {output_path}")
    return content_kernel

def extract_channel(stage_2, channel):
    """Extract channel data, handling different key formats."""
    # Try different case variations
    channel_variations = [
        channel,  # lowercase
        channel.capitalize(),  # Capitalized
        channel.upper(),  # UPPERCASE
        channel.title()  # Title Case
    ]
    
    # Special handling for known variations
    if channel == 'youtube':
        channel_variations.insert(1, 'YouTube')
    elif channel == 'seo':
        channel_variations.insert(1, 'SEO')
    
    data = {}
    for variant in channel_variations:
        if variant in stage_2:
            data = stage_2[variant]
            break
    
    return {
        "job": data.get('job', ''),
        "register": data.get('register', ''),
        "must_do": data.get('must_do', []),
        "must_not_do": data.get('must_not_do', [])
    }

if __name__ == "__main__":
    book_code = sys.argv[1] if len(sys.argv) > 1 else "TKAM"
    
    # Default paths
    checkpoint_dir = f"outputs/checkpoints/{book_code}"
    text_kernel_path = "To_Kill_a_Mockingbird_kernel_v6_1.json"
    output_dir = "outputs/kernels"
    
    # Allow override via environment or additional args
    if len(sys.argv) > 2:
        checkpoint_dir = sys.argv[2]
    if len(sys.argv) > 3:
        text_kernel_path = sys.argv[3]
    if len(sys.argv) > 4:
        output_dir = sys.argv[4]
    
    build_content_kernel(
        book_code=book_code,
        checkpoint_dir=checkpoint_dir,
        text_kernel_path=text_kernel_path,
        output_dir=output_dir
    )

