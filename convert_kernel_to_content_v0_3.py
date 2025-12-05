#!/usr/bin/env python3
"""
Kernel to Student Content Converter
Version: 0.3

Takes: kernel JSON + optional reasoning doc
Returns: structured plain-language content for mobile site

Changes from v0.2:
- Can work WITHOUT ReasoningDoc (derives pattern from kernel macro vars)
- Generates synthetic reasoning context from kernel if no doc provided
- Better pattern derivation from code combinations

Usage:
    # With ReasoningDoc (best quality)
    python convert_kernel_to_content_v0_3.py kernels/Book_kernel.json kernels/Book_ReasoningDoc.md
    
    # Kernel-only mode (derives pattern from macro vars)
    python convert_kernel_to_content_v0_3.py kernels/Book_kernel.json
    
    # Auto-detect by title
    python convert_kernel_to_content_v0_3.py --title "Matilda"
"""

import json
import argparse
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Configuration settings"""
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 8192
    
    KERNELS_DIR = Path("kernels")
    OUTPUTS_DIR = Path("outputs")
    
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    CONVERTER_VERSION = "0.3"
    OUTPUT_SCHEMA_VERSION = "1.0"


# =============================================================================
# PATTERN DERIVATION FROM CODES
# =============================================================================

# Map code combinations to pattern names
PATTERN_MAP = {
    # First-person patterns
    ("FP", "INT", "RETRO", "ADV"): "Nostalgic Instruction",
    ("FP", "INT", "RETRO", "OBJ"): "Retrospective Witness",
    ("FP", "INT", "SIM", "ADV"): "Immediate Advocacy",
    ("FP", "INT", "SIM", "OBJ"): "Present Witness",
    
    # Third-person omniscient patterns
    ("TPO", "ZERO", "HEAVY", "ADV"): "Intrusive Advocacy",
    ("TPO", "ZERO", "SOME", "ADV"): "Guided Omniscience",
    ("TPO", "ZERO", "NONE", "OBJ"): "Detached Omniscience",
    ("TPO", "ZERO", "HEAVY", "OBJ"): "Ironic Omniscience",
    
    # Third-person limited patterns
    ("TPL", "INT", "NONE", "OBJ"): "Stoic Witnessing",
    ("TPL", "INT", "NONE", "ADV"): "Focused Advocacy",
    ("TPL", "INT", "SOME", "ADV"): "Intimate Guidance",
    ("TPL", "INT", "SOME", "OBJ"): "Close Observation",
}


def derive_pattern_from_kernel(kernel: dict) -> dict:
    """
    Derive alignment pattern from kernel macro variables.
    Returns dict with pattern_name, core_dynamic, reader_effect.
    """
    macro = kernel.get("macro_variables", {})
    narrative = macro.get("narrative", {})
    rhetoric = macro.get("rhetoric", {})
    
    # Extract key codes
    voice = narrative.get("voice", {})
    pov = voice.get("pov", "TPO")
    focalization = voice.get("focalization", "INT")
    intrusion = voice.get("narrative_intrusion", "NONE")
    temporal = voice.get("temporal_distance", "SIM")
    
    rhet_voice = rhetoric.get("voice", {})
    stance = rhet_voice.get("stance", "OBJ")
    tone = rhet_voice.get("tone", "Neutral")
    
    # Try to match pattern
    key = (pov, focalization, intrusion, stance)
    pattern_name = PATTERN_MAP.get(key)
    
    # Fallback: generate from components
    if not pattern_name:
        # Build descriptive name from codes
        pov_desc = {"FP": "Personal", "TPO": "Omniscient", "TPL": "Focused"}.get(pov, "")
        stance_desc = {"ADV": "Advocacy", "OBJ": "Observation", "CRIT": "Critique"}.get(stance, "")
        intrusion_desc = {"HEAVY": "Guided", "SOME": "Moderate", "NONE": "Restrained"}.get(intrusion, "")
        
        if intrusion_desc and stance_desc:
            pattern_name = f"{intrusion_desc} {stance_desc}"
        else:
            pattern_name = f"{pov_desc} {stance_desc}"
    
    # Generate dynamic description
    pov_effect = {
        "FP": "gives us intimate access to one perspective",
        "TPO": "lets the narrator see everything and comment freely",
        "TPL": "keeps us close to one character's experience"
    }.get(pov, "shapes our access to the story")
    
    stance_effect = {
        "ADV": "guiding us toward a clear position",
        "OBJ": "letting us draw our own conclusions",
        "CRIT": "questioning what we see"
    }.get(stance, "shaping how we respond")
    
    intrusion_effect = {
        "HEAVY": "The narrator frequently interrupts to comment and guide",
        "SOME": "The narrator occasionally steps in to clarify",
        "NONE": "The narrator stays invisible, just showing"
    }.get(intrusion, "")
    
    core_dynamic = f"The {pov} perspective {pov_effect}, while the {stance} stance means the text is {stance_effect}."
    
    reader_effect = f"{intrusion_effect}. Combined with {tone.lower() if tone else 'the overall'} tone, this creates a distinctive reading experience."
    
    return {
        "pattern_name": pattern_name,
        "core_dynamic": core_dynamic,
        "reader_effect": reader_effect,
        "codes": {
            "pov": pov,
            "focalization": focalization,
            "intrusion": intrusion,
            "stance": stance,
            "tone": tone
        }
    }


def generate_synthetic_reasoning(kernel: dict) -> str:
    """
    Generate a synthetic reasoning context from kernel macro variables.
    Used when no ReasoningDoc is provided.
    """
    pattern = derive_pattern_from_kernel(kernel)
    macro = kernel.get("macro_variables", {})
    devices = kernel.get("micro_devices", [])
    
    # Group devices by section
    devices_by_section = {}
    for d in devices:
        section = d.get("assigned_section", "unknown")
        if section not in devices_by_section:
            devices_by_section[section] = []
        devices_by_section[section].append(d.get("name", "Unknown"))
    
    # Build synthetic reasoning
    lines = [
        f"## 1. Alignment Pattern",
        f"",
        f"**Pattern**: {pattern['pattern_name']}",
        f"",
        f"**Core Dynamic**: {pattern['core_dynamic']}",
        f"",
        f"**Reader Effect**: {pattern['reader_effect']}",
        f"",
        f"## 2. Macro Variable Summary",
        f"",
    ]
    
    # Add narrative voice summary
    nv = macro.get("narrative", {}).get("voice", {})
    lines.append(f"**Narrative Voice**: {nv.get('pov', '')} POV with {nv.get('focalization', '')} focalization, "
                 f"{nv.get('reliability', '')} narrator, {nv.get('narrative_intrusion', '')} intrusion.")
    
    # Add rhetorical voice summary
    rv = macro.get("rhetoric", {}).get("voice", {})
    lines.append(f"")
    lines.append(f"**Rhetorical Voice**: {rv.get('stance', '')} stance, {rv.get('tone', '')} tone, "
                 f"{rv.get('pathos', '')} pathos.")
    
    # Add device summary
    lines.append(f"")
    lines.append(f"## 3. Device Distribution")
    lines.append(f"")
    for section in ["exposition", "rising_action", "climax", "falling_action", "resolution"]:
        section_devices = devices_by_section.get(section, [])
        if section_devices:
            lines.append(f"**{section.replace('_', ' ').title()}**: {', '.join(section_devices)}")
    
    # Add mediation summary
    mediation = macro.get("device_mediation", {}).get("summary", "")
    if mediation:
        lines.append(f"")
        lines.append(f"## 4. Alignment Effect")
        lines.append(f"")
        lines.append(mediation)
    
    return "\n".join(lines)


# =============================================================================
# FILE DETECTION
# =============================================================================

def safe_title(title: str) -> str:
    """Convert title to safe filename format."""
    safe = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    return safe.replace(' ', '_')


def find_kernel_path(text_title: str, kernels_dir: Path = None) -> Optional[Path]:
    """Find kernel JSON file for a given text title."""
    kernels_dir = kernels_dir or Config.KERNELS_DIR
    if not kernels_dir.exists():
        return None
    
    pattern = f"{safe_title(text_title)}_kernel*.json"
    matches = list(kernels_dir.glob(pattern))
    
    if matches:
        return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


def find_reasoning_doc_path(text_title: str, kernels_dir: Path = None) -> Optional[Path]:
    """Find reasoning document for a given text title."""
    kernels_dir = kernels_dir or Config.KERNELS_DIR
    if not kernels_dir.exists():
        return None
    
    pattern = f"{safe_title(text_title)}_ReasoningDoc*.md"
    matches = list(kernels_dir.glob(pattern))
    
    if matches:
        return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


# =============================================================================
# FILE LOADING
# =============================================================================

def load_kernel(kernel_path: Path) -> dict:
    """Load kernel JSON file."""
    with open(kernel_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_reasoning_doc(reasoning_path: Path) -> str:
    """Load reasoning doc markdown file."""
    with open(reasoning_path, 'r', encoding='utf-8') as f:
        return f.read()


# =============================================================================
# JSON CLEANING
# =============================================================================

def clean_json_response(response_text: str) -> str:
    """Clean API response to extract valid JSON."""
    text = response_text.strip()
    
    # Remove markdown code blocks
    text = re.sub(r'^```json\s*\n?', '', text)
    text = re.sub(r'^```\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    
    # Handle nested code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_block = not in_block
                continue
            if in_block:
                json_lines.append(line)
        text = "\n".join(json_lines)
    
    return text.strip()


# =============================================================================
# PROMPT BUILDING
# =============================================================================

def build_conversion_prompt(kernel: dict, reasoning_context: str, is_synthetic: bool = False) -> str:
    """Build the prompt that instructs the API to convert kernel to student content."""
    
    title = kernel.get('metadata', {}).get('title', 'Unknown').strip()
    author = kernel.get('metadata', {}).get('author', 'Unknown').strip()
    
    context_note = ""
    if is_synthetic:
        context_note = """
