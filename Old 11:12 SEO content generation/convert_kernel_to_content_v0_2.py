#!/usr/bin/env python3
"""
Kernel to Student Content Converter
Version: 0.2

Takes: kernel JSON + reasoning doc (or auto-detects by title)
Returns: structured plain-language content for mobile site

Changes from v0.1:
- Config class (borrowed from create_kernel.py)
- Auto-detect files by title (borrowed from run_stage2.py)
- Better JSON cleaning
- Output validation
- Version tracking in output
- Retry logic for API failures

Usage:
    # Explicit paths
    python convert_kernel_to_content.py kernels/Book_kernel_v4_0.json kernels/Book_ReasoningDoc_v4_1.md
    
    # Auto-detect by title
    python convert_kernel_to_content.py --title "To Kill a Mockingbird"
    
    # Custom output path
    python convert_kernel_to_content.py --title "The Giver" -o outputs/giver_content.json
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
# CONFIGURATION (borrowed from create_kernel.py)
# =============================================================================

class Config:
    """Configuration settings"""
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 8192
    
    # Directories
    KERNELS_DIR = Path("kernels")
    OUTPUTS_DIR = Path("outputs")
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    # Version tracking
    CONVERTER_VERSION = "0.2"
    OUTPUT_SCHEMA_VERSION = "1.0"


# =============================================================================
# FILE DETECTION (borrowed from run_stage2.py)
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
        # Return most recently modified
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
# JSON CLEANING (improved from create_kernel.py)
# =============================================================================

def clean_json_response(response_text: str) -> str:
    """
    Clean API response to extract valid JSON.
    Handles markdown code blocks and common formatting issues.
    """
    text = response_text.strip()
    
    # Remove markdown code blocks
    if text.startswith("```"):
        # Find the actual JSON start
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
    
    # Alternative: just strip ```json and ``` markers
    text = re.sub(r'^```json\s*\n?', '', text)
    text = re.sub(r'^```\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    
    return text.strip()


# =============================================================================
# PROMPT BUILDING
# =============================================================================

def build_conversion_prompt(kernel: dict, reasoning_doc: str) -> str:
    """Build the prompt that instructs the API to convert kernel to student content."""
    
    # Extract key info for more focused prompt
    title = kernel.get('metadata', {}).get('title', 'Unknown').strip()
    author = kernel.get('metadata', {}).get('author', 'Unknown').strip()
    
    return f"""You are converting a technical literary analysis kernel into plain-language content for high school students studying for essays.

## INPUT: KERNEL
```json
{json.dumps(kernel, indent=2)}
```

## INPUT: REASONING DOC
{reasoning_doc}

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
    "pattern_name": "The alignment pattern name from the reasoning doc",
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

1. PLAIN LANGUAGE: No technical terms without explanation. "First-person retrospective narration" → "Scout tells the story, looking back as an adult"

2. MEANING FIRST: Devices serve meaning. Don't say "Lee uses foreshadowing." Say "Something dark is coming — we feel it through hints early on."

3. SHOW THE REASONING: The connections section should make the reader think "oh, THAT'S why it works."

4. USABLE THESIS: The thesis should be something a student can actually put in an essay. Not too long, not too abstract.

5. QUOTES FROM KERNEL: Use the anchor_phrase values from micro_devices in the kernel. These are the actual quotes.

6. CHAPTER NUMBERS: quote_chapter must be an integer, taken from the chapter field in micro_devices.

Return ONLY the JSON object. No explanation before or after."""


# =============================================================================
# OUTPUT VALIDATION
# =============================================================================

def validate_output(content: dict) -> tuple[bool, list[str]]:
    """
    Validate the converted content has required structure.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    # Check top-level keys
    required_keys = ['metadata', 'layer_1_whats_happening', 'layer_2_meaning_by_section', 
                     'layer_3_connections', 'layer_4_thesis']
    for key in required_keys:
        if key not in content:
            errors.append(f"Missing required key: {key}")
    
    # Check layer 1
    if 'layer_1_whats_happening' in content:
        l1 = content['layer_1_whats_happening']
        for field in ['who_tells_it', 'what_we_experience', 'how_it_feels']:
            if field not in l1:
                errors.append(f"Layer 1 missing: {field}")
    
    # Check layer 2 has 5 sections
    if 'layer_2_meaning_by_section' in content:
        sections = content['layer_2_meaning_by_section']
        if not isinstance(sections, list):
            errors.append("Layer 2 should be a list")
        elif len(sections) != 5:
            errors.append(f"Layer 2 should have 5 sections, got {len(sections)}")
        else:
            expected_sections = ['Exposition', 'Rising Action', 'Climax', 'Falling Action', 'Resolution']
            for i, section in enumerate(sections):
                if section.get('section') != expected_sections[i]:
                    errors.append(f"Layer 2 section {i} should be '{expected_sections[i]}', got '{section.get('section')}'")
    
    # Check layer 3
    if 'layer_3_connections' in content:
        l3 = content['layer_3_connections']
        for field in ['step_1', 'step_2', 'step_3', 'pattern_name']:
            if field not in l3:
                errors.append(f"Layer 3 missing: {field}")
    
    # Check layer 4
    if 'layer_4_thesis' in content:
        l4 = content['layer_4_thesis']
        if 'thesis_sentence' not in l4:
            errors.append("Layer 4 missing: thesis_sentence")
        if 'components' not in l4:
            errors.append("Layer 4 missing: components")
    
    return len(errors) == 0, errors


