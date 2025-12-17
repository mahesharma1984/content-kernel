# phase_2/stage_5b_refine.py

import json
import os
import sys
from anthropic import Anthropic

# Channel definitions - embedded, not external
CHANNEL_DEFINITIONS = {
    "social": {
        "platform": "TikTok/Reels/Shorts",
        "format": "60-90 second vertical video script",
        "register": "emotional_provocative",
        "output_structure": "[HOOK - 3 sec] [VISUAL] [SPOKEN] [CLIFFHANGER] [CTA]",
        "must_include": [
            "Visual direction in brackets",
            "Spoken text clearly marked", 
            "Hook in first 3 seconds",
            "Cliffhanger ending"
        ],
        "must_not_include": [
            "Educational explanation",
            "Pattern names or jargon",
            "Satisfied curiosity"
        ]
    },
    "youtube": {
        "platform": "YouTube",
        "format": "5-10 minute video script (opening section)",
        "register": "educational_demonstration",
        "output_structure": "[HOOK] [PROMISE] [PREVIEW] [PAYOFF]",
        "must_include": [
            "Specific scene examples",
            "Pattern name revealed",
            "CTA to guide"
        ],
        "must_not_include": [
            "Complete framework",
            "Application to other works"
        ]
    },
    "seo": {
        "platform": "Web/Blog",
        "format": "1500-2000 word article (headline + opening)",
        "register": "analytical",
        "output_structure": "**Headline**\\n\\nOpening paragraph...",
        "must_include": [
            "SEO-friendly headline",
            "Search intent answered",
            "CTA to guide"
        ],
        "must_not_include": [
            "Complete pattern",
            "Application beyond this text"
        ]
    },
    "guide": {
        "platform": "PDF download",
        "format": "15-20 page guide (intro + structure)",
        "register": "systematic_comprehensive",
        "output_structure": "**Title**\\n\\n**Introduction:**\\n...\\n\\n**Structure:**\\n1. ...",
        "must_include": [
            "Complete framework",
            "Application to other works",
            "Practical tools"
        ],
        "must_not_include": [
            "CTA (this is the deliverable)",
            "Repetition from other channels"
        ]
    }
}

def build_channel_prompt_section():
    """Build channel format requirements for prompt."""
    sections = []
    for channel, defn in CHANNEL_DEFINITIONS.items():
        section = f"""
### {channel.upper()}
- Platform: {defn['platform']}
- Format: {defn['format']}
- Register: {defn['register']}
- Output structure: {defn['output_structure']}
- Must include: {', '.join(defn['must_include'])}
- Must NOT include: {', '.join(defn['must_not_include'])}
"""
        sections.append(section)
    return "\n".join(sections)

def validate_channel_format(channel, content):
    """Validate content matches expected format."""
    defn = CHANNEL_DEFINITIONS.get(channel.lower(), {})
    issues = []
    
    if channel.lower() == 'social':
        # Must have video script markers
        required_markers = ['[HOOK', '[VISUAL', '[SPOKEN', '[CTA']
        has_markers = any(marker in content.upper() for marker in ['[HOOK', '[VISUAL', 'SPOKEN]', '[CTA'])
        
        if not has_markers:
            issues.append(f"Social content missing video script markers. Got caption instead of script.")
        
        # Should NOT look like a tweet/caption
        if content.count('\n') < 3 and len(content) < 300:
            issues.append(f"Social content looks like caption ({len(content)} chars, {content.count(chr(10))} lines). Should be video script.")
    
    elif channel.lower() == 'youtube':
        if '[HOOK]' not in content and '[hook]' not in content.lower():
            issues.append("YouTube missing [HOOK] marker")
    
    return issues

def load_prompt_template(path):
    with open(path, 'r') as f:
        return f.read()

def escape_json_for_format(json_str):
    """Escape braces in JSON string so it can be safely used in .format()"""
    return json_str.replace('{', '{{').replace('}', '}}')

def get_channel_format(channel):
    """Return expected format for channel."""
    formats = {
        "social": "60-90 second vertical video script",
        "youtube": "5-10 minute video script (opening)",
        "seo": "1500-2000 word article (headline + opening)",
        "guide": "15-20 page document (intro + structure)"
    }
    return formats.get(channel, "unknown")

def validate_format(channel, content):
    """Check if content matches expected format."""
    if channel == "social":
        # Must have video script markers
        markers = ['[hook', '[visual', '[spoken', '[cta', '[cliffhanger']
        has_markers = sum(1 for m in markers if m in content.lower())
        return has_markers >= 3
    
    elif channel == "youtube":
        markers = ['[hook]', '[promise]', '[preview]', '[payoff]']
        has_markers = sum(1 for m in markers if m in content.lower())
        return has_markers >= 2
    
    elif channel == "seo":
        # Should have headline (bold or ##)
        return '**' in content or content.startswith('#')
    
    elif channel == "guide":
        # Should have structure
        return 'structure' in content.lower() or '1.' in content
    
    return True

