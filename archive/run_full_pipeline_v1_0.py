#!/usr/bin/env python3
"""
FULL PIPELINE - All Stages
Version: 1.0

Runs all stages of the content generation pipeline:
- Stage 1: Kernel Extraction
- Stage 2: Content Derivation (themes, thesis)
- Stage 3: Page Assembly
- Stage 4: HTML Generation

Usage:
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json --skip-stage2
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json --resume-from stage3
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    OUTPUTS_DIR = Path("outputs")
    SITE_DIR = Path("site")


# =============================================================================
# PIPELINE RUNNER
# =============================================================================

class PipelineRunner:
    """Runs all stages of the content generation pipeline."""
    
    def __init__(self, kernel_path: str, output_dir: Optional[str] = None, 
                 site_dir: Optional[str] = None, skip_stage2: bool = False,
                 resume_from: Optional[str] = None):
        self.kernel_path = Path(kernel_path)
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUTS_DIR
        self.site_dir = Path(site_dir) if site_dir else Config.SITE_DIR
        self.skip_stage2 = skip_stage2
        self.resume_from = resume_from
        
        if not self.kernel_path.exists():
            raise FileNotFoundError(f"Kernel file not found: {self.kernel_path}")
        
        # Extract book slug from kernel filename
        # Format: BookName_kernel_v5_0.json -> bookname
        kernel_name = self.kernel_path.stem
        if '_kernel_' in kernel_name:
            self.book_slug = kernel_name.split('_kernel_')[0].lower().replace(' ', '_')
        else:
            # Fallback: use filename without extension
            self.book_slug = kernel_name.lower().replace(' ', '_')
    
    def run_stage1(self) -> bool:
        """Run Stage 1: Kernel Extraction."""
        print("\n" + "="*70)
        print("STAGE 1: KERNEL EXTRACTION")
        print("="*70)
        
        cmd = [
            sys.executable,
            "extract_kernel_v1_0.py",
            str(self.kernel_path),
            "-o", str(self.output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    
    def run_stage2(self) -> bool:
        """Run Stage 2: Content Derivation."""
        if self.skip_stage2:
            print("\n" + "="*70)
            print("STAGE 2: CONTENT DERIVATION (SKIPPED)")
            print("="*70)
            print("⚠️  Stage 2 skipped (--skip-stage2 flag or no API key)")
            return True
        
        print("\n" + "="*70)
        print("STAGE 2: CONTENT DERIVATION")
        print("="*70)
        
        # Check if convert_kernel_to_content_v2_0.py exists and can run Stage 2
        converter_path = Path("convert_kernel_to_content_v2_0.py")
        if converter_path.exists():
            # Use the converter which handles Stage 1 + Stage 2
            # But we already ran Stage 1, so we need to check if it can resume
            cmd = [
                sys.executable,
                "convert_kernel_to_content_v2_0.py",
                str(self.kernel_path),
                "-o", str(self.output_dir),
                "--resume-from", "stage2"
            ]
            
            result = subprocess.run(cmd, capture_output=False)
            return result.returncode == 0
        else:
            print("⚠️  convert_kernel_to_content_v2_0.py not found")
            print("   Stage 2 requires API calls for theme and thesis derivation")
            print("   Skipping Stage 2...")
            return True
    
    def run_stage3(self) -> bool:
        """Run Stage 3: Page Assembly."""
        print("\n" + "="*70)
        print("STAGE 3: PAGE ASSEMBLY")
        print("="*70)
        
        cmd = [
            sys.executable,
            "assemble_pages_v1_0.py",
            self.book_slug,
            "-i", str(self.output_dir / self.book_slug),
            "-o", str(self.output_dir / self.book_slug)
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    
    def run_stage4(self) -> bool:
        """Run Stage 4: HTML Generation."""
        print("\n" + "="*70)
        print("STAGE 4: HTML GENERATION")
        print("="*70)
        
        cmd = [
            sys.executable,
            "generate_html_v1_0.py",
            self.book_slug,
            "-i", str(self.output_dir / self.book_slug),
            "-o", str(self.site_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    
    def run(self) -> bool:
        """Run full pipeline."""
        print("\n" + "="*70)
        print("FULL PIPELINE: ALL STAGES")
        print("="*70)
        print(f"Kernel: {self.kernel_path.name}")
        print(f"Book Slug: {self.book_slug}")
        print(f"Output: {self.output_dir}")
        print(f"Site: {self.site_dir}")
        
        stages_to_run = []
        
        # Determine which stages to run
        if self.resume_from:
            if self.resume_from == "stage2":
                stages_to_run = ["stage2", "stage3", "stage4"]
            elif self.resume_from == "stage3":
                stages_to_run = ["stage3", "stage4"]
            elif self.resume_from == "stage4":
                stages_to_run = ["stage4"]
            else:
                print(f"❌ Unknown resume point: {self.resume_from}")
                return False
        else:
            stages_to_run = ["stage1", "stage2", "stage3", "stage4"]
        
        # Run stages
        stage_results = {}
        
        if "stage1" in stages_to_run:
            stage_results["stage1"] = self.run_stage1()
            if not stage_results["stage1"]:
                print("\n❌ Stage 1 failed. Stopping pipeline.")
                return False
        
        if "stage2" in stages_to_run:
            stage_results["stage2"] = self.run_stage2()
            if not stage_results["stage2"]:
                print("\n⚠️  Stage 2 failed or skipped. Continuing to Stage 3...")
        
        if "stage3" in stages_to_run:
            stage_results["stage3"] = self.run_stage3()
            if not stage_results["stage3"]:
                print("\n❌ Stage 3 failed. Stopping pipeline.")
                return False
        
        if "stage4" in stages_to_run:
            stage_results["stage4"] = self.run_stage4()
            if not stage_results["stage4"]:
                print("\n❌ Stage 4 failed. Stopping pipeline.")
                return False
        
        # Summary
        print("\n" + "="*70)
        print("PIPELINE SUMMARY")
        print("="*70)
        
        for stage, success in stage_results.items():
            status = "✓" if success else "❌"
            print(f"{status} {stage.upper()}: {'SUCCESS' if success else 'FAILED'}")
        
        all_success = all(stage_results.values())
        
        if all_success:
            print(f"\n✅ Pipeline complete!")
            print(f"   HTML files: {self.site_dir / self.book_slug}")
        else:
            print(f"\n⚠️  Pipeline completed with errors")
        
        return all_success


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Run full content generation pipeline (all stages)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run all stages
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json
    
    # Skip Stage 2 (no API calls)
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json --skip-stage2
    
    # Resume from Stage 3
    python run_full_pipeline_v1_0.py Orbital_kernel_v5_0.json --resume-from stage3
    
Stages:
    1. Kernel Extraction (extract_kernel_v1_0.py)
    2. Content Derivation (convert_kernel_to_content_v2_0.py - themes, thesis)
    3. Page Assembly (assemble_pages_v1_0.py)
    4. HTML Generation (generate_html_v1_0.py)
        """
    )
    
    parser.add_argument('kernel_path', help='Path to kernel JSON file')
    parser.add_argument('-o', '--output-dir', help='Output directory for JSON files (default: outputs)')
    parser.add_argument('-s', '--site-dir', help='Output directory for HTML files (default: site)')
    parser.add_argument('--skip-stage2', action='store_true', 
                       help='Skip Stage 2 (content derivation via API)')
    parser.add_argument('--resume-from', choices=['stage2', 'stage3', 'stage4'],
                       help='Resume pipeline from specified stage')
    
    args = parser.parse_args()
    
    try:
        runner = PipelineRunner(
            args.kernel_path,
            output_dir=args.output_dir,
            site_dir=args.site_dir,
            skip_stage2=args.skip_stage2,
            resume_from=args.resume_from
        )
        success = runner.run()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