NOTE: The reasoning context below was derived from the kernel's macro variables. 
Use it as a guide but prioritize the actual kernel data for specific details."""
    
    return f"""You are converting a technical literary analysis kernel into plain-language content for high school students studying for essays.

## INPUT: KERNEL
```json
{json.dumps(kernel, indent=2)}
```

## INPUT: REASONING CONTEXT
{context_note}
{reasoning_context}

## YOUR TASK

Convert this technical analysis into student-accessible content for "{title}" by {author}. 

A Year 9 student should be able to read and understand every sentence.

## OUTPUT FORMAT

Return a JSON object with this exact structure:

```json
{{
  "metadata": {{
    "title": "Text title",
    "author": "Author name"
  }},
  
  "layer_1_whats_happening": {{
    "who_tells_it": "One sentence. Who narrates? What's their perspective? Use plain language.",
    "what_we_experience": "One sentence. What happens in the story? No jargon.",
    "how_it_feels": "One sentence. What emotions does the reader feel?"
  }},
  
  "layer_2_meaning_by_section": [
    {{
      "section": "Exposition",
      "meaning": "What meaning is created in this section? One sentence, plain language.",
      "quote": "Key quote from this section (use anchor_phrase from kernel micro_devices)",
      "quote_chapter": 1,
      "devices_supporting": "Which devices support this meaning and how? Brief."
    }},
    {{
      "section": "Rising Action",
      "meaning": "...",
      "quote": "...",
      "quote_chapter": 0,
      "devices_supporting": "..."
    }},
    {{
      "section": "Climax",
      "meaning": "...",
      "quote": "...",
      "quote_chapter": 0,
      "devices_supporting": "..."
    }},
    {{
      "section": "Falling Action",
      "meaning": "...",
      "quote": "...",
      "quote_chapter": 0,
      "devices_supporting": "..."
    }},
    {{
      "section": "Resolution",
      "meaning": "...",
      "quote": "...",
      "quote_chapter": 0,
      "devices_supporting": "..."
    }}
  ],
  
  "layer_3_connections": {{
    "step_1": "First part of how the elements work together. Start with what the narrative voice lets us SEE or EXPERIENCE.",
    "step_2": "Second part. What does another element let us UNDERSTAND or FEEL?",
    "step_3": "The combined effect. 'Together: [what happens]'",
    "pattern_name": "The alignment pattern name",
    "pattern_explanation": "One sentence explaining why this name fits"
  }},
  
  "layer_4_thesis": {{
    "components": {{
      "who_tells_it": "Brief phrase",
      "what_they_reveal": "Brief phrase", 
      "story_type": "Brief phrase",
      "larger_meaning": "Brief phrase",
      "method": "Brief phrase - how it achieves this without being heavy-handed"
    }},
    "thesis_sentence": "The full thesis, built from the components above. Should be one clear sentence a student can copy into an essay."
  }}
}}
```

