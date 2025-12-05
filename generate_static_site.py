"""
Static Site Generator for Text Analysis Pages
Version: 0.2

Takes: folder of content JSON files
Outputs: folder of static HTML pages ready for deployment

Changes from v0.1:
- Added UTF-8 encoding to all file write operations
- Replaced emojis with HTML entities for better compatibility
- Added Netlify form handling to email capture form
- Added text title tracking in form submissions

Usage:
    python generate_static_site.py content/ dist/
"""

import json
import os
import argparse
from pathlib import Path


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Analysis | 5-Minute Literary Analysis</title>
    <meta name="description" content="Understand {title} by {author} in 5 minutes. Plain-language analysis with thesis, quotes, and essay evidence.">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }}
        .accordion-content.open {{ max-height: 2000px; }}
        .chevron {{ transition: transform 0.3s ease; }}
        .chevron.open {{ transform: rotate(180deg); }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="max-w-md mx-auto bg-white min-h-screen shadow-lg">
        
        <!-- Header -->
        <div class="p-5 border-b border-gray-100">
            <p class="text-gray-400 text-xs uppercase tracking-wide mb-1">5-Minute Analysis</p>
            <h1 class="text-xl font-bold text-gray-900">{title}</h1>
            <p class="text-gray-500 text-sm">{author}</p>
        </div>

        <!-- Layer 1: What's happening -->
        <div class="p-5 bg-blue-50">
            <p class="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-4">What's the story doing?</p>
            
            <div class="space-y-4">
                <div>
                    <p class="text-xs text-gray-500 mb-1">Who tells it?</p>
                    <p class="text-gray-800 text-sm">{who_tells_it}</p>
                </div>
                
                <div>
                    <p class="text-xs text-gray-500 mb-1">What do we experience?</p>
                    <p class="text-gray-800 text-sm">{what_we_experience}</p>
                </div>
                
                <div>
                    <p class="text-xs text-gray-500 mb-1">How does it feel?</p>
                    <p class="text-gray-800 text-sm">{how_it_feels}</p>
                </div>
            </div>
        </div>

        <!-- Layer 2: Meaning by section -->
        <div class="border-b border-gray-200">
            <button onclick="toggleAccordion('meaning')" class="w-full py-4 px-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors">
                <span class="font-semibold text-gray-800">What meaning is created?</span>
                <svg id="meaning-chevron" class="chevron w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="meaning-content" class="accordion-content px-5 text-gray-700">
                <div class="pb-5 divide-y divide-gray-100">
                    {sections_html}
                </div>
            </div>
        </div>

        <!-- Layer 3: Connections -->
        <div class="border-b border-gray-200">
            <button onclick="toggleAccordion('connections')" class="w-full py-4 px-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors">
                <span class="font-semibold text-gray-800">How the parts connect</span>
                <svg id="connections-chevron" class="chevron w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="connections-content" class="accordion-content px-5 text-gray-700">
                <div class="pb-5 space-y-4">
                    <div class="flex gap-3">
                        <div class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">1</div>
                        <p class="text-sm text-gray-700">{step_1}</p>
                    </div>
                    
                    <div class="flex gap-3">
                        <div class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">2</div>
                        <p class="text-sm text-gray-700">{step_2}</p>
                    </div>
                    
                    <div class="flex gap-3">
                        <div class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">3</div>
                        <p class="text-sm text-gray-700">{step_3}</p>
                    </div>

                    <div class="mt-4 pt-4 border-t border-gray-200">
                        <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">This pattern is called</p>
                        <p class="text-lg font-semibold text-blue-900">{pattern_name}</p>
                        <p class="text-sm text-gray-600 mt-1">{pattern_explanation}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Layer 4: Thesis -->
        <div class="p-5 border-b border-gray-200">
            <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Your thesis</p>
                <button onclick="copyThesis()" id="copy-btn" class="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1">
                    &#128203; Copy
                </button>
            </div>
            
            <!-- Thesis components -->
            <div class="space-y-2 mb-4">
                <div class="flex gap-2 text-xs">
                    <span class="text-gray-400 shrink-0 w-28">Who tells it &rarr;</span>
                    <span class="text-gray-600">{comp_who}</span>
                </div>
                <div class="flex gap-2 text-xs">
                    <span class="text-gray-400 shrink-0 w-28">What's revealed &rarr;</span>
                    <span class="text-gray-600">{comp_what}</span>
                </div>
                <div class="flex gap-2 text-xs">
                    <span class="text-gray-400 shrink-0 w-28">Story type &rarr;</span>
                    <span class="text-gray-600">{comp_story}</span>
                </div>
                <div class="flex gap-2 text-xs">
                    <span class="text-gray-400 shrink-0 w-28">Larger meaning &rarr;</span>
                    <span class="text-gray-600">{comp_meaning}</span>
                </div>
                <div class="flex gap-2 text-xs">
                    <span class="text-gray-400 shrink-0 w-28">Method &rarr;</span>
                    <span class="text-gray-600">{comp_method}</span>
                </div>
            </div>

            <!-- Combined thesis -->
            <div class="bg-gray-50 rounded-lg p-4">
                <p id="thesis-text" class="text-gray-800 text-sm leading-relaxed font-medium">{thesis_sentence}</p>
            </div>
        </div>

        <!-- Email capture -->
        <div class="p-5 bg-gray-50">
            <p class="font-semibold text-gray-800 mb-1">Want the full quote bank?</p>
            <p class="text-sm text-gray-600 mb-4">15+ quotes with analysis templates, organised by section.</p>
            <form class="flex gap-2" name="email-capture" method="POST" data-netlify="true" netlify-honeypot="bot-field">
                <input type="hidden" name="form-name" value="email-capture" />
                <input type="hidden" name="bot-field" />
                <input type="hidden" name="text-title" value="{title}" />
                <input
                    type="email"
                    name="email"
                    placeholder="Your email"
                    class="flex-1 px-4 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:border-blue-500"
                    required
                />
                <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
                    Get it
                </button>
            </form>
        </div>

        <!-- System C hook -->
        <div class="p-5 border-t border-gray-200">
            <a href="#workbook" class="block bg-blue-50 rounded-lg p-4 flex items-center justify-between hover:bg-blue-100 transition-colors">
                <div>
                    <p class="font-semibold text-blue-900 text-sm">Learn to write this yourself</p>
                    <p class="text-sm text-blue-600">{title} Essay Workbook &rarr;</p>
                </div>
                <span class="text-2xl">&#128216;</span>
            </a>
        </div>

        <!-- Footer -->
        <div class="p-5 text-center text-xs text-gray-400">
            <p>&copy; 2024 · <a href="/" class="hover:text-gray-600">More texts</a></p>
        </div>
    </div>

    <script>
        function toggleAccordion(id) {{
            const content = document.getElementById(id + '-content');
            const chevron = document.getElementById(id + '-chevron');
            content.classList.toggle('open');
            chevron.classList.toggle('open');
        }}

        function copyThesis() {{
            const thesis = document.getElementById('thesis-text').innerText;
            navigator.clipboard.writeText(thesis).then(() => {{
                const btn = document.getElementById('copy-btn');
                btn.innerHTML = '&#10003; Copied';
                setTimeout(() => {{ btn.innerHTML = '&#128203; Copy'; }}, 2000);
            }});
        }}
    </script>
</body>
</html>
'''

SECTION_TEMPLATE = '''
<div class="py-3">
    <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-bold text-blue-600 uppercase tracking-wide">{section}</span>
    </div>
    <p class="text-gray-800 text-sm font-medium mb-2">{meaning}</p>
    <p class="text-gray-600 text-sm italic mb-2">"{quote}" <span class="text-gray-400 text-xs">Ch. {chapter}</span></p>
    <p class="text-gray-500 text-xs">{devices}</p>
</div>
'''

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5-Minute Literary Analysis</title>
    <meta name="description" content="Understand VCE texts in 5 minutes. Plain-language analysis with thesis, quotes, and essay evidence.">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="max-w-md mx-auto bg-white min-h-screen shadow-lg">
        <div class="p-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-2">5-Minute Analysis</h1>
            <p class="text-gray-600 text-sm mb-6">Understand your VCE texts. Plain language. Usable thesis. Essay evidence.</p>
            
            <div class="space-y-3">
                {text_links}
            </div>
        </div>
        
        <div class="p-6 text-center text-xs text-gray-400">
            <p>&copy; 2024</p>
        </div>
    </div>
</body>
</html>
'''

TEXT_LINK_TEMPLATE = '''
<a href="{slug}.html" class="block p-4 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors">
    <p class="font-semibold text-gray-900">{title}</p>
    <p class="text-sm text-gray-500">{author}</p>
</a>
'''


def slugify(title: str) -> str:
    """Convert title to URL-safe slug."""
    return title.lower().replace(' ', '-').replace("'", '').replace('"', '').replace(':', '').replace('.', '')


def generate_sections_html(sections: list) -> str:
    """Generate HTML for all sections."""
    html_parts = []
    for section in sections:
        html_parts.append(SECTION_TEMPLATE.format(
            section=section['section'],
            meaning=section['meaning'],
            quote=section.get('quote', ''),
            chapter=section.get('quote_chapter', ''),
            devices=section.get('devices_supporting', '')
        ))
    return ''.join(html_parts)


def generate_page(content: dict) -> str:
    """Generate full HTML page from content JSON."""
    
    sections_html = generate_sections_html(content['layer_2_meaning_by_section'])
    
    return HTML_TEMPLATE.format(
        title=content['metadata']['title'],
        author=content['metadata']['author'],
        who_tells_it=content['layer_1_whats_happening']['who_tells_it'],
        what_we_experience=content['layer_1_whats_happening']['what_we_experience'],
        how_it_feels=content['layer_1_whats_happening']['how_it_feels'],
        sections_html=sections_html,
        step_1=content['layer_3_connections']['step_1'],
        step_2=content['layer_3_connections']['step_2'],
        step_3=content['layer_3_connections']['step_3'],
        pattern_name=content['layer_3_connections']['pattern_name'],
        pattern_explanation=content['layer_3_connections']['pattern_explanation'],
        comp_who=content['layer_4_thesis']['components']['who_tells_it'],
        comp_what=content['layer_4_thesis']['components']['what_they_reveal'],
        comp_story=content['layer_4_thesis']['components']['story_type'],
        comp_meaning=content['layer_4_thesis']['components']['larger_meaning'],
        comp_method=content['layer_4_thesis']['components']['method'],
        thesis_sentence=content['layer_4_thesis']['thesis_sentence']
    )


def generate_index(texts: list) -> str:
    """Generate index page listing all texts."""
    links = []
    for text in texts:
        links.append(TEXT_LINK_TEMPLATE.format(
            slug=text['slug'],
            title=text['title'],
            author=text['author']
        ))
    return INDEX_TEMPLATE.format(text_links=''.join(links))


def main():
    parser = argparse.ArgumentParser(description="Generate static HTML pages from content JSON files")
    parser.add_argument("input_dir", help="Directory containing content JSON files")
    parser.add_argument("output_dir", help="Directory for output HTML files")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Track all texts for index
    texts = []
    
    # Process each JSON file
    for json_file in input_path.glob('*.json'):
        print(f"Processing: {json_file.name}")
        
        with open(json_file, 'r') as f:
            content = json.load(f)
        
        # Generate slug from title
        slug = slugify(content['metadata']['title'])
        
        # Generate HTML
        html = generate_page(content)
        
        # Write output file
        output_file = output_path / f"{slug}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  → {output_file}")
        
        # Track for index
        texts.append({
            'slug': slug,
            'title': content['metadata']['title'],
            'author': content['metadata']['author']
        })
    
    # Generate index page
    index_html = generate_index(texts)
    index_file = output_path / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"  → {index_file}")
    
    print(f"\nDone! Generated {len(texts)} pages + index in {output_path}/")


if __name__ == "__main__":
    main()
