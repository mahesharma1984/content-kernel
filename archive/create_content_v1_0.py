#!/usr/bin/env python3
"""
CONTENT CREATION PIPELINE - VERSION 1.0
Transforms kernel JSON → SEO-ready pedagogical HTML

Stages:
1. Extraction (no API)
2. Theme Derivation (API)
3. Thesis Generation (API)  
4. Page Assembly (no API)
5. Pedagogical Translation (API)
6. HTML Generation (no API)

Usage:
    python create_content_v1_0.py Orbital_kernel_v5_0.json
    python create_content_v1_0.py Orbital_kernel_v5_0.json --resume-from stage3
"""

import anthropic
import argparse
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import helper from extract_kernel_v1_0
from extract_kernel_v1_0 import slugify


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000
    OUTPUTS_DIR = Path("outputs")
    SITE_DIR = Path("dist")
    PROMPTS_DIR = Path("prompts")


# =============================================================================
# CONTENT CREATOR
# =============================================================================

class ContentCreator:
    """Six-stage content creation pipeline."""
    
    def __init__(self, kernel_path: str, output_dir: Optional[str] = None):
        self.kernel_path = Path(kernel_path)
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUTS_DIR
        
        # Initialize API client
        if not Config.API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Anthropic(api_key=Config.API_KEY)
        
        # Stage outputs (dependencies)
        self.kernel = None
        self.book_slug = None
        self._stage1_data = None
        self._stage2_data = None
        self._stage3_data = None
        self._stage4_data = None
        self._stage5_data = None
        
        # Stage directory for checkpoints
        self.stage_dir = None
    
    def _get_checkpoint_path(self, stage_name: str) -> Path:
        """Get checkpoint file path for a stage."""
        if not self.book_slug:
            raise ValueError("book_slug must be set before accessing checkpoints")
        
        if not self.stage_dir:
            self.stage_dir = self.output_dir / self.book_slug / "stages"
            self.stage_dir.mkdir(parents=True, exist_ok=True)
        
        return self.stage_dir / f"{stage_name}.json"
    
    def _save_checkpoint(self, stage_name: str, data: dict) -> Path:
        """Save checkpoint file."""
        checkpoint_path = self._get_checkpoint_path(stage_name)
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Checkpoint saved: {checkpoint_path}")
        return checkpoint_path
    
    def _load_checkpoint(self, stage_name: str) -> Optional[dict]:
        """Load checkpoint file if it exists."""
        if not self.book_slug:
            return None
        
        checkpoint_path = self._get_checkpoint_path(stage_name)
        if checkpoint_path.exists():
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded checkpoint: {checkpoint_path}")
            return data
        
        # Also check legacy location for stage1 (from extract_kernel_v1_0.py)
        if stage_name == "content_stage1":
            legacy_path = self.output_dir / self.book_slug / "stage1_extraction.json"
            if legacy_path.exists():
                with open(legacy_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ Loaded checkpoint: {legacy_path}")
                return data
        
        return None
    
    def load_kernel(self) -> bool:
        """Load kernel JSON file."""
        if not self.kernel_path.exists():
            print(f"❌ Kernel not found: {self.kernel_path}")
            return False
        
        with open(self.kernel_path, 'r', encoding='utf-8') as f:
            self.kernel = json.load(f)
        
        # Extract book slug
        title = self.kernel.get('metadata', {}).get('title', '')
        self.book_slug = slugify(title)
        
        print(f"✓ Loaded: {title}")
        return True
    
    def stage1_extraction(self) -> bool:
        """Stage 1: Extract required data from kernel."""
        cached = self._load_checkpoint('content_stage1')
        if cached:
            self._stage1_data = cached
            return True
        
        if not self.kernel:
            print("❌ Error: Kernel not loaded")
            return False
        
        ap = self.kernel.get('alignment_pattern', {})
        meta = self.kernel.get('metadata', {})
        macro = self.kernel.get('macro_variables', {})
        
        # Get device priorities, fallback to extracting from micro_devices
        device_priorities = ap.get('device_priorities', [])
        if not device_priorities:
            device_counts = {}
            for d in self.kernel.get('micro_devices', []):
                name = d.get('name', '')
                device_counts[name] = device_counts.get(name, 0) + 1
            device_priorities = sorted(device_counts.keys(), 
                                       key=lambda x: device_counts[x], 
                                       reverse=True)[:5]
        
        self._stage1_data = {
            "metadata": {
                "title": meta.get('title'),
                "author": meta.get('author'),
                "book_slug": self.book_slug
            },
            "pattern": {
                "name": ap.get('pattern_name'),
                "core_dynamic": ap.get('core_dynamic'),
                "reader_effect": ap.get('reader_effect'),
                "device_priorities": device_priorities
            },
            "macro_variables": macro,
            "micro_devices": self.kernel.get('micro_devices', [])
        }
        
        self._save_checkpoint('content_stage1', self._stage1_data)
        return True
    
    def _call_claude(self, prompt: str) -> str:
        """Make API call to Claude."""
        try:
            response = self.client.messages.create(
                model=Config.MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise
    
    def _build_theme_prompt(self) -> str:
        """Build theme derivation prompt."""
        pattern = self._stage1_data['pattern']
        macro = self._stage1_data['macro_variables']
        devices = self._stage1_data['micro_devices']
        
        # Get sample devices (first 5)
        sample_devices = devices[:5]
        sample_text = "\n".join([
            f"- {d.get('name', '')}: \"{d.get('anchor_phrase', '')}\""
            for d in sample_devices
        ])
        
        # Load prompt template
        prompt_path = Config.PROMPTS_DIR / "derive_themes_v1_0.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            # Fallback template
            template = """Identify 3-4 major themes. Output JSON:
{{
  "themes": [
    {{
      "name": "Theme name",
      "slug": "theme-slug",
      "description": "Description",
      "pattern_connection": "Connection to pattern",
      "device_examples": [
        {{
          "device_name": "Device",
          "quote": "Quote from micro_devices",
          "effect": "Effect"
        }}
      ]
    }}
  ]
}}"""
        
        # Replace placeholders manually to avoid conflicts with JSON braces
        prompt = template.replace('{pattern_name}', pattern['name'])
        prompt = prompt.replace('{core_dynamic}', pattern['core_dynamic'])
        prompt = prompt.replace('{reader_effect}', pattern['reader_effect'])
        prompt = prompt.replace('{tone}', macro.get('rhetoric', {}).get('voice', {}).get('tone', ''))
        prompt = prompt.replace('{device_priorities}', ', '.join(pattern['device_priorities'][:5]))
        prompt = prompt.replace('{device_mediation_summary}', macro.get('device_mediation', {}).get('summary', ''))
        prompt = prompt.replace('{sample_devices}', sample_text)
        
        return prompt
    
    def _parse_themes(self, response: str) -> List[Dict]:
        """Parse themes from API response."""
        # Try to extract JSON from response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```'):
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
        
        try:
            data = json.loads(response)
            return data.get('themes', [])
        except json.JSONDecodeError:
            # Try to find JSON object in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get('themes', [])
                except:
                    pass
            print(f"⚠️  Warning: Could not parse themes JSON")
            return []
    
    def _validate_theme_quotes(self, themes: List[Dict]) -> List[Dict]:
        """Ensure all quotes in themes exist in kernel.micro_devices."""
        kernel_quotes = {d.get('anchor_phrase', '') for d in self._stage1_data['micro_devices']}
        
        for theme in themes:
            for device in theme.get('device_examples', []):
                quote = device.get('quote', '')
                if quote and quote not in kernel_quotes:
                    print(f"⚠️  Quote not in kernel: \"{quote[:30]}...\"")
                    # Try to find closest match
                    for kq in kernel_quotes:
                        if quote.lower() in kq.lower() or kq.lower() in quote.lower():
                            device['quote'] = kq
                            print(f"   → Matched to: \"{kq[:30]}...\"")
                            break
        
        return themes
    
    def stage2_theme_derivation(self) -> bool:
        """Stage 2: Derive themes via API."""
        cached = self._load_checkpoint('content_stage2')
        if cached:
            self._stage2_data = cached
            return True
        
        # DEPENDENCY CHECK
        if not self._stage1_data:
            print("❌ Error: Stage 1 extraction not available")
            return False
        
        # Build prompt
        prompt = self._build_theme_prompt()
        
        # API call
        print("   Calling API for theme derivation...")
        response = self._call_claude(prompt)
        
        # Parse and validate
        themes = self._parse_themes(response)
        
        # Validate quotes exist in kernel
        themes = self._validate_theme_quotes(themes)
        
        if not themes:
            print("❌ Error: No themes generated")
            return False
        
        self._stage2_data = themes
        self._save_checkpoint('content_stage2', self._stage2_data)
        print(f"   ✓ Generated {len(themes)} themes")
        return True
    
    def _build_thesis_prompt(self) -> str:
        """Build thesis generation prompt."""
        pattern = self._stage1_data['pattern']
        themes = self._stage2_data
        
        # Format themes for prompt
        themes_text = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in themes
        ])
        
        # Load prompt template
        prompt_path = Config.PROMPTS_DIR / "generate_thesis_v1_0.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            # Fallback template
            template = """Create 3-4 example thesis statements. Output JSON:
{{
  "theses": [
    {{
      "focus": "Theme-focused",
      "statement": "Thesis statement",
      "structure_notes": "Notes"
    }}
  ]
}}"""
        
        # Replace placeholders manually to avoid conflicts with JSON braces
        prompt = template.replace('{pattern_name}', pattern['name'])
        prompt = prompt.replace('{core_dynamic}', pattern['core_dynamic'])
        prompt = prompt.replace('{reader_effect}', pattern['reader_effect'])
        prompt = prompt.replace('{themes}', themes_text)
        prompt = prompt.replace('{device_priorities}', ', '.join(pattern['device_priorities'][:5]))
        
        return prompt
    
    def _parse_theses(self, response: str) -> List[Dict]:
        """Parse theses from API response."""
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```'):
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
        
        try:
            data = json.loads(response)
            return data.get('theses', [])
        except json.JSONDecodeError:
            # Try to find JSON object in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get('theses', [])
                except:
                    pass
            print(f"⚠️  Warning: Could not parse theses JSON")
            return []
    
    def stage3_thesis_generation(self) -> bool:
        """Stage 3: Generate theses via API."""
        cached = self._load_checkpoint('content_stage3')
        if cached:
            self._stage3_data = cached
            return True
        
        # DEPENDENCY CHECKS
        if not self._stage1_data:
            print("❌ Error: Stage 1 extraction not available")
            return False
        if not self._stage2_data:
            print("❌ Error: Stage 2 themes not available")
            return False
        
        # Build prompt
        prompt = self._build_thesis_prompt()
        
        # API call
        print("   Calling API for thesis generation...")
        response = self._call_claude(prompt)
        
        # Parse
        theses = self._parse_theses(response)
        
        if not theses:
            print("❌ Error: No theses generated")
            return False
        
        self._stage3_data = theses
        self._save_checkpoint('content_stage3', self._stage3_data)
        print(f"   ✓ Generated {len(theses)} theses")
        return True
    
    def _assemble_hub(self) -> dict:
        """Assemble hub page JSON."""
        from assemble_pages_v1_0 import StaticContent
        
        book_slug = self._stage1_data["metadata"]["book_slug"]
        pattern = self._stage1_data["pattern"]
        macro = self._stage1_data["macro_variables"]
        
        # Build worked example formula from top 3 device priorities
        device_priorities = pattern.get("device_priorities", [])
        formula = " + ".join(device_priorities[:3]) if device_priorities else "Device 1 + Device 2 + Device 3"
        
        # Build structure string
        total_chapters = macro.get("structure", {}).get("total_chapters")
        structure_str = f"{total_chapters} chapters" if total_chapters else "Multiple chapters"
        
        # Build theme links
        theme_links = []
        for theme in self._stage2_data:
            theme_links.append({
                "text": theme["name"],
                "url": f"themes/{theme['slug']}/"
            })
        
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
                    "links": theme_links + [
                        {"text": "Build Your Thesis", "url": "essay-guide/", "emphasis": True}
                    ]
                }
            }
        }
        
        return hub
    
    def _assemble_theme(self, theme: dict) -> dict:
        """Assemble a single theme page JSON."""
        from assemble_pages_v1_0 import StaticContent
        
        book_slug = self._stage1_data["metadata"]["book_slug"]
        pattern = self._stage1_data["pattern"]
        
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
    
    def _assemble_essay_guide(self) -> dict:
        """Assemble essay_guide.json."""
        from assemble_pages_v1_0 import StaticContent
        
        book_slug = self._stage1_data["metadata"]["book_slug"]
        title = self._stage1_data["metadata"]["title"]
        pattern = self._stage1_data["pattern"]
        
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
                    "themes": [t["name"] for t in self._stage2_data],
                    "devices": pattern.get("device_priorities", [])[:5]
                },
                "example_theses": self._stage3_data
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
    
    def stage4_page_assembly(self) -> bool:
        """Stage 4: Assemble pages from prior stages."""
        cached = self._load_checkpoint('content_stage4')
        if cached:
            self._stage4_data = cached
            return True
        
        # DEPENDENCY CHECKS (all prior stages)
        if not self._stage1_data:
            print("❌ Error: Stage 1 not available")
            return False
        if not self._stage2_data:
            print("❌ Error: Stage 2 not available")
            return False
        if not self._stage3_data:
            print("❌ Error: Stage 3 not available")
            return False
        
        self._stage4_data = {
            "hub": self._assemble_hub(),
            "themes": [self._assemble_theme(t) for t in self._stage2_data],
            "essay_guide": self._assemble_essay_guide()
        }
        
        self._save_checkpoint('content_stage4', self._stage4_data)
        print(f"   ✓ Assembled 1 hub, {len(self._stage2_data)} themes, 1 essay guide")
        return True
    
    def _translate_content(self, text: str) -> List[Dict]:
        """Translate dense text to structured pedagogical blocks."""
        prompt = f"""Translate this for Year 10-12 students. Output as JSON array of blocks.

Block types:
- {{"type": "statement", "text": "..."}}
- {{"type": "bullets", "items": ["...", "..."]}}
- {{"type": "scaffold", "question": "..."}}
- {{"type": "emphasis", "text": "..."}}

Rules:
- Unpack dense sentences into stages
- Use bullets for lists
- Add scaffold questions where helpful
- Keep academic vocabulary

Content:
{text}

Output ONLY valid JSON array:"""

        response = self._call_claude(prompt)
        
        # Parse JSON
        response = response.strip()
        if response.startswith('```'):
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: wrap in statement block
            return [{"type": "statement", "text": text}]
    
    def _translate_all_pages(self, pages: dict) -> dict:
        """Translate all content fields in pages."""
        translated = {
            "hub": pages["hub"].copy(),
            "themes": [],
            "essay_guide": pages["essay_guide"].copy()
        }
        
        # Translate hub zones
        for zone_name in ["knowledge", "pedagogy"]:
            zone = translated["hub"]["zones"][zone_name]
            if "description" in zone:
                print(f"   Translating hub.{zone_name}.description...")
                zone["description"] = self._translate_content(zone["description"])
            if "reader_effect" in zone:
                print(f"   Translating hub.{zone_name}.reader_effect...")
                zone["reader_effect"] = self._translate_content(zone["reader_effect"])
        
        # Translate theme pages
        for theme in pages["themes"]:
            translated_theme = theme.copy()
            zone = translated_theme["zones"]["knowledge"]
            
            print(f"   Translating theme: {zone['heading']}...")
            if "description" in zone:
                zone["description"] = self._translate_content(zone["description"])
            if "pattern_connection" in zone:
                zone["pattern_connection"] = self._translate_content(zone["pattern_connection"])
            
            translated["themes"].append(translated_theme)
        
        # Translate essay guide
        # (Essay guide typically doesn't need translation as it's more structured)
        
        return translated
    
    def stage5_translation(self) -> bool:
        """Stage 5: Translate content to pedagogical blocks."""
        cached = self._load_checkpoint('content_stage5')
        if cached:
            self._stage5_data = cached
            return True
        
        if not self._stage4_data:
            print("❌ Error: Stage 4 pages not available")
            return False
        
        # Translate each content field
        print("   Translating content to pedagogical blocks...")
        self._stage5_data = self._translate_all_pages(self._stage4_data)
        
        self._save_checkpoint('content_stage5', self._stage5_data)
        print(f"   ✓ Translation complete")
        return True
    
    def _render_blocks(self, blocks: List[Dict]) -> str:
        """Render structured blocks to semantic HTML."""
        html_parts = []
        
        for block in blocks:
            btype = block.get('type', 'statement')
            
            if btype == 'statement':
                html_parts.append(f'<p>{block["text"]}</p>')
            
            elif btype == 'bullets':
                items = '\n'.join(f'    <li>{item}</li>' for item in block['items'])
                html_parts.append(f'<ul class="bullet-list">\n{items}\n</ul>')
            
            elif btype == 'scaffold':
                html_parts.append(f'''<div class="scaffold-question">
    <span class="scaffold-label">Ask yourself:</span>
    <p>{block["question"]}</p>
</div>''')
            
            elif btype == 'emphasis':
                html_parts.append(f'<p class="emphasis"><strong>{block["text"]}</strong></p>')
        
        return '\n\n'.join(html_parts)
    
    def _render_content_field(self, content: Any) -> str:
        """Render a content field (string or blocks) to HTML."""
        if content is None:
            return ''
        if isinstance(content, str):
            return f'<p>{content}</p>'
        elif isinstance(content, list):
            return self._render_blocks(content)
        else:
            return str(content) if content else ''
    
    def stage6_html_generation(self) -> bool:
        """Stage 6: Generate HTML from translated pages."""
        # Try to load stage5 checkpoint if not already loaded
        if not self._stage5_data:
            cached = self._load_checkpoint('content_stage5')
            if cached:
                self._stage5_data = cached
            else:
                print("❌ Error: Stage 5 translated content not available")
                return False
        
        # Load stage1 data if not loaded (needed for metadata)
        if not self._stage1_data:
            cached = self._load_checkpoint('content_stage1')
            if cached:
                self._stage1_data = cached
            else:
                print("❌ Error: Stage 1 extraction not available")
                return False
        
        # Import HTML generation utilities
        from generate_html_v1_0 import CSS, base_template
        
        # Create output directory
        output_path = Config.SITE_DIR / self.book_slug
        output_path.mkdir(parents=True, exist_ok=True)
        
        book_title = self._stage1_data["metadata"]["title"]
        book_author = self._stage1_data["metadata"]["author"]
        
        # Render hub
        hub_data = self._stage5_data["hub"]
        hub_html = self._render_hub_html(hub_data, book_title, book_author)
        (output_path / "index.html").write_text(hub_html, encoding='utf-8')
        print(f"   ✓ index.html (hub)")
        
        # Render themes
        themes_dir = output_path / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        for theme in self._stage5_data["themes"]:
            theme_slug = theme["theme_slug"]
            theme_html = self._render_theme_html(theme, book_title, self.book_slug)
            (themes_dir / theme_slug).mkdir(parents=True, exist_ok=True)
            (themes_dir / theme_slug / "index.html").write_text(theme_html, encoding='utf-8')
            print(f"   ✓ themes/{theme_slug}/index.html")
        
        # Render essay guide
        essay_guide = self._stage5_data["essay_guide"]
        essay_html = self._render_essay_guide_html(essay_guide, book_title, self.book_slug)
        (output_path / "essay-guide").mkdir(parents=True, exist_ok=True)
        (output_path / "essay-guide" / "index.html").write_text(essay_html, encoding='utf-8')
        print(f"   ✓ essay-guide/index.html")
        
        print(f"\n✅ HTML generation complete")
        print(f"   Output: {output_path}")
        return True
    
    def _render_hub_html(self, data: dict, book_title: str, book_author: str) -> str:
        """Render hub page with block support."""
        from generate_html_v1_0 import base_template
        
        z = data["zones"]
        k, p, c = z["knowledge"], z["pedagogy"], z["cta"]
        
        # Theme links
        links = ""
        for link in c["links"]:
            cls = "cta-link emphasis" if link.get("emphasis") else "cta-link"
            links += f'<a href="{link["url"]}" class="{cls}">{link["text"]}</a>\n'
        
        # Prompts
        prompts = "".join(f"<li>{pr}</li>" for pr in p.get("prompts", []))
        
        # Render description and reader_effect with block support
        description_html = self._render_content_field(k.get("description", ""))
        reader_effect_html = self._render_content_field(k.get("reader_effect", ""))
        
        content = f"""
        <header class="page-header">
            <h1>{book_title}</h1>
            <p class="subtitle">by {book_author}</p>
        </header>

        <section class="zone zone-knowledge">
            <span class="zone-badge">{k["badge"]}</span>
            <h2>{k["heading"]}</h2>
            {description_html}
            <p><strong>Reader Effect:</strong></p>
            {reader_effect_html}
            
            <div class="quick-reference">
                <div class="quick-ref-item">
                    <div class="label">Structure</div>
                    <div class="value">{k["quick_reference"]["structure"]}</div>
                </div>
                <div class="quick-ref-item">
                    <div class="label">Voice</div>
                    <div class="value">{k["quick_reference"]["voice"]}</div>
                </div>
                <div class="quick-ref-item">
                    <div class="label">Tone</div>
                    <div class="value">{k["quick_reference"]["tone"]}</div>
                </div>
            </div>
        </section>

        <section class="zone zone-pedagogy">
            <span class="zone-badge">{p["badge"]}</span>
            <h2>{p["heading"]}</h2>
            
            <div class="worked-example">
                <div class="formula">{p["worked_example"]["formula"]}</div>
                <div class="arrow">{p["worked_example"]["arrow"]}</div>
                <div class="effect">{p["worked_example"]["effect"]}</div>
            </div>
            
            <ul class="prompts">{prompts}</ul>
        </section>

        <section class="zone zone-cta">
            <span class="zone-badge">{c["badge"]}</span>
            <div class="cta-links">{links}</div>
        </section>
    """
        
        return base_template(f"{book_title} Analysis", content)
    
    def _render_theme_html(self, data: dict, book_title: str, book_slug: str) -> str:
        """Render theme page with block support."""
        from generate_html_v1_0 import base_template
        
        z = data["zones"]
        k, p, c = z["knowledge"], z["pedagogy"], z["cta"]
        
        # Device examples
        devices = ""
        for dev in k.get("device_examples", []):
            devices += f"""
        <div class="device-example">
            <div class="device-name">{dev["device_name"]}</div>
            <div class="device-quote">"{dev["quote"]}"</div>
            <div class="device-effect">{dev["effect"]}</div>
        </div>"""
        
        # Steps
        steps = ""
        for step in p.get("three_steps", []):
            steps += f"""
        <div class="step">
            <div class="step-number">{step["step"]}</div>
            <div class="step-content">
                <h3>{step["title"]}</h3>
                <p>{step["content"]}</p>
            </div>
        </div>"""
        
        # Links
        links = ""
        for link in c.get("links", []):
            links += f'<a href="{link["url"]}" class="cta-link">{link["text"]}</a>\n'
        
        breadcrumb = f"""
        <nav class="breadcrumb">
            <a href="/{book_slug}/">{book_title}</a>
            <span class="sep">›</span>
            <a href="/{book_slug}/">Themes</a>
            <span class="sep">›</span>
            {k["heading"]}
        </nav>
    """
        
        # Render description and pattern_connection with block support
        description_html = self._render_content_field(k.get("description", ""))
        pattern_connection_html = self._render_content_field(k.get("pattern_connection", ""))
        
        content = f"""
        <header class="page-header">
            <h1>{k["heading"]}</h1>
            <p class="subtitle">Theme Analysis</p>
        </header>

        <section class="zone zone-knowledge">
            <span class="zone-badge">{k["badge"]}</span>
            <h2>{k["heading"]}</h2>
            {description_html}
            
            <div class="pattern-connection">
                <div class="pattern-connection-label">Pattern Connection</div>
                {pattern_connection_html}
            </div>
            
            <div class="device-examples">
                <h3>Device Examples</h3>
                {devices}
            </div>
        </section>

        <section class="zone zone-pedagogy">
            <span class="zone-badge">{p["badge"]}</span>
            <h2>How to Analyze This Theme</h2>
            <div class="steps">{steps}</div>
        </section>

        <section class="zone zone-cta">
            <span class="zone-badge">{c["badge"]}</span>
            <div class="cta-links">{links}</div>
        </section>
    """
        
        return base_template(f"{k['heading']} | {book_title}", content, breadcrumb)
    
    def _render_essay_guide_html(self, data: dict, book_title: str, book_slug: str) -> str:
        """Render essay guide page."""
        from generate_html_v1_0 import base_template, render_essay_guide
        
        # Use existing render function for essay guide (it's more structured)
        return render_essay_guide(data, book_title, book_slug)
    
    def run(self, resume_from: Optional[str] = None, 
            stop_after: Optional[str] = None,
            include_render: bool = False) -> bool:
        """Run the full pipeline."""
        print(f"\n{'='*60}")
        print(f"CONTENT CREATION PIPELINE v1.0")
        print(f"{'='*60}")
        
        if not self.load_kernel():
            return False
        
        # Load kernel first to get book info
        if not self.kernel:
            if not self.load_kernel():
                return False
        
        print(f"Book: {self.kernel.get('metadata', {}).get('title', 'Unknown')}")
        print(f"Output: {self.output_dir}/{self.book_slug}/")
        
        stages = [
            ("Stage 1: Extraction", self.stage1_extraction, "stage1"),
            ("Stage 2: Theme Derivation", self.stage2_theme_derivation, "stage2"),
            ("Stage 3: Thesis Generation", self.stage3_thesis_generation, "stage3"),
            ("Stage 4: Page Assembly", self.stage4_page_assembly, "stage4"),
            ("Stage 5: Translation", self.stage5_translation, "stage5"),
        ]
        
        # Stage 6 is optional
        if include_render:
            stages.append(("Stage 6: HTML Generation", self.stage6_html_generation, "stage6"))
        
        # Determine start index
        start_idx = 0
        if resume_from:
            stage_map = {"stage1": 0, "stage2": 1, "stage3": 2, "stage4": 3, "stage5": 4, "stage6": 5}
            if resume_from in stage_map:
                start_idx = stage_map[resume_from]
                print(f"\n🔄 Resuming from {resume_from}")
            else:
                print(f"⚠️  Unknown resume point: {resume_from}, starting from beginning")
        
        # Run stages
        for idx, (name, stage_fn, stage_id) in enumerate(stages):
            if idx < start_idx:
                continue
            
            print(f"\n{'='*60}\n{name}\n{'='*60}")
            if not stage_fn():
                print(f"\n❌ Pipeline failed at {name}")
                return False
            
            if stop_after and stage_id == stop_after:
                print(f"\n⏸️  Stopping after {name}")
                return True
        
        # Stage 6 is optional
        if include_render:
            print(f"\n✅ Content generation complete")
            print(f"   HTML: {Config.SITE_DIR}/{self.book_slug}/")
        else:
            print(f"\n✅ Content generation complete (Stage 1-5)")
            print(f"   Content: {self.output_dir}/{self.book_slug}/stages/content_stage5.json")
            print(f"   To render: python render_html_v1_0.py {self.output_dir}/{self.book_slug}/")
        
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Content Creation Pipeline v1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python create_content_v1_0.py Orbital_kernel_v5_0.json
    python create_content_v1_0.py Orbital_kernel_v5_0.json --resume-from stage3
    python create_content_v1_0.py Orbital_kernel_v5_0.json --stop-after stage1
        """
    )
    parser.add_argument('kernel', help='Path to kernel JSON file')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: outputs/)')
    parser.add_argument('--resume-from', help='Resume from stage (stage1-stage6)')
    parser.add_argument('--stop-after', help='Stop after stage (stage1-stage6)')
    parser.add_argument('--render', action='store_true', 
                        help='Include HTML generation (Stage 6)')
    
    args = parser.parse_args()
    
    try:
        creator = ContentCreator(args.kernel, args.output_dir)
        success = creator.run(
            resume_from=args.resume_from,
            stop_after=args.stop_after,
            include_render=args.render
        )
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
