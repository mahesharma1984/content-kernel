#!/usr/bin/env python3
"""
PAGE ASSEMBLY - Stage 3
Version: 1.0

Assembles Stage 1 extraction + Stage 2 derivations into final page JSONs.
Pure assembly — no API calls, no new content generation.

Usage:
    python assemble_pages_v1_0.py orbital -o outputs/
"""

import json
import argparse
from pathlib import Path
from typing import Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    OUTPUTS_DIR = Path("outputs")


# =============================================================================
# STATIC CONTENT
# =============================================================================

class StaticContent:
    """All hardcoded text that doesn't come from Stage 1 or Stage 2."""
    
    # Badges
    BADGE_KNOWLEDGE_HUB = "Knowledge: What the Book Does"
    BADGE_PEDAGOGY_HUB = "Pedagogy: How to Read for Patterns"
    BADGE_CTA_HUB = "Action: Explore Through Themes"
    
    BADGE_PEDAGOGY_THEME = "Pedagogy: How to Analyze This Theme"
    BADGE_CTA_THEME = "Action: Keep Exploring"
    
    BADGE_KNOWLEDGE_ESSAY = "Knowledge: Building Your Thesis"
    BADGE_PEDAGOGY_ESSAY = "Pedagogy: From Pattern to Thesis"
    BADGE_CTA_ESSAY = "Action: Get Support"
    
    # Headings
    HEADING_PEDAGOGY_HUB = "What Pattern-Recognition Means"
    
    # Prompts (hub pedagogy zone)
    PROMPTS = [
        "What's the cumulative effect of these devices working together?",
        "Why would the author choose this particular combination?",
        "What reader experience does this pattern create?"
    ]
    
    # Three steps titles (theme pages)
    THREE_STEPS = [
        {"step": 1, "title": "Identify the Pattern's Effect"},
        {"step": 2, "title": "Connect Devices to This Effect"},
        {"step": 3, "title": "Articulate Theme Meaning"}
    ]
    
    # Four steps (essay guide) - content populated dynamically
    FOUR_STEPS_TEMPLATE = [
        {"step": 1, "title": "Choose your theme", "content": "Select from the themes above"},
        {"step": 2, "title": "Identify devices", "content": "Which devices create this theme?"},
        {"step": 3, "title": "Connect to pattern", "content": None},  # Populated with pattern name
        {"step": 4, "title": "Synthesize", "content": "Combine into clear thesis statement"}
    ]
    
    # CTA text
    CTA_PRIMARY_ESSAY = "Get help developing your thesis"
    CTA_SECONDARY_ESSAY = "Upload your draft"


# =============================================================================
# ASSEMBLER CLASS
# =============================================================================