## CRITICAL RULES

1. PLAIN LANGUAGE: No technical terms without explanation. "Third-person omniscient with heavy intrusion" → "An all-knowing narrator who constantly comments and guides us"

2. MEANING FIRST: Devices serve meaning. Don't say "Dahl uses hyperbole." Say "Everything is exaggerated to make us laugh at how ridiculous the adults are."

3. SHOW THE REASONING: The connections section should make the reader think "oh, THAT'S why it works."

4. USABLE THESIS: The thesis should be something a student can actually put in an essay. Not too long, not too abstract.

5. QUOTES FROM KERNEL: Use the anchor_phrase or quote_snippet values from micro_devices. These are the actual quotes.

6. CHAPTER NUMBERS: quote_chapter must be an integer from the kernel data.

Return ONLY the JSON object. No explanation before or after."""


# =============================================================================
# OUTPUT VALIDATION
# =============================================================================

def validate_output(content: dict) -> tuple[bool, list[str]]:
    """Validate the converted content has required structure."""
    errors = []
    
    required_keys = ['metadata', 'layer_1_whats_happening', 'layer_2_meaning_by_section', 
                     'layer_3_connections', 'layer_4_thesis']
    for key in required_keys:
        if key not in content:
            errors.append(f"Missing required key: {key}")
    
    if 'layer_1_whats_happening' in content:
        l1 = content['layer_1_whats_happening']
        for field in ['who_tells_it', 'what_we_experience', 'how_it_feels']:
            if field not in l1:
                errors.append(f"Layer 1 missing: {field}")
    
    if 'layer_2_meaning_by_section' in content:
        sections = content['layer_2_meaning_by_section']
        if not isinstance(sections, list):
            errors.append("Layer 2 should be a list")
        elif len(sections) != 5:
            errors.append(f"Layer 2 should have 5 sections, got {len(sections)}")
    
    if 'layer_3_connections' in content:
        l3 = content['layer_3_connections']
        for field in ['step_1', 'step_2', 'step_3', 'pattern_name']:
            if field not in l3:
                errors.append(f"Layer 3 missing: {field}")
    
    if 'layer_4_thesis' in content:
        l4 = content['layer_4_thesis']
        if 'thesis_sentence' not in l4:
            errors.append("Layer 4 missing: thesis_sentence")
    
    return len(errors) == 0, errors


# =============================================================================
# API CALL
# =============================================================================

def call_api(client: anthropic.Anthropic, prompt: str) -> str:
    """Call Claude API with retry logic."""
    
    for attempt in range(Config.MAX_RETRIES):
        try:
            print(f"  API call attempt {attempt + 1}/{Config.MAX_RETRIES}...")
            
            message = client.messages.create(
                model=Config.MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except anthropic.RateLimitError:
            if attempt < Config.MAX_RETRIES - 1:
                wait_time = Config.RETRY_DELAY * (attempt + 1)
                print(f"  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except anthropic.APIError as e:
            if attempt < Config.MAX_RETRIES - 1:
                print(f"  API error: {e}. Retrying...")
                time.sleep(Config.RETRY_DELAY)
            else:
                raise
    
    raise RuntimeError("Max retries exceeded")


# =============================================================================
# MAIN CONVERSION
# =============================================================================

def convert_kernel_to_content(
    kernel: dict, 
    reasoning_doc: str = None,
    api_key: str = None
) -> dict:
    """
    Convert kernel + optional reasoning doc to student content.
    
    If no reasoning_doc provided, generates synthetic reasoning from kernel.
    """
    client = anthropic.Anthropic(api_key=api_key or Config.API_KEY)
    
    if not client.api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    # Determine reasoning context
    is_synthetic = False
    if reasoning_doc:
        reasoning_context = reasoning_doc
        print("  Using provided ReasoningDoc")
    else:
        reasoning_context = generate_synthetic_reasoning(kernel)
        is_synthetic = True
        print("  Generated synthetic reasoning from kernel")
        
        # Show derived pattern
        pattern = derive_pattern_from_kernel(kernel)
        print(f"  Derived pattern: {pattern['pattern_name']}")
    
    prompt = build_conversion_prompt(kernel, reasoning_context, is_synthetic)
    
    print("\nConverting via API...")
    response_text = call_api(client, prompt)
    
    # Clean and parse JSON
    cleaned = clean_json_response(response_text)
    
    try:
        content = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response (first 500 chars): {response_text[:500]}")
        raise
    
    # Validate
    is_valid, errors = validate_output(content)
    if not is_valid:
        print("⚠️  Validation warnings:")
        for err in errors:
            print(f"    - {err}")
    
    # Add metadata
    content['_converter_metadata'] = {
        'converter_version': Config.CONVERTER_VERSION,
        'schema_version': Config.OUTPUT_SCHEMA_VERSION,
        'generated_at': datetime.now().isoformat(),
        'source_kernel_version': kernel.get('metadata', {}).get('kernel_version', 'unknown'),
        'reasoning_source': 'provided' if not is_synthetic else 'synthetic'
    }
    
    return content


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert kernel + optional reasoning doc to student-facing content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With ReasoningDoc (best quality)
  python convert_kernel_to_content_v0_3.py kernels/TKAM_kernel.json kernels/TKAM_ReasoningDoc.md
  
  # Kernel-only (derives pattern from macro vars)
  python convert_kernel_to_content_v0_3.py kernels/Matilda_kernel.json
  
  # Auto-detect by title
  python convert_kernel_to_content_v0_3.py --title "Matilda"
"""
    )
    
    parser.add_argument("kernel", nargs='?', help="Path to kernel JSON file")
    parser.add_argument("reasoning", nargs='?', help="Path to reasoning doc (optional)")
    parser.add_argument("--title", "-t", help="Text title (auto-detects files)")
    parser.add_argument("--kernels-dir", help="Directory containing kernels", default="kernels")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("--api-key", help="Anthropic API key")
    
    args = parser.parse_args()
    
    # Resolve input files
    kernel_path = None
    reasoning_path = None
    
    if args.title:
        kernels_dir = Path(args.kernels_dir)
        print(f"Auto-detecting files for: {args.title}")
        
        kernel_path = find_kernel_path(args.title, kernels_dir)
        reasoning_path = find_reasoning_doc_path(args.title, kernels_dir)
        
        if not kernel_path:
            print(f"❌ Could not find kernel for '{args.title}' in {kernels_dir}")
            sys.exit(1)
            
        print(f"  Found kernel: {kernel_path.name}")
        if reasoning_path:
            print(f"  Found reasoning: {reasoning_path.name}")
        else:
            print(f"  No ReasoningDoc found - will derive from kernel")
        
    elif args.kernel:
        kernel_path = Path(args.kernel)
        if args.reasoning:
            reasoning_path = Path(args.reasoning)
        
        if not kernel_path.exists():
            print(f"❌ Kernel file not found: {kernel_path}")
            sys.exit(1)
        if reasoning_path and not reasoning_path.exists():
            print(f"⚠️  ReasoningDoc not found: {reasoning_path} - will derive from kernel")
            reasoning_path = None
    else:
        parser.error("Provide either --title OR kernel path")
    
    # Load inputs
    print(f"\nLoading kernel: {kernel_path}")
    kernel = load_kernel(kernel_path)
    
    reasoning_doc = None
    if reasoning_path:
        print(f"Loading reasoning doc: {reasoning_path}")
        reasoning_doc = load_reasoning_doc(reasoning_path)
    
    # Get title for output naming
    title = kernel.get('metadata', {}).get('title', 'Unknown').strip()
    
    # Convert
    content = convert_kernel_to_content(kernel, reasoning_doc, args.api_key)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        Config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = Config.OUTPUTS_DIR / f"{safe_title(title)}_content_v{Config.OUTPUT_SCHEMA_VERSION}.json"
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)
    
    print(f"\n✅ Output written to: {output_path}")
    
    is_valid, errors = validate_output(content)
    if is_valid:
        print("✅ Output validation: PASSED")
    else:
        print(f"⚠️  Output validation: {len(errors)} warnings")
    
    return content


if __name__ == "__main__":
    main()
