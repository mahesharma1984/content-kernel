#!/usr/bin/env python3
"""
PEDAGOGICAL TRANSLATION - Stage 3A
Version: 1.0

Translates dense academic content into unpacked, pedagogically 
structured text for Year 10-12 students.

Usage:
    python translate_content_v1_0.py orbital -i outputs/orbital/
"""

import json
import argparse
import os
from pathlib import Path
from typing import Optional, Any

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    OUTPUTS_DIR = Path("outputs")
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 2000


# =============================================================================
# TRANSLATION PROMPT
# =============================================================================

TRANSLATION_PROMPT = """You are translating literary analysis content for Year 10-12 students (ages 15-18).
These students are capable but need dense academic writing unpacked.

## Rules
1. RETAIN all academic vocabulary (juxtaposition, omniscient, paradox, contemplative, meditative, etc.)
2. UNPACK dense sentences into stages — break compound ideas into separate lines
3. MAKE connections explicit (cause → effect, technique → result)
4. ADD scaffolding questions where helpful ("Ask yourself...", "Why this word?")
5. USE bullet points (•) to break down lists of concepts
6. KEEP the same meaning — do not simplify the ideas, simplify the structure
7. USE line breaks between distinct ideas
8. KEEP paragraphs short (2-3 sentences max)

## Format
- Line breaks between ideas
- Bullet points: • (not - or *)
- Em-dashes for asides: —
- Short paragraphs

## Example

BEFORE:
"Contrasts the intimate measure of human reach with infinite space, emphasizing our physical vulnerability against cosmic vastness."

AFTER:
"Harvey places two things side by side:
• Something intimate: a hand-span (human scale)
• Something infinite: the universe unfolding

The contrast emphasises physical vulnerability—the astronauts are separated from death by a 'skin of metal.' The word 'skin' makes this barrier feel fragile, organic, easily punctured."

## Content to Translate
{content}

## Output
Translate the content following the rules above. Return ONLY the translated text, no preamble."""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_nested(obj: dict, path: str) -> Any:
    """Get nested value using dot notation."""
    keys = path.split('.')
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj


def set_nested(obj: dict, path: str, value: Any):
    """Set nested value using dot notation."""
    keys = path.split('.')
    for key in keys[:-1]:
        if not isinstance(obj, dict):
            return
        obj = obj.setdefault(key, {})
    if isinstance(obj, dict):
        obj[keys[-1]] = value


# =============================================================================
# TRANSLATOR CLASS
# =============================================================================