class PageAssembler:
    """Assembles Stage 1 + Stage 2 into final page JSONs."""
    
    def __init__(self, book_slug: str, input_dir: Optional[str] = None, output_dir: Optional[str] = None):
        self.book_slug = book_slug
        self.input_dir = Path(input_dir) if input_dir else Config.OUTPUTS_DIR / book_slug
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUTS_DIR / book_slug
        self.stage1 = None
        self.stage2 = None
    
    def load_inputs(self) -> bool:
        """Load Stage 1 and Stage 2 JSONs."""
        print(f"\n📖 Loading inputs for: {self.book_slug}")
        
        # Load Stage 1 - check multiple possible locations
        stage1_paths = [
            self.input_dir / "stage1_extraction.json",
            self.input_dir / "stages" / "stage1_extraction.json"
        ]
        
        stage1_path = None
        for path in stage1_paths:
            if path.exists():
                stage1_path = path
                break
        
        if not stage1_path:
            print(f"❌ Error: stage1_extraction.json not found")
            print(f"   Checked: {stage1_paths[0]}")
            print(f"   Checked: {stage1_paths[1]}")
            print(f"   Run Stage 1 first: python extract_kernel_v1_0.py <kernel>")
            return False
        
        with open(stage1_path, 'r', encoding='utf-8') as f:
            self.stage1 = json.load(f)
        print(f"   ✓ Loaded stage1_extraction.json from {stage1_path}")
        
        # Load Stage 2 - check multiple possible locations
        stage2_paths = [
            self.input_dir / "stage2_derivations.json",
            self.input_dir / "stages" / "stage2_derivations.json"
        ]
        
        stage2_path = None
        for path in stage2_paths:
            if path.exists():
                stage2_path = path
                break
        
        if not stage2_path:
            print(f"❌ Error: stage2_derivations.json not found")
            print(f"   Checked: {stage2_paths[0]}")
            print(f"   Checked: {stage2_paths[1]}")
            print(f"   Run Stage 2 first: python derive_content_v1_0.py {self.book_slug}")
            return False
        
        with open(stage2_path, 'r', encoding='utf-8') as f:
            self.stage2 = json.load(f)
        print(f"   ✓ Loaded stage2_derivations.json from {stage2_path}")
        
        return True
    
    def validate_inputs(self) -> bool:
        """Validate required fields exist."""
        print(f"\n🔍 Validating inputs...")
        
        errors = []
        
        # Stage 1 required fields
        if not self.stage1.get("pattern", {}).get("name"):
            errors.append("stage1.pattern.name missing")
        if not self.stage1.get("pattern", {}).get("reader_effect"):
            errors.append("stage1.pattern.reader_effect missing")
        if not self.stage1.get("metadata", {}).get("book_slug"):
            errors.append("stage1.metadata.book_slug missing")
        
        # Stage 2 required fields
        if not self.stage2.get("themes"):
            errors.append("stage2.themes missing or empty")
        if not self.stage2.get("theses"):
            errors.append("stage2.theses missing or empty")
        
        if errors:
            print(f"❌ Validation failed:")
            for e in errors:
                print(f"   - {e}")
            return False
        
        print(f"   ✓ All required fields present")
        print(f"   ✓ {len(self.stage2['themes'])} themes found")
        print(f"   ✓ {len(self.stage2['theses'])} theses found")
        return True
    
    def _build_theme_links(self) -> list:
        """Build theme links for hub CTA."""
        links = []
        for theme in self.stage2["themes"]:
            links.append({
                "text": theme["name"],
                "url": f"themes/{theme['slug']}/"
            })
        return links
    
    def assemble_hub(self) -> dict:
        """Assemble hub.json."""
        book_slug = self.stage1["metadata"]["book_slug"]
        pattern = self.stage1["pattern"]
        macro = self.stage1["macro_variables"]
        
        # Build worked example formula from top 3 device priorities
        device_priorities = pattern.get("device_priorities", [])
        formula = " + ".join(device_priorities[:3]) if device_priorities else "Device 1 + Device 2 + Device 3"
        
        # Build structure string
        total_chapters = macro.get("structure", {}).get("total_chapters")
        structure_str = f"{total_chapters} chapters" if total_chapters else "Multiple chapters"
        
        hub = {
            "page_type": "hub",
            "book_slug": book_slug,
            "url": f"/{book_slug}/",
            "zones": {
                "knowledge": {
                    "badge": StaticContent.BADGE_KNOWLEDGE_HUB,
                    "heading": pattern["name"],
                    "description": pattern["core_dynamic"],
                    "reader_effect": pattern["reader_effect"],
                    "quick_reference": {
                        "structure": structure_str,
                        "voice": macro.get("voice", {}).get("pov_description", ""),
                        "tone": macro.get("rhetoric", {}).get("tone", "")
                    }
                },
                "pedagogy": {
                    "badge": StaticContent.BADGE_PEDAGOGY_HUB,
                    "heading": StaticContent.HEADING_PEDAGOGY_HUB,
                    "worked_example": {
                        "formula": formula,
                        "arrow": "→",
                        "effect": pattern["reader_effect"]
                    },
                    "prompts": StaticContent.PROMPTS
                },
                "cta": {
                    "badge": StaticContent.BADGE_CTA_HUB,
                    "links": self._build_theme_links() + [
                        {"text": "Build Your Thesis", "url": "essay-guide/", "emphasis": True}
                    ]
                }
            }
        }
        
        return hub
    
    def assemble_theme(self, theme: dict) -> dict:
        """Assemble a single theme page JSON."""
        book_slug = self.stage1["metadata"]["book_slug"]
        pattern = self.stage1["pattern"]
        
        # Get first device name for step 2 content
        first_device = theme["device_examples"][0]["device_name"] if theme.get("device_examples") else "the key device"
        
        theme_page = {
            "page_type": "theme",
            "book_slug": book_slug,
            "theme_slug": theme["slug"],
            "url": f"/{book_slug}/themes/{theme['slug']}/",
            "zones": {
                "knowledge": {
                    "badge": f"Knowledge: {theme['name']}",
                    "heading": theme["name"],
                    "description": theme["description"],
                    "pattern_connection": theme["pattern_connection"],
                    "device_examples": theme["device_examples"]
                },
                "pedagogy": {
                    "badge": StaticContent.BADGE_PEDAGOGY_THEME,
                    "three_steps": [
                        {
                            "step": 1,
                            "title": StaticContent.THREE_STEPS[0]["title"],
                            "content": pattern["reader_effect"]
                        },
                        {
                            "step": 2,
                            "title": StaticContent.THREE_STEPS[1]["title"],
                            "content": f"See how {first_device} and other devices create this theme"
                        },
                        {
                            "step": 3,
                            "title": StaticContent.THREE_STEPS[2]["title"],
                            "content": theme["description"]
                        }
                    ]
                },
                "cta": {
                    "badge": StaticContent.BADGE_CTA_THEME,
                    "links": [
                        {"text": "Back to Hub", "url": f"/{book_slug}/"},
                        {"text": "Build Your Thesis", "url": f"/{book_slug}/essay-guide/"}
                    ]
                }
            }
        }
        
        return theme_page
    
    def assemble_essay_guide(self) -> dict:
        """Assemble essay_guide.json."""
        book_slug = self.stage1["metadata"]["book_slug"]
        title = self.stage1["metadata"]["title"]
        pattern = self.stage1["pattern"]
        
        # Build four steps with pattern name
        four_steps = []
        for step in StaticContent.FOUR_STEPS_TEMPLATE:
            step_copy = step.copy()
            if step["step"] == 3:
                step_copy["content"] = f"How does {pattern['name']} work?"
            four_steps.append(step_copy)
        
        essay_guide = {
            "page_type": "essay_guide",
            "book_slug": book_slug,
            "url": f"/{book_slug}/essay-guide/",
            "zones": {
                "knowledge": {
                    "badge": StaticContent.BADGE_KNOWLEDGE_ESSAY,
                    "heading": f"How to Write About {title}",
                    "thesis_components": {
                        "pattern": pattern["name"],
                        "themes": [t["name"] for t in self.stage2["themes"]],
                        "devices": pattern.get("device_priorities", [])[:5]
                    },
                    "example_theses": self.stage2["theses"]
                },
                "pedagogy": {
                    "badge": StaticContent.BADGE_PEDAGOGY_ESSAY,
                    "four_steps": four_steps
                },
                "cta": {
                    "badge": StaticContent.BADGE_CTA_ESSAY,
                    "primary": StaticContent.CTA_PRIMARY_ESSAY,
                    "secondary": StaticContent.CTA_SECONDARY_ESSAY
                }
            }
        }
        
        return essay_guide
    
    def save_json(self, filename: str, data: dict, subdir: Optional[str] = None):
        """Save JSON to output directory."""
        if subdir:
            output_path = self.output_dir / subdir
            output_path.mkdir(parents=True, exist_ok=True)
            filepath = output_path / filename
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def assemble(self) -> bool:
        """Run full assembly."""
        print("\n" + "="*60)
        print("STAGE 3: PAGE ASSEMBLY")
        print("="*60)
        
        # Load inputs
        if not self.load_inputs():
            return False
        
        # Validate
        if not self.validate_inputs():
            return False
        
        # Assemble pages
        print(f"\n📦 Assembling pages...")
        
        # Hub
        hub = self.assemble_hub()
        hub_path = self.save_json("hub.json", hub)
        print(f"   ✓ hub.json")
        
        # Themes
        themes_dir = self.output_dir / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        for theme in self.stage2["themes"]:
            theme_page = self.assemble_theme(theme)
            theme_path = self.save_json(f"{theme['slug']}.json", theme_page, "themes")
            print(f"   ✓ themes/{theme['slug']}.json")
        
        # Essay guide
        essay_guide = self.assemble_essay_guide()
        essay_path = self.save_json("essay_guide.json", essay_guide)
        print(f"   ✓ essay_guide.json")
        
        # Summary
        print(f"\n💾 Output directory: {self.output_dir}")
        print(f"   - 1 hub page")
        print(f"   - {len(self.stage2['themes'])} theme pages")
        print(f"   - 1 essay guide")
        
        return True
    
    def run(self) -> bool:
        """Run assembly."""
        if not self.assemble():
            return False
        
        print(f"\n✅ Stage 3 complete")
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Assemble Stage 1 + Stage 2 into final page JSONs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python assemble_pages_v1_0.py orbital
    python assemble_pages_v1_0.py orbital -i outputs/ -o outputs/
        """
    )
    parser.add_argument('book_slug', help='Book slug (e.g., orbital)')
    parser.add_argument('-i', '--input-dir', help='Input directory containing stage1 and stage2 JSONs')
    parser.add_argument('-o', '--output-dir', help='Output directory for assembled pages')
    
    args = parser.parse_args()
    
    assembler = PageAssembler(
        args.book_slug,
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )
    success = assembler.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