# =============================================================================
# API CALL WITH RETRY (borrowed pattern from create_kernel.py)
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
    reasoning_doc: str, 
    api_key: str = None
) -> dict:
    """
    Call Claude API to convert kernel + reasoning doc to student content.
    
    Args:
        kernel: Parsed kernel JSON
        reasoning_doc: Raw reasoning doc text
        api_key: Anthropic API key (uses env var if not provided)
    
    Returns:
        Structured content dict with version metadata
    """
    client = anthropic.Anthropic(api_key=api_key or Config.API_KEY)
    
    if not client.api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    prompt = build_conversion_prompt(kernel, reasoning_doc)
    
    print("Converting via API...")
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
    
    # Add version metadata
    content['_converter_metadata'] = {
        'converter_version': Config.CONVERTER_VERSION,
        'schema_version': Config.OUTPUT_SCHEMA_VERSION,
        'generated_at': datetime.now().isoformat(),
        'source_kernel_version': kernel.get('metadata', {}).get('kernel_version', 'unknown')
    }
    
    return content


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert kernel + reasoning doc to student-facing content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explicit paths
  python convert_kernel_to_content.py kernels/TKAM_kernel_v4_0.json kernels/TKAM_ReasoningDoc_v4_1.md
  
  # Auto-detect by title
  python convert_kernel_to_content.py --title "To Kill a Mockingbird"
  
  # Custom output
  python convert_kernel_to_content.py --title "The Giver" -o outputs/giver_content.json
"""
    )
    
    # Input options (either explicit paths OR title for auto-detect)
    parser.add_argument("kernel", nargs='?', help="Path to kernel JSON file")
    parser.add_argument("reasoning", nargs='?', help="Path to reasoning doc markdown file")
    parser.add_argument("--title", "-t", help="Text title (auto-detects kernel and reasoning doc)")
    parser.add_argument("--kernels-dir", help="Directory containing kernels", default="kernels")
    
    # Output options
    parser.add_argument("-o", "--output", help="Output JSON file path")
    
    # API options
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Resolve input files
    kernel_path = None
    reasoning_path = None
    
    if args.title:
        # Auto-detect mode
        kernels_dir = Path(args.kernels_dir)
        print(f"Auto-detecting files for: {args.title}")
        
        kernel_path = find_kernel_path(args.title, kernels_dir)
        reasoning_path = find_reasoning_doc_path(args.title, kernels_dir)
        
        if not kernel_path:
            print(f"❌ Could not find kernel for '{args.title}' in {kernels_dir}")
            sys.exit(1)
        if not reasoning_path:
            print(f"❌ Could not find reasoning doc for '{args.title}' in {kernels_dir}")
            sys.exit(1)
            
        print(f"  Found kernel: {kernel_path.name}")
        print(f"  Found reasoning: {reasoning_path.name}")
        
    elif args.kernel and args.reasoning:
        # Explicit paths mode
        kernel_path = Path(args.kernel)
        reasoning_path = Path(args.reasoning)
        
        if not kernel_path.exists():
            print(f"❌ Kernel file not found: {kernel_path}")
            sys.exit(1)
        if not reasoning_path.exists():
            print(f"❌ Reasoning doc not found: {reasoning_path}")
            sys.exit(1)
    else:
        parser.error("Provide either --title OR both kernel and reasoning paths")
    
    # Load inputs
    print(f"\nLoading kernel: {kernel_path}")
    kernel = load_kernel(kernel_path)
    
    print(f"Loading reasoning doc: {reasoning_path}")
    reasoning_doc = load_reasoning_doc(reasoning_path)
    
    # Get title for output naming
    title = kernel.get('metadata', {}).get('title', 'Unknown').strip()
    
    # Convert
    print()
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
    
    # Validate summary
    is_valid, errors = validate_output(content)
    if is_valid:
        print("✅ Output validation: PASSED")
    else:
        print(f"⚠️  Output validation: {len(errors)} warnings")
    
    return content


if __name__ == "__main__":
    main()
