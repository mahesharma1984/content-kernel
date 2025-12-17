# utils/archive_old_outputs.py
# Version: 1.0
# Date: December 17, 2025
# Purpose: Move old stage outputs to archive

import os
import shutil
from datetime import datetime

def archive_old_outputs(source_dir, archive_dir):
    """Move old stage JSONs to archive."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(archive_dir, f"stage_outputs_{timestamp}")
    
    os.makedirs(archive_path, exist_ok=True)
    
    # Patterns to archive
    patterns = [
        "_stage_1_",
        "_stage_3_",
        "_stage_5a_",
        "_stage_4_",
        "_stage_2_",
        "_stage_5b_",
    ]
    
    moved = 0
    for filename in os.listdir(source_dir):
        if any(p in filename.lower() for p in patterns):
            src = os.path.join(source_dir, filename)
            dst = os.path.join(archive_path, filename)
            shutil.move(src, dst)
            print(f"  Archived: {filename}")
            moved += 1
    
    print(f"\n✓ Archived {moved} files to: {archive_path}")

if __name__ == "__main__":
    # Archive phase 1 outputs
    archive_old_outputs(
        "outputs/manual_exploration/phase_1",
        "archive/stage_outputs"
    )
    
    # Archive phase 2 outputs
    archive_old_outputs(
        "outputs/manual_exploration/phase_2",
        "archive/stage_outputs"
    )

