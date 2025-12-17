# utils/move_to_checkpoints.py
# Version: 1.0
# Date: December 17, 2025

import os
import shutil
import sys

def move_to_checkpoints(book_code, source_dirs, checkpoint_dir):
    """Move stage outputs to checkpoints folder."""
    
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    patterns = [
        "stage_1", "stage_3", "stage_5a",
        "stage_4", "stage_2", "stage_5b"
    ]
    
    moved = 0
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            print(f"  Skipping (not found): {source_dir}")
            continue
        
        for filename in os.listdir(source_dir):
            # Check if file matches any stage pattern and is for this book
            if any(p in filename.lower() for p in patterns):
                # Check if it's for the right book (case-insensitive)
                if book_code.upper() in filename.upper() or filename.lower().startswith(book_code.lower()):
                    src = os.path.join(source_dir, filename)
                    # Only copy JSON files (skip .raw files)
                    if filename.endswith('.json'):
                        dst = os.path.join(checkpoint_dir, filename)
                        shutil.copy(src, dst)  # Copy, not move (preserve originals for now)
                        print(f"  Copied: {filename}")
                        moved += 1
    
    print(f"\n✓ {moved} files copied to: {checkpoint_dir}")

if __name__ == "__main__":
    book_code = sys.argv[1] if len(sys.argv) > 1 else "TKAM"
    
    source_dirs = [
        "outputs/manual_exploration/phase_1",
        "outputs/manual_exploration/phase_2"
    ]
    
    checkpoint_dir = f"outputs/checkpoints/{book_code}"
    
    # Allow override
    if len(sys.argv) > 2:
        source_dirs = sys.argv[2].split(',')
    if len(sys.argv) > 3:
        checkpoint_dir = sys.argv[3]
    
    move_to_checkpoints(
        book_code=book_code,
        source_dirs=source_dirs,
        checkpoint_dir=checkpoint_dir
    )

