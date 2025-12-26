#!/usr/bin/env python3
"""
Generate Page
Converts kernel JSON to analysis HTML page via Claude API.

Usage:
    python scripts/generate_page.py kernels/Orbital_kernel_v6_1.json
    python scripts/generate_page.py kernels/  # Process all kernels in folder
"""

import os
import sys
import json
import re
from pathlib import Path
from anthropic import Anthropic

# =============================================================================
# CONFIGURATION
# =============================================================================

DIST_DIR = Path('./dist')
BASE_URL = 'https://luminait.app'

client = Anthropic()

# =============================================================================
# REWRITING METHOD (from REWRITING_METHOD_v1_0.md)
# =============================================================================

REWRITING_METHOD = """
## Rewriting Method: Kernel to Student-Facing Page

Transform academic kernel content into student-facing analysis pages (Year 10-12 audience). Same intellectual content, accessible structure.

### Five Rules

**Rule 1: Ground in Story First**
- Lead with what happens in the book
- First paragraph must mention characters, setting, or plot
- Don't lead with pattern/technique

**Rule 2: Retain Vocabulary, Unpack Structure**
- Keep academic terms: omniscient, juxtaposition, contemplative, motif, imagery, symbolism, free indirect discourse, lyrical prose, meditative, elegiac, paradox
- Break compound sentences into stages
- One idea per sentence
- Use em-dashes for definitions

**Rule 3: Make Connections Explicit**
- Show technique → effect
- Use connectors: "This creates...", "The effect:", "The result:", "Notice what's next to what:", "This matters because..."

**Rule 4: Add Scaffolding**
- Include "Ask yourself:" boxes after major sections
- Use bullet breakdowns for complex concepts
- Add "Why [term]?" explanations

**Rule 5: Short Paragraphs**
- 2-3 sentences maximum per paragraph
- Line breaks between ideas

### Page Structure

1. **What the Novel Does** — plot/story grounding (from narrative mode, setting)
2. **The Central Pattern** — pattern name + unpacked explanation (from alignment_pattern)
3. **Key Techniques** — 3-4 device examples with quotes (from micro_devices)
4. **Structure** — how the book is organized (from macro_variables.narrative.structure)
5. **Themes** — connected back to pattern (derived from pattern + reader_effect)

### Device Block Format

For each device:
- Device name as heading
- Quote in italics
- Bullet breakdown of what's in the quote
- Effect statement explaining what this creates for the reader

### Scaffolding Block Format

- "Ask yourself: [Question]"
- 2-3 sentence answer modeling the thinking
- Place after: central pattern intro, each major section, themes-to-pattern connection
"""

