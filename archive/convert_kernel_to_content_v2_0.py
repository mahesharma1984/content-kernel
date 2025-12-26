#!/usr/bin/env python3
"""
Kernel to Content Converter - Version 2.0
Staged Pipeline: Extraction → API Derivation → Page Assembly

Three-stage pipeline:
Stage 1: Extract from kernel (no API)
Stage 2: Derive via API (themes, thesis)
Stage 3: Assemble page JSONs (no API)

Usage:
    python convert_kernel_to_content_v2_0.py <kernel_path> [output_dir] [--resume-from stage2|stage3]
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)

# Import Stage 1 extractor
from extract_kernel_v1_0 import KernelExtractor, slugify


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000
    OUTPUTS_DIR = Path("outputs")
    PROMPTS_DIR = Path("prompts")


# =============================================================================
# CONTENT CONVERTER
# =============================================================================

class ContentConverter:
    """
    Three-stage pipeline:
    Stage 1: Extract from kernel (no API)
    Stage 2: Derive via API (themes, thesis)
    Stage 3: Assemble page JSONs (no API)
    """
    
    def __init__(self, kernel_path: str, output_dir: Optional[str] = None):
        self.kernel_path = Path(kernel_path)
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUTS_DIR
        self.book_slug = None
        
        # Create directories
        self.stage_dir = None  # Will be set after book_slug is determined
        self.client = None
        
        # Initialize API client if key is available
        if Config.API_KEY:
            self.client = anthropic.Anthropic(api_key=Config.API_KEY)
        else:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. Stage 2 will be skipped.")
    
    def _get_stage_dir(self) -> Path:
        """Get stage directory path (creates if needed)."""
        if not self.book_slug:
            raise ValueError("book_slug must be set before accessing stage_dir")
        if not self.stage_dir:
            self.stage_dir = self.output_dir / self.book_slug / "stages"
            self.stage_dir.mkdir(parents=True, exist_ok=True)
        return self.stage_dir
    
    def _save_checkpoint(self, stage_name: str, data: dict) -> Path:
        """Save checkpoint file."""
        checkpoint_path = self._get_stage_dir() / f"{stage_name}.json"
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Checkpoint saved: {checkpoint_path}")
        return checkpoint_path
    
    def _load_checkpoint(self, stage_name: str) -> Optional[dict]:
        """Load checkpoint file if it exists."""
        if not self.book_slug:
            # Can't load checkpoint without book_slug
            return None
        
        # First check stages/ subdirectory
        checkpoint_path = self._get_stage_dir() / f"{stage_name}.json"
        if checkpoint_path.exists():
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded checkpoint: {checkpoint_path}")
            return data
        
        # Also check if extractor saved it directly (for stage1_extraction)
        if stage_name == "stage1_extraction":
            extractor_path = self.output_dir / self.book_slug / "stage1_extraction.json"
            if extractor_path.exists():
                with open(extractor_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ Loaded checkpoint: {extractor_path}")
                return data
        
        return None
    
    def stage1_kernel_extraction(self) -> dict:
        """
        Stage 1: Extract all usable content from kernel.
        No API calls, pure extraction.
        Uses extract_kernel_v1_0.py
        """
        print("\n" + "="*60)
        print("STAGE 1: Kernel Extraction")
        print("="*60)
        
        # Determine book_slug from kernel filename first
        # This ensures we look in the right directory
        filename = self.kernel_path.stem
        book_name = filename.split('_kernel')[0]
        temp_book_slug = slugify(book_name)
        
        # Check if we already have extraction for this book
        self.book_slug = temp_book_slug
        cached = self._load_checkpoint("stage1_extraction")
        if cached:
            print("   ✓ Using cached extraction")
            return cached
        
        # Reset book_slug since we'll set it from extraction
        self.book_slug = None
        
        # Run extraction using Stage 1 extractor
        extractor = KernelExtractor(str(self.kernel_path), str(self.output_dir))
        if not extractor.extract():
            raise ValueError("Stage 1 extraction failed")
        
        # Set book_slug from extraction
        self.book_slug = extractor.extraction['metadata']['book_slug']
        
        # The extractor saves to book_slug/stage1_extraction.json
        # We also save to stages/ subdirectory for consistency with other stages
        self._save_checkpoint("stage1_extraction", extractor.extraction)
        
        return extractor.extraction
    
    def stage2_content_derivation(self) -> dict:
        """
        Stage 2: API calls for themes and thesis.
        Requires stage1_extraction.json to exist.
        """
        print("\n" + "="*60)
        print("STAGE 2: Content Derivation")
        print("="*60)
        
        # Load Stage 1 output
        extraction = self._load_checkpoint("stage1_extraction")
        if not extraction:
            raise ValueError("Stage 1 must complete before Stage 2. Run stage1_kernel_extraction() first.")
        
        # Set book_slug if not already set
        if not self.book_slug:
            self.book_slug = extraction['metadata']['book_slug']
        
        # Check for cached derivations
        cached = self._load_checkpoint("stage2_derivations")
        if cached:
            print("   ✓ Using cached derivations")
            return cached
        
        if not self.client:
            print("⚠️  Skipping Stage 2: No API key available")
            derivations = {
                "themes": [],
                "theses": []
            }
            self._save_checkpoint("stage2_derivations", derivations)
            return derivations
        
        # Derive themes
        print("   Deriving themes...")
        themes = self._derive_themes(extraction)
        
        # Generate thesis examples
        print("   Generating thesis examples...")
        theses = self._generate_theses(extraction, themes)
        
        derivations = {
            "themes": themes,
            "theses": theses
        }
        
        # Save checkpoint
        self._save_checkpoint("stage2_derivations", derivations)
        return derivations
    
    def _derive_themes(self, extraction: dict) -> List[dict]:
        """Call API with theme derivation prompt."""
        # Load prompt template
        prompt_path = Config.PROMPTS_DIR / "derive_themes_v1_0.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Prepare sample devices (first 10)
        sample_devices = extraction['micro_devices'][:10]
        sample_devices_json = json.dumps(sample_devices, indent=2)
        
        # Fill template using manual replacement to avoid issues with JSON braces
        prompt = prompt_template.replace('{pattern_name}', extraction['pattern']['name'])
        prompt = prompt.replace('{core_dynamic}', extraction['pattern']['core_dynamic'])
        prompt = prompt.replace('{reader_effect}', extraction['pattern']['reader_effect'])
        prompt = prompt.replace('{tone}', extraction['macro_variables']['rhetoric']['tone'])
        prompt = prompt.replace('{device_priorities}', json.dumps(extraction['pattern']['device_priorities']))
        prompt = prompt.replace('{device_mediation_summary}', extraction['device_mediation']['summary'])
        prompt = prompt.replace('{sample_devices}', sample_devices_json)
        
        # Call API
        try:
            response = self.client.messages.create(
                model=Config.MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            themes_data = json.loads(content)
            return themes_data.get("themes", [])
            
        except Exception as e:
            print(f"❌ Error deriving themes: {e}")
            return []
    
    def _generate_theses(self, extraction: dict, themes: List[dict]) -> List[dict]:
        """Call API with thesis generation prompt."""
        # Load prompt template
        prompt_path = Config.PROMPTS_DIR / "generate_thesis_v1_0.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Fill template using manual replacement
        prompt = prompt_template.replace('{pattern_name}', extraction['pattern']['name'])
        prompt = prompt.replace('{core_dynamic}', extraction['pattern']['core_dynamic'])
        prompt = prompt.replace('{reader_effect}', extraction['pattern']['reader_effect'])
        prompt = prompt.replace('{themes}', json.dumps(themes, indent=2))
        prompt = prompt.replace('{device_priorities}', json.dumps(extraction['pattern']['device_priorities'][:5]))
        
        # Call API
        try:
            response = self.client.messages.create(
                model=Config.MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text.strip()
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            theses_data = json.loads(content)
            return theses_data.get("theses", [])
            
        except Exception as e:
            print(f"❌ Error generating theses: {e}")
            return []
    
    def stage3_page_assembly(self):
        """
        Stage 3: Combine Stage 1 + Stage 2 into page content JSONs.
        No API calls, pure assembly.
        """
        print("\n" + "="*60)
        print("STAGE 3: Page Assembly")
        print("="*60)
        
        # Load checkpoints
        extraction = self._load_checkpoint("stage1_extraction")
        derivations = self._load_checkpoint("stage2_derivations")
        
        if not extraction:
            raise ValueError("Stage 1 must complete before Stage 3.")
        if not derivations:
            raise ValueError("Stage 2 must complete before Stage 3.")
        
        # Set book_slug from extraction
        self.book_slug = extraction['metadata']['book_slug']
        
        # Create output directory
        book_dir = self.output_dir / self.book_slug
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Hub page
        hub = self._assemble_hub(extraction, derivations)
        hub_path = book_dir / "hub.json"
        with open(hub_path, 'w', encoding='utf-8') as f:
            json.dump(hub, f, indent=2)
        print(f"✓ Created: {hub_path}")
        
        # Theme pages
        themes_dir = book_dir / "themes"
        themes_dir.mkdir(exist_ok=True)
        
        for theme in derivations.get("themes", []):
            theme_page = self._assemble_theme(extraction, theme)
            theme_path = themes_dir / f"{theme['slug']}.json"
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme_page, f, indent=2)
            print(f"✓ Created: {theme_path}")
        
        # Essay guide
        essay_guide = self._assemble_essay_guide(extraction, derivations)
        essay_path = book_dir / "essay_guide.json"
        with open(essay_path, 'w', encoding='utf-8') as f:
            json.dump(essay_guide, f, indent=2)
        print(f"✓ Created: {essay_path}")
        
        print(f"\n✓ Stage 3 complete. Content JSONs in: {book_dir}")
    
    def _assemble_hub(self, extraction: dict, derivations: dict) -> dict:
        """Assemble hub page content."""
        return {
            "page_type": "hub",
            "book_slug": extraction["metadata"]["book_slug"],
            "url": f"/{extraction['metadata']['book_slug']}/",
            "zones": {
                "knowledge": {
                    "badge": "Knowledge: What the Book Does",
                    "heading": extraction["pattern"]["name"],
                    "description": extraction["pattern"]["core_dynamic"],
                    "reader_effect": extraction["pattern"]["reader_effect"],
                    "quick_reference": {
                        "structure": f"{extraction['macro_variables']['structure']['total_chapters']} chapters",
                        "voice": extraction["macro_variables"]["voice"]["pov_description"],
                        "tone": extraction["macro_variables"]["rhetoric"]["tone"]
                    }
                },
                "pedagogy": {
                    "badge": "Pedagogy: How to Read for Patterns",
                    "heading": "What Pattern-Recognition Means",
                    "worked_example": self._create_device_formula(extraction),
                    "prompts": [
                        "What's the cumulative effect of these devices working together?",
                        "Why would the author choose this particular combination?",
                        "What reader experience does this pattern create?"
                    ]
                },
                "cta": {
                    "badge": "Action: Explore Through Themes",
                    "links": self._create_theme_links(derivations)
                }
            }
        }
    
    def _create_device_formula(self, extraction: dict) -> dict:
        """Create device formula from priorities."""
        priorities = extraction["pattern"]["device_priorities"][:3]
        formula = " + ".join(priorities)
        effect = extraction["pattern"]["reader_effect"].split('.')[0]  # First sentence
        return {
            "formula": formula,
            "arrow": "→",
            "effect": effect
        }
    
    def _create_theme_links(self, derivations: dict) -> List[dict]:
        """Create links to theme pages."""
        links = []
        for theme in derivations.get("themes", []):
            links.append({
                "text": theme["name"],
                "url": f"themes/{theme['slug']}/"
            })
        links.append({
            "text": "Build Your Thesis",
            "url": "essay-guide/",
            "emphasis": True
        })
        return links
    
    def _assemble_theme(self, extraction: dict, theme: dict) -> dict:
        """Assemble theme page content."""
        return {
            "page_type": "theme",
            "book_slug": extraction["metadata"]["book_slug"],
            "theme_slug": theme["slug"],
            "url": f"/{extraction['metadata']['book_slug']}/themes/{theme['slug']}/",
            "zones": {
                "knowledge": {
                    "badge": f"Knowledge: {theme['name']}",
                    "heading": theme["name"],
                    "description": theme["description"],
                    "pattern_connection": theme["pattern_connection"],
                    "device_examples": theme["device_examples"]
                },
                "pedagogy": {
                    "badge": "Pedagogy: How to Analyze This Theme",
                    "three_steps": [
                        {
                            "step": 1,
                            "title": "Identify the Pattern's Effect",
                            "content": extraction["pattern"]["reader_effect"]
                        },
                        {
                            "step": 2,
                            "title": "Connect Devices to This Effect",
                            "content": f"See how {theme['device_examples'][0]['device_name']} and other devices create this theme"
                        },
                        {
                            "step": 3,
                            "title": "Articulate Theme Meaning",
                            "content": theme["description"]
                        }
                    ]
                },
                "cta": {
                    "badge": "Action: Keep Exploring",
                    "links": [
                        {"text": "Back to Hub", "url": f"/{extraction['metadata']['book_slug']}/"},
                        {"text": "Build Your Thesis", "url": f"/{extraction['metadata']['book_slug']}/essay-guide/"}
                    ]
                }
            }
        }
    
    def _assemble_essay_guide(self, extraction: dict, derivations: dict) -> dict:
        """Assemble essay guide content."""
        return {
            "page_type": "essay_guide",
            "book_slug": extraction["metadata"]["book_slug"],
            "url": f"/{extraction['metadata']['book_slug']}/essay-guide/",
            "zones": {
                "knowledge": {
                    "badge": "Knowledge: Building Your Thesis",
                    "heading": f"How to Write About {extraction['metadata']['title']}",
                    "thesis_components": {
                        "pattern": extraction["pattern"]["name"],
                        "themes": [t["name"] for t in derivations.get("themes", [])],
                        "devices": extraction["pattern"]["device_priorities"][:5]
                    },
                    "example_theses": derivations.get("theses", [])
                },
                "pedagogy": {
                    "badge": "Pedagogy: From Pattern to Thesis",
                    "four_steps": [
                        {"step": 1, "title": "Choose your theme", "content": "Select from the themes above"},
                        {"step": 2, "title": "Identify devices", "content": "Which devices create this theme?"},
                        {"step": 3, "title": "Connect to pattern", "content": f"How does {extraction['pattern']['name']} work?"},
                        {"step": 4, "title": "Synthesize", "content": "Combine into clear thesis statement"}
                    ]
                },
                "cta": {
                    "badge": "Action: Get Support",
                    "primary": "Get help developing your thesis",
                    "secondary": "Upload your draft"
                }
            }
        }
    
    def run(self, resume_from: Optional[str] = None):
        """
        Run complete pipeline with optional resume.
        
        Args:
            resume_from: 'stage2' or 'stage3' to skip completed stages
        """
        if resume_from is None:
            self.stage1_kernel_extraction()
            self.stage2_content_derivation()
            self.stage3_page_assembly()
        elif resume_from == 'stage2':
            self.stage2_content_derivation()
            self.stage3_page_assembly()
        elif resume_from == 'stage3':
            self.stage3_page_assembly()
        else:
            raise ValueError("resume_from must be 'stage2', 'stage3', or None")
        
        print("\n✅ Pipeline complete!")


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert kernel JSON to content JSONs (v2.0 staged pipeline)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python convert_kernel_to_content_v2_0.py Orbital_kernel_v5_0.json
    python convert_kernel_to_content_v2_0.py Orbital_kernel_v5_0.json -o Content/
    python convert_kernel_to_content_v2_0.py Orbital_kernel_v5_0.json --resume-from stage2
        """
    )
    parser.add_argument('kernel', help='Path to kernel JSON file')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: outputs/)')
    parser.add_argument('--resume-from', choices=['stage2', 'stage3'], 
                       help='Resume from specific stage')
    
    args = parser.parse_args()
    
    converter = ContentConverter(args.kernel, args.output_dir)
    converter.run(resume_from=args.resume_from)
    
    return 0


if __name__ == "__main__":
    exit(main())