class ContentTranslator:
    """Translates page JSON content for Year 10-12 audience."""
    
    def __init__(self, book_slug: str, input_dir: Optional[str] = None):
        self.book_slug = book_slug
        self.input_dir = Path(input_dir) if input_dir else Config.OUTPUTS_DIR / book_slug
        
        # Initialize API client
        if Config.API_KEY:
            self.client = anthropic.Anthropic(api_key=Config.API_KEY)
        else:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. Translation will be skipped.")
            self.client = None
    
    def translate_text(self, content: str) -> str:
        """Send content to API for translation."""
        if not self.client:
            return content  # Return unchanged if no API key
        
        if not content or len(content) < 50:
            return content  # Skip very short content
        
        try:
            response = self.client.messages.create(
                model=Config.MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": TRANSLATION_PROMPT.format(content=content)
                }]
            )
            
            translated = response.content[0].text.strip()
            
            # Clean up any markdown code blocks if present
            if "```" in translated:
                # Extract content between code blocks
                parts = translated.split("```")
                if len(parts) > 1:
                    # Take the middle part (usually the actual content)
                    translated = parts[1].strip()
                    if translated.startswith("text\n") or translated.startswith("markdown\n"):
                        translated = translated.split("\n", 1)[1] if "\n" in translated else translated
            
            return translated
            
        except Exception as e:
            print(f"      ⚠️  Translation error: {e}")
            return content  # Return original on error
    
    def translate_hub(self, data: dict) -> dict:
        """Translate hub page."""
        print(f"   Translating hub...")
        
        # Description
        desc = get_nested(data, "zones.knowledge.description")
        if desc:
            translated = self.translate_text(desc)
            set_nested(data, "zones.knowledge.description", translated)
            print(f"      ✓ description")
        
        # Reader effect
        effect = get_nested(data, "zones.knowledge.reader_effect")
        if effect:
            translated = self.translate_text(effect)
            set_nested(data, "zones.knowledge.reader_effect", translated)
            print(f"      ✓ reader_effect")
        
        # Worked example effect
        we_effect = get_nested(data, "zones.pedagogy.worked_example.effect")
        if we_effect:
            translated = self.translate_text(we_effect)
            set_nested(data, "zones.pedagogy.worked_example.effect", translated)
            print(f"      ✓ worked_example.effect")
        
        return data
    
    def translate_theme(self, data: dict) -> dict:
        """Translate theme page."""
        theme_slug = data.get("theme_slug", "unknown")
        print(f"   Translating theme: {theme_slug}...")
        
        # Description
        desc = get_nested(data, "zones.knowledge.description")
        if desc:
            translated = self.translate_text(desc)
            set_nested(data, "zones.knowledge.description", translated)
            print(f"      ✓ description")
        
        # Pattern connection
        pc = get_nested(data, "zones.knowledge.pattern_connection")
        if pc:
            translated = self.translate_text(pc)
            set_nested(data, "zones.knowledge.pattern_connection", translated)
            print(f"      ✓ pattern_connection")
        
        # Device examples (array)
        devices = get_nested(data, "zones.knowledge.device_examples")
        if devices:
            for i, dev in enumerate(devices):
                if dev.get("effect"):
                    translated = self.translate_text(dev["effect"])
                    devices[i]["effect"] = translated
            print(f"      ✓ device_examples ({len(devices)} devices)")
        
        # Three steps (array)
        steps = get_nested(data, "zones.pedagogy.three_steps")
        if steps:
            for i, step in enumerate(steps):
                if step.get("content"):
                    translated = self.translate_text(step["content"])
                    steps[i]["content"] = translated
            print(f"      ✓ three_steps ({len(steps)} steps)")
        
        return data
    
    def translate_essay_guide(self, data: dict) -> dict:
        """Translate essay guide page."""
        print(f"   Translating essay_guide...")
        
        # Example theses (array) - translate structure_notes only
        theses = get_nested(data, "zones.knowledge.example_theses")
        if theses:
            for i, thesis in enumerate(theses):
                if thesis.get("structure_notes"):
                    translated = self.translate_text(thesis["structure_notes"])
                    theses[i]["structure_notes"] = translated
            print(f"      ✓ example_theses ({len(theses)} theses)")
        
        # Four steps (array)
        steps = get_nested(data, "zones.pedagogy.four_steps")
        if steps:
            for i, step in enumerate(steps):
                if step.get("content") and len(step["content"]) > 30:
                    translated = self.translate_text(step["content"])
                    steps[i]["content"] = translated
            print(f"      ✓ four_steps")
        
        return data
    
    def load_json(self, filepath: Path) -> dict:
        """Load JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_json(self, filepath: Path, data: dict):
        """Save JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def run(self) -> bool:
        """Run translation on all page JSONs."""
        print("\n" + "="*60)
        print("STAGE 3A: PEDAGOGICAL TRANSLATION")
        print("="*60)
        
        if not self.client:
            print("\n❌ Error: ANTHROPIC_API_KEY not set.")
            print("   Set it with: export ANTHROPIC_API_KEY=your_key")
            return False
        
        print(f"\n📖 Translating content for: {self.book_slug}")
        print(f"   Input: {self.input_dir}")
        
        # Translate hub
        hub_path = self.input_dir / "hub.json"
        if hub_path.exists():
            data = self.load_json(hub_path)
            translated = self.translate_hub(data)
            self.save_json(hub_path, translated)
            print(f"   💾 Saved hub.json")
        else:
            print(f"   ⚠️  hub.json not found at {hub_path}")
        
        # Translate themes
        themes_dir = self.input_dir / "themes"
        if themes_dir.exists():
            theme_files = list(themes_dir.glob("*.json"))
            if theme_files:
                for theme_file in theme_files:
                    data = self.load_json(theme_file)
                    translated = self.translate_theme(data)
                    self.save_json(theme_file, translated)
                    print(f"   💾 Saved themes/{theme_file.name}")
            else:
                print(f"   ⚠️  No theme files found in {themes_dir}")
        else:
            print(f"   ⚠️  themes directory not found at {themes_dir}")
        
        # Translate essay guide
        essay_path = self.input_dir / "essay_guide.json"
        if essay_path.exists():
            data = self.load_json(essay_path)
            translated = self.translate_essay_guide(data)
            self.save_json(essay_path, translated)
            print(f"   💾 Saved essay_guide.json")
        else:
            print(f"   ⚠️  essay_guide.json not found at {essay_path}")
        
        print(f"\n✅ Stage 3A complete")
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Translate page JSONs for Year 10-12 audience',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python translate_content_v1_0.py orbital
    python translate_content_v1_0.py orbital -i outputs/orbital/
        """
    )
    parser.add_argument('book_slug', help='Book slug (e.g., orbital)')
    parser.add_argument('-i', '--input-dir', help='Directory with page JSONs')
    
    args = parser.parse_args()
    
    translator = ContentTranslator(
        args.book_slug,
        input_dir=args.input_dir
    )
    success = translator.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