# =============================================================================
# HTML TEMPLATE
# =============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {seo_tags}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.7;
            color: #333;
            max-width: 720px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
        }}
        
        header {{
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: normal;
            margin-bottom: 8px;
        }}
        
        .author {{
            color: #666;
            font-style: italic;
        }}
        
        .section {{
            margin-bottom: 48px;
        }}
        
        h2 {{
            font-size: 1.4rem;
            font-weight: normal;
            border-bottom: 1px solid #ccc;
            padding-bottom: 8px;
            margin-bottom: 20px;
        }}
        
        p {{
            margin-bottom: 16px;
        }}
        
        .scaffold {{
            background: #f5f5f5;
            padding: 16px;
            margin: 20px 0;
            border-left: 3px solid #888;
        }}
        
        .scaffold-question {{
            font-weight: bold;
            color: #555;
            margin-bottom: 8px;
        }}
        
        .concept-list {{
            margin: 16px 0;
            padding-left: 20px;
        }}
        
        .concept-list li {{
            margin-bottom: 8px;
        }}
        
        .device {{
            background: #fff;
            border-left: 3px solid #666;
            padding: 20px;
            margin: 24px 0;
        }}
        
        .device-name {{
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 12px;
        }}
        
        .quote {{
            font-style: italic;
            color: #555;
            margin-bottom: 12px;
            padding-left: 16px;
            border-left: 2px solid #ddd;
        }}
        
        .metadata {{
            font-size: 0.85rem;
            color: #888;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    {content}
    
    <footer class="metadata">
        <p>Analysis generated from {title} kernel v{kernel_version} • Rewriting method: v1.0</p>
    </footer>
</body>
</html>'''

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def slugify(text):
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def extract_kernel_data(kernel):
    """Extract relevant data from kernel JSON."""
    metadata = kernel.get('metadata', {})
    pattern = kernel.get('alignment_pattern', {})
    macro = kernel.get('macro_variables', {})
    devices = kernel.get('micro_devices', [])
    
    # Select best devices
    selected_devices = select_devices(devices, 4)
    
    return {
        'title': metadata.get('title', 'Unknown'),
        'author': metadata.get('author', 'Unknown'),
        'kernel_version': metadata.get('kernel_version', '6.0'),
        'pattern_name': pattern.get('pattern_name', 'Unknown Pattern'),
        'core_dynamic': pattern.get('core_dynamic', ''),
        'reader_effect': pattern.get('reader_effect', ''),
        'device_priorities': pattern.get('device_priorities', []),
        'narrative': macro.get('narrative', {}),
        'rhetoric': macro.get('rhetoric', {}),
        'device_mediation': macro.get('device_mediation', {}).get('summary', ''),
        'devices': selected_devices
    }


def select_devices(devices, count):
    """Select best devices for variety."""
    # Filter to verified quotes only
    verified = [d for d in devices if d.get('quote_verified') == True]
    
    # Prefer variety: different device types, different sections
    selected = []
    used_types = set()
    used_sections = set()
    
    # First pass: one of each type from different sections
    for device in verified:
        if len(selected) >= count:
            break
        if device['name'] not in used_types and device.get('assigned_section') not in used_sections:
            selected.append(device)
            used_types.add(device['name'])
            used_sections.add(device.get('assigned_section'))
    
    # Second pass: fill remaining slots
    for device in verified:
        if len(selected) >= count:
            break
        if device not in selected:
            selected.append(device)
    
    return selected


def generate_seo_tags(data, slug):
    """Generate SEO meta tags."""
    description = data['core_dynamic'][:155]
    if len(data['core_dynamic']) > 155:
        description += '...'
    
    # Escape quotes for HTML attributes
    description = description.replace('"', '&quot;')
    
    return f'''<title>{data['title']} by {data['author']} — Analysis</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{data['title']} by {data['author']} — Analysis">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <link rel="canonical" href="{BASE_URL}/{slug}/">'''


# =============================================================================
# CLAUDE API CALL
# =============================================================================

def generate_content(kernel_data):
    """Call Claude API to generate page content."""
    
    # Format devices for prompt
    devices_text = ""
    for i, d in enumerate(kernel_data['devices'], 1):
        devices_text += f"""
{i}. **{d['name']}**
   Quote: "{d['anchor_phrase']}"
   Effect: {d['effect']}
   Section: {d.get('assigned_section', 'unknown')}
"""
    
    # Get narrative info
    narrative = kernel_data['narrative']
    rhetoric = kernel_data['rhetoric']
    
    prompt = f"""
You are generating the main content (inside <body>) for an HTML analysis page.

{REWRITING_METHOD}

## Kernel Data

**Title:** {kernel_data['title']}
**Author:** {kernel_data['author']}

**Pattern Name:** {kernel_data['pattern_name']}
**Core Dynamic:** {kernel_data['core_dynamic']}
**Reader Effect:** {kernel_data['reader_effect']}

**Narrative Voice:**
- POV: {narrative.get('voice', {}).get('pov_description', 'Not specified')}
- Tone: {rhetoric.get('voice', {}).get('tone', 'Not specified')}

**Narrative Structure:**
- Chronology: {narrative.get('structure', {}).get('chronology', 'Not specified')}
- Plot Architecture: {narrative.get('structure', {}).get('plot_architecture_description', 'Not specified')}
- Beginning: {narrative.get('structure', {}).get('beginning_type', 'Not specified')}
- Ending: {narrative.get('structure', {}).get('ending_type', 'Not specified')}

**Device Mediation:** {kernel_data['device_mediation']}

**Selected Devices (use these exact quotes):**
{devices_text}

## Output Format

Generate ONLY the content that goes inside <body>, structured as:

<header>
    <h1>{kernel_data['title']}</h1>
    <p class="author">by {kernel_data['author']}</p>
</header>

<main>
    <section class="section">
        <h2>What the Novel Does</h2>
        [Story-grounded introduction - what happens, who's in it, how it's told]
        [Include scaffold box]
    </section>
    
    <section class="section">
        <h2>The Central Pattern: {kernel_data['pattern_name']}</h2>
        [Pattern explanation - unpacked, with bullet list of components]
        [Include scaffold box explaining "why this name"]
    </section>
    
    <section class="section">
        <h2>Key Techniques</h2>
        [3-4 device blocks using the exact quotes provided]
        [Each device: name, quote, bullet breakdown, effect]
    </section>
    
    <section class="section">
        <h2>Structure</h2>
        [How the book is organized - connect structure to meaning]
    </section>
    
    <section class="section">
        <h2>Themes</h2>
        [2-3 themes, each a short paragraph]
        [Final scaffold box connecting themes to pattern]
    </section>
</main>

Use these CSS classes:
- .section for each section
- .scaffold for "Ask yourself" boxes (.scaffold-question for the question)
- .concept-list for bullet lists
- .device for device blocks (.device-name, .quote)

Output ONLY the HTML content. No explanation, no markdown, no code blocks.
"""

    message = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=8000,
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )
    
    return message.content[0].text


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def generate_page(kernel_path):
    """Generate HTML page from kernel JSON."""
    kernel_path = Path(kernel_path)
    print(f'Processing: {kernel_path}')
    
    # Read kernel
    with open(kernel_path, 'r', encoding='utf-8') as f:
        kernel = json.load(f)
    
    # Extract data
    kernel_data = extract_kernel_data(kernel)
    print(f'  Title: {kernel_data["title"]}')
    print(f'  Pattern: {kernel_data["pattern_name"]}')
    print(f'  Devices: {len(kernel_data["devices"])} selected')
    
    # Generate slug
    slug = slugify(kernel_data['title'])
    print(f'  Slug: {slug}')
    
    # Generate content via Claude
    print('  Calling Claude API...')
    content = generate_content(kernel_data)
    
    # Clean content (remove markdown code blocks if present)
    content = re.sub(r'^```html?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    
    # Fix encoding issues
    content = content.encode('utf-8').decode('utf-8')
    
    # Generate SEO tags
    seo_tags = generate_seo_tags(kernel_data, slug)
    
    # Assemble HTML
    html = HTML_TEMPLATE.format(
        seo_tags=seo_tags,
        content=content,
        title=kernel_data['title'],
        kernel_version=kernel_data['kernel_version']
    )
    
    # Create directory
    output_dir = DIST_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f'  Created: {output_dir}')
    
    # Write file
    output_path = output_dir / 'index.html'
    with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(html)
    print(f'  Written: {output_path}')
    
    return {'slug': slug, 'output_path': str(output_path)}


def main():
    if len(sys.argv) < 2:
        print('Usage: python generate_page.py <kernel.json> [kernel2.json ...]')
        print('       python generate_page.py kernels/')
        sys.exit(1)
    
    paths = []
    
    for arg in sys.argv[1:]:
        arg_path = Path(arg)
        if arg_path.is_dir():
            # Process all JSON files in directory
            paths.extend(arg_path.glob('*.json'))
        else:
            paths.append(arg_path)
    
    print(f'Found {len(paths)} kernel(s) to process\n')
    
    for kernel_path in paths:
        try:
            generate_page(kernel_path)
            print('  ✓ Done\n')
        except Exception as e:
            print(f'  ✗ Error: {e}\n')
    
    print('Run "python scripts/build_all.py" to update homepage and sitemap')


if __name__ == '__main__':
    main()

