#!/usr/bin/env python3
"""
Run the full pipeline (all stages) on all kernel files in the current directory.

Stages:
    1. Kernel Extraction (extract_kernel_v1_0.py)
    2. Content Derivation (convert_kernel_to_content_v2_0.py - themes, thesis)
    3. Page Assembly (assemble_pages_v1_0.py)
    4. HTML Generation (generate_html_v1_0.py)
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Find all kernel files in current directory
    kernel_files = sorted(Path('.').glob('*kernel*.json'))
    
    # Filter out files in subdirectories
    kernel_files = [f for f in kernel_files if f.parent == Path('.')]
    
    if not kernel_files:
        print("No kernel files found in current directory")
        return 1
    
    print(f"Found {len(kernel_files)} kernel files")
    print("="*70)
    print("Running full pipeline (all 4 stages) for each kernel")
    print("="*70)
    
    results = []
    
    for i, kernel_file in enumerate(kernel_files, 1):
        print(f"\n[{i}/{len(kernel_files)}] Processing: {kernel_file.name}")
        print("-"*70)
        
        try:
            # Use the full pipeline runner
            result = subprocess.run(
                [sys.executable, 'run_full_pipeline_v1_0.py', 
                 str(kernel_file), '-o', 'outputs/', '-s', 'site/'],
                capture_output=False,  # Show output in real-time
                timeout=1800  # 30 minute timeout per kernel (includes all stages)
            )
            
            if result.returncode == 0:
                print(f"\n✓ Success: {kernel_file.name}")
                results.append((kernel_file.name, "SUCCESS", None))
            else:
                print(f"\n❌ Error: {kernel_file.name}")
                results.append((kernel_file.name, "ERROR", "See output above"))
                
        except subprocess.TimeoutExpired:
            print(f"\n⏱ Timeout: {kernel_file.name}")
            results.append((kernel_file.name, "TIMEOUT", None))
        except Exception as e:
            print(f"\n❌ Exception: {kernel_file.name} - {e}")
            results.append((kernel_file.name, "EXCEPTION", str(e)))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    success_count = sum(1 for _, status, _ in results if status == "SUCCESS")
    error_count = len(results) - success_count
    
    for kernel_name, status, error in results:
        status_symbol = "✓" if status == "SUCCESS" else "❌"
        print(f"{status_symbol} {kernel_name}: {status}")
        if error:
            print(f"   {error}")
    
    print(f"\nTotal: {len(results)}")
    print(f"Success: {success_count}")
    print(f"Failed: {error_count}")
    
    if success_count > 0:
        print(f"\n📁 Outputs:")
        print(f"   JSON files: outputs/")
        print(f"   HTML files: site/")
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())