def parse_markdown_to_json(markdown_text, book_title):
    """Parse Stage 5B markdown output into JSON structure."""
    import re
    
    result = {
        "stage": "5B",
        "book_title": book_title,
        "content_blocks": {},
        "overall_validation": {
            "all_constraints_met": True,
            "issues_found": [],
            "ready_for_rendering": True
        }
    }
    
    # Split by channel headers
    # Handles: ## SOCIAL, ## YOUTUBE, ## SEO, ## GUIDE (with optional parentheticals)
    # Pattern matches: ## CHANNEL (optional text) followed by content until next ## or end
    channel_pattern = r'##\s*(SOCIAL|YOUTUBE|SEO|GUIDE)(?:[^\n]*)?\n(.*?)(?=\n##\s*(?:SOCIAL|YOUTUBE|SEO|GUIDE)|\Z)'
    matches = re.findall(channel_pattern, markdown_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    
    for channel_name, content in matches:
        channel_key = channel_name.lower()
        content = content.strip()
        
        # Remove trailing separators (---, --, or multiple newlines)
        content = re.sub(r'\n-{2,}\s*$', '', content).strip()
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        
        result["content_blocks"][channel_key] = {
            "final_content": content,
            "format": get_channel_format(channel_key),
            "constraint_validation": {
                "job_accomplished": True,
                "format_correct": validate_format(channel_key, content)
            }
        }
    
    return result

def refine_with_constraints(starting_path, channels_path, thread_path, prompt_path, output_path):
    """Apply Stage 5B refinement."""
    
    # Load inputs
    with open(starting_path, 'r') as f:
        starting = json.load(f)
    
    with open(channels_path, 'r') as f:
        channels = json.load(f)
    
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    template = load_prompt_template(prompt_path)
    
    # Extract drafts
    drafts = starting.get('starting_drafts', {})
    
    # Helper to get channel data with case-insensitive lookup
    def get_channel_data(channel_key):
        for k, v in channels.items():
            if k.lower() == channel_key.lower():
                return v
        return {}
    
    def get_draft(channel_key):
        for k, v in drafts.items():
            if k.lower() == channel_key.lower():
                return v
        return {}
    
    # Prepare prompt
    social_channel = get_channel_data('social')
    youtube_channel = get_channel_data('youtube')
    seo_channel = get_channel_data('seo')
    guide_channel = get_channel_data('guide')
    
    social_draft_data = get_draft('social')
    youtube_draft_data = get_draft('youtube')
    seo_draft_data = get_draft('seo')
    guide_draft_data = get_draft('guide')
    
    # Build channel format requirements
    channel_formats = build_channel_prompt_section()
    
    # Build base prompt from template using string replacement to avoid brace escaping issues
    base_prompt = template
    base_prompt = base_prompt.replace('{core_message}', thread['core_message'])
    base_prompt = base_prompt.replace('{agitation_register}', thread['agitation_register'])
    base_prompt = base_prompt.replace('{solution_register}', thread['solution_register'])
    base_prompt = base_prompt.replace('{starting_drafts_json}', json.dumps(drafts, indent=2))
    base_prompt = base_prompt.replace('{channel_strategy_json}', json.dumps(channels, indent=2))
    base_prompt = base_prompt.replace('{social_draft}', json.dumps(social_draft_data, indent=2))
    base_prompt = base_prompt.replace('{social_job}', social_channel.get('job', 'Not defined'))
    base_prompt = base_prompt.replace('{social_must_do}', json.dumps(social_channel.get('must_do', [])))
    base_prompt = base_prompt.replace('{social_must_not_do}', json.dumps(social_channel.get('must_not_do', [])))
    base_prompt = base_prompt.replace('{youtube_draft}', json.dumps(youtube_draft_data, indent=2))
    base_prompt = base_prompt.replace('{youtube_job}', youtube_channel.get('job', 'Not defined'))
    base_prompt = base_prompt.replace('{youtube_must_do}', json.dumps(youtube_channel.get('must_do', [])))
    base_prompt = base_prompt.replace('{youtube_must_not_do}', json.dumps(youtube_channel.get('must_not_do', [])))
    base_prompt = base_prompt.replace('{seo_draft}', json.dumps(seo_draft_data, indent=2))
    base_prompt = base_prompt.replace('{seo_job}', seo_channel.get('job', 'Not defined'))
    base_prompt = base_prompt.replace('{seo_must_do}', json.dumps(seo_channel.get('must_do', [])))
    base_prompt = base_prompt.replace('{seo_must_not_do}', json.dumps(seo_channel.get('must_not_do', [])))
    base_prompt = base_prompt.replace('{guide_draft}', json.dumps(guide_draft_data, indent=2))
    base_prompt = base_prompt.replace('{guide_job}', guide_channel.get('job', 'Not defined'))
    base_prompt = base_prompt.replace('{guide_must_do}', json.dumps(guide_channel.get('must_do', [])))
    base_prompt = base_prompt.replace('{guide_must_not_do}', json.dumps(guide_channel.get('must_not_do', [])))
    
    # Add channel format requirements to prompt
    prompt = base_prompt + """

## CRITICAL: Channel Format Requirements

Each channel has a specific format. Your output MUST match these exactly:

""" + channel_formats + """

## Social Output Example (REQUIRED FORMAT)

```
[HOOK - 3 seconds]
[Visual: Text on screen] "TKAM feels different..."
[Spoken] "But you've never been able to say WHY."

[VISUAL: Confused student looking at book]
[Spoken] "There's a specific structural reason."

[CLIFFHANGER]
[Spoken] "I break down the exact mechanism..."
[Visual: Arrow pointing down]

[CTA: implied - curiosity drives to YouTube]
```

NOT this (wrong - this is a caption):
```
You know TKAM feels different from other memory books—but you can't put your finger on why. There's a specific structural reason Scout's narration creates that unique reading experience. I break down the exact mechanism in my latest video 👇
```

"""
    
    # Call API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Refining content with constraints...")
    print("(This may take 60-90 seconds)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        # Extract book title from file path or use default
        book_title = "To Kill a Mockingbird"  # Default
        if "TKAM" in starting_path.upper():
            book_title = "To Kill a Mockingbird"
        elif "jane_eyre" in starting_path.lower():
            book_title = "Jane Eyre"
        # Add more book title mappings as needed
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save markdown output (human readable)
        md_output_path = output_path.replace('.json', '.md')
        with open(md_output_path, 'w') as f:
            f.write(f"# {book_title} - Stage 5B Content\n\n")
            f.write(response_text)
        print(f"✓ Markdown saved: {md_output_path}")
        
        # Parse markdown to JSON (programmatic use)
        try:
            result = parse_markdown_to_json(response_text, book_title)
            
            # Validate format
            issues = []
            for channel, block in result["content_blocks"].items():
                final_content = block.get("final_content", "")
                if final_content:
                    # Use existing validate_channel_format for detailed checks
                    format_issues = validate_channel_format(channel, final_content)
                    if format_issues:
                        issues.extend([f"{channel}: {issue}" for issue in format_issues])
                    
                    # Also check format_correct flag
                    if not block.get("constraint_validation", {}).get("format_correct", True):
                        issues.append(f"{channel}: format validation failed")
            
            if issues:
                result["overall_validation"]["issues_found"] = issues
                result["overall_validation"]["all_constraints_met"] = False
                print(f"\nWARNING: Format issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                result["overall_validation"]["all_constraints_met"] = True
                result["overall_validation"]["ready_for_rendering"] = True
            
            # Save JSON output
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✓ JSON saved: {output_path}")
            
            # Quick validation summary
            overall = result.get('overall_validation', {})
            print(f"\nAll constraints met: {overall.get('all_constraints_met', 'Unknown')}")
            print(f"Ready for rendering: {overall.get('ready_for_rendering', 'Unknown')}")
            
            if overall.get('issues_found'):
                print(f"Issues: {overall['issues_found']}")
            
            return result
            
        except Exception as e:
            print(f"ERROR parsing markdown: {e}")
            import traceback
            traceback.print_exc()
            # Still save raw for manual recovery
            raw_path = output_path.replace('.json', '.raw')
            with open(raw_path, 'w') as f:
                f.write(response_text)
            print(f"Raw response saved to: {raw_path}")
            return None
            
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        print("Check:")
        print("  1. ANTHROPIC_API_KEY is set")
        print("  2. Prompt length < 100k tokens")
        print("  3. Internet connection working")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    starting_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_starting_drafts.json"
    channels_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    thread_path = sys.argv[3] if len(sys.argv) > 3 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    prompt_path = sys.argv[4] if len(sys.argv) > 4 else "prompts/phase_2/stage_5b_constrained.txt"
    output_path = sys.argv[5] if len(sys.argv) > 5 else "outputs/manual_exploration/phase_2/TKAM_stage_5b_content.json"
    
    refine_with_constraints(starting_path, channels_path, thread_path, prompt_path, output_path)

