"""
Static Site Generator for Text Analysis Pages
Version: 0.6

Takes: folder of content JSON files
Outputs: folder of static HTML pages ready for deployment

Changes from v0.5:
- Increased Freytag arc SVG text from 7px to 11px for legibility
- Enlarged Freytag arc overall (height 70 → 95)

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
    <title>{title} Analysis | LumintAIT Literary Analysis</title>
    <meta name="description" content="{title} analysis for VCE and IB English. Systematic breakdown with thesis, quotes, and essay evidence. Understand how the text creates meaning.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        cream: '#FAF9F6',
                        ink: '#1a1a1a',
                        inkLight: '#4a4a4a',
                        inkMuted: '#767676',
                        accent: '#9f1239',
                        accentLight: '#fff1f2',
                        rule: '#E8E4E0',
                    }},
                    fontFamily: {{
                        serif: ['Playfair Display', 'Georgia', 'serif'],
                        sans: ['Source Sans 3', 'system-ui', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ -webkit-font-smoothing: antialiased; }}
        .accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }}
        .accordion-content.open {{ max-height: 3000px; }}
        .chevron {{ transition: transform 0.3s ease; }}
        .chevron.open {{ transform: rotate(180deg); }}
    </style>
</head>
<body class="bg-cream min-h-screen font-sans text-ink">
    <div class="max-w-lg mx-auto bg-white min-h-screen shadow-sm border-x border-rule">
        
        <!-- Header -->
        <header class="px-6 pt-8 pb-6 border-b border-rule">
            <a href="/" class="text-xs tracking-widest text-inkMuted uppercase hover:text-accent transition-colors">&larr; LumintAIT</a>
            <h1 class="font-serif text-2xl font-semibold text-ink leading-tight mt-4 mb-1">{title}</h1>
            <p class="text-inkMuted">{author}</p>
        </header>

        <!-- Layer 1: Three Pillars -->
        <section class="px-6 py-8 border-b border-rule bg-accentLight/30">
            <p class="text-xs tracking-widest text-accent uppercase mb-6">What's the story doing?</p>
            
            <div class="space-y-6 sm:space-y-0 sm:grid sm:grid-cols-3 sm:gap-4 sm:text-center">
                <div class="flex sm:block items-start sm:items-center gap-4 sm:gap-0">
                    <div class="w-10 h-10 shrink-0 sm:mx-auto mb-0 sm:mb-3 rounded-full bg-accentLight flex items-center justify-center">
                        <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-xs text-inkMuted uppercase tracking-wide mb-1 sm:mb-2">Who tells it</p>
                        <p class="text-sm text-ink leading-relaxed">{who_tells_it}</p>
                    </div>
                </div>
                
                <div class="flex sm:block items-start sm:items-center gap-4 sm:gap-0">
                    <div class="w-10 h-10 shrink-0 sm:mx-auto mb-0 sm:mb-3 rounded-full bg-accentLight flex items-center justify-center">
                        <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-xs text-inkMuted uppercase tracking-wide mb-1 sm:mb-2">What we experience</p>
                        <p class="text-sm text-ink leading-relaxed">{what_we_experience}</p>
                    </div>
                </div>
                
                <div class="flex sm:block items-start sm:items-center gap-4 sm:gap-0">
                    <div class="w-10 h-10 shrink-0 sm:mx-auto mb-0 sm:mb-3 rounded-full bg-accentLight flex items-center justify-center">
                        <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-xs text-inkMuted uppercase tracking-wide mb-1 sm:mb-2">How it feels</p>
                        <p class="text-sm text-ink leading-relaxed">{how_it_feels}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Layer 2: Meaning with Freytag Arc -->
        <div class="border-b border-rule">
            <button onclick="toggleAccordion('meaning')" class="w-full py-5 px-6 flex items-center justify-between text-left hover:bg-cream/50 transition-colors">
                <span class="font-serif text-lg font-medium text-ink">What meaning is created?</span>
                <svg id="meaning-chevron" class="chevron w-5 h-5 text-inkMuted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="meaning-content" class="accordion-content px-6 text-ink">
                <div class="pb-6">
                    <!-- Freytag Arc -->
                    <div class="mb-6 flex justify-center">
                        <svg width="320" height="95" viewBox="0 0 320 95" class="text-accent">
                            <path d="M25 75 Q85 68 125 45 Q160 18 160 18 Q160 18 195 45 Q235 68 295 75" stroke="currentColor" stroke-width="2" fill="none"/>
                            <circle cx="45" cy="72" r="5" fill="currentColor" opacity="0.5"/>
                            <circle cx="105" cy="52" r="5" fill="currentColor" opacity="0.5"/>
                            <circle cx="160" cy="18" r="6" fill="currentColor"/>
                            <circle cx="215" cy="52" r="5" fill="currentColor" opacity="0.5"/>
                            <circle cx="275" cy="72" r="5" fill="currentColor" opacity="0.5"/>
                            <text x="45" y="90" text-anchor="middle" font-size="11" fill="#767676" text-transform="uppercase">Expo</text>
                            <text x="105" y="68" text-anchor="middle" font-size="11" fill="#767676" text-transform="uppercase">Rising</text>
                            <text x="160" y="10" text-anchor="middle" font-size="11" fill="#9f1239" font-weight="600" text-transform="uppercase">Climax</text>
                            <text x="215" y="68" text-anchor="middle" font-size="11" fill="#767676" text-transform="uppercase">Falling</text>
                            <text x="275" y="90" text-anchor="middle" font-size="11" fill="#767676" text-transform="uppercase">Reso</text>
                        </svg>
                    </div>
                    
                    <div class="space-y-3">
                        {sections_html}
                    </div>
                </div>
            </div>
        </div>

        <!-- How it's achieved: Devices -->
        <div class="border-b border-rule">
            <button onclick="toggleAccordion('devices')" class="w-full py-5 px-6 flex items-center justify-between text-left hover:bg-cream/50 transition-colors">
                <span class="font-serif text-lg font-medium text-ink">How it's achieved</span>
                <svg id="devices-chevron" class="chevron w-5 h-5 text-inkMuted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="devices-content" class="accordion-content px-6 text-ink">
                <div class="pb-6 space-y-3">
                    {devices_html}
                </div>
            </div>
        </div>

        <!-- Layer 3: Connections - Convergence -->
        <div class="border-b border-rule">
            <button onclick="toggleAccordion('connections')" class="w-full py-5 px-6 flex items-center justify-between text-left hover:bg-cream/50 transition-colors">
                <span class="font-serif text-lg font-medium text-ink">How the parts connect</span>
                <svg id="connections-chevron" class="chevron w-5 h-5 text-inkMuted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="connections-content" class="accordion-content px-6 text-ink">
                <div class="pb-6">
                    <!-- Two inputs -->
                    <div class="grid grid-cols-2 gap-3 mb-2">
                        <div class="bg-cream rounded p-4 border-l-2 border-accent">
                            <p class="text-xs tracking-wide text-accent uppercase mb-2">Narration</p>
                            <p class="text-sm text-inkLight leading-relaxed">{step_1}</p>
                        </div>
                        <div class="bg-cream rounded p-4 border-l-2 border-accent">
                            <p class="text-xs tracking-wide text-accent uppercase mb-2">Devices</p>
                            <p class="text-sm text-inkLight leading-relaxed">{step_2}</p>
                        </div>
                    </div>
                    
                    <!-- Convergence arrow -->
                    <div class="flex justify-center my-1">
                        <svg width="120" height="36" viewBox="0 0 120 36" fill="none">
                            <path d="M30 0 L30 12 Q30 22 45 26 L55 28" stroke="#9f1239" stroke-width="1.5" fill="none"/>
                            <path d="M90 0 L90 12 Q90 22 75 26 L65 28" stroke="#9f1239" stroke-width="1.5" fill="none"/>
                            <path d="M60 24 L60 34" stroke="#9f1239" stroke-width="1.5" fill="none"/>
                            <path d="M55 29 L60 36 L65 29" stroke="#9f1239" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    
                    <!-- Synthesis -->
                    <div class="bg-accentLight rounded p-5 border border-accent/20">
                        <p class="text-xs tracking-wide text-accent uppercase mb-2">Together</p>
                        <p class="text-ink leading-relaxed">{step_3}</p>
                    </div>
                    
                    <!-- Pattern -->
                    <div class="mt-6 pt-5 border-t border-rule">
                        <p class="text-xs text-inkMuted uppercase tracking-wide mb-1">This pattern is called</p>
                        <p class="font-serif text-xl font-medium text-ink">{pattern_name}</p>
                        <p class="text-inkLight leading-relaxed mt-2">{pattern_explanation}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Layer 4: Thesis - Component Assembly -->
        <section class="px-6 py-8 border-b border-rule">
            <div class="flex items-center justify-between mb-5">
                <p class="text-xs tracking-widest text-inkMuted uppercase">Your thesis</p>
                <button onclick="copyThesis()" id="copy-btn" class="text-xs text-accent hover:text-ink transition-colors flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy
                </button>
            </div>
            
            <!-- Component stack -->
            <div class="space-y-1 mb-3">
                <div class="flex items-center gap-3 p-2 bg-cream rounded border-l-2 border-inkMuted">
                    <span class="text-xs text-inkMuted w-24 shrink-0">Who tells it</span>
                    <span class="text-sm text-inkLight">{comp_who}</span>
                </div>
                <div class="flex items-center gap-3 p-2 bg-cream rounded border-l-2 border-inkMuted">
                    <span class="text-xs text-inkMuted w-24 shrink-0">What's revealed</span>
                    <span class="text-sm text-inkLight">{comp_what}</span>
                </div>
                <div class="flex items-center gap-3 p-2 bg-cream rounded border-l-2 border-inkMuted">
                    <span class="text-xs text-inkMuted w-24 shrink-0">Story type</span>
                    <span class="text-sm text-inkLight">{comp_story}</span>
                </div>
                <div class="flex items-center gap-3 p-2 bg-cream rounded border-l-2 border-inkMuted">
                    <span class="text-xs text-inkMuted w-24 shrink-0">Larger meaning</span>
                    <span class="text-sm text-inkLight">{comp_meaning}</span>
                </div>
                <div class="flex items-center gap-3 p-2 bg-cream rounded border-l-2 border-inkMuted">
                    <span class="text-xs text-inkMuted w-24 shrink-0">Method</span>
                    <span class="text-sm text-inkLight">{comp_method}</span>
                </div>
            </div>
            
            <!-- Assembly arrow -->
            <div class="flex justify-center my-3">
                <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
                    <path d="M20 0 L20 18" stroke="#9f1239" stroke-width="1.5"/>
                    <path d="M14 14 L20 22 L26 14" stroke="#9f1239" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
                </svg>
            </div>

            <!-- Combined thesis -->
            <div class="bg-accentLight rounded p-5 border-l-2 border-accent">
                <p id="thesis-text" class="text-ink leading-relaxed">{thesis_sentence}</p>
            </div>
        </section>

        <!-- Email capture -->
        <section class="px-6 py-8 bg-cream/50">
            <p class="font-serif text-lg font-medium text-ink mb-2">Want the full quote bank?</p>
            <p class="text-inkMuted mb-5">15+ quotes with analysis templates, organised by section.</p>
            <form class="flex gap-3" name="email-capture" method="POST" data-netlify="true" netlify-honeypot="bot-field">
                <input type="hidden" name="form-name" value="email-capture" />
                <input type="hidden" name="bot-field" />
                <input type="hidden" name="text-title" value="{title}" />
                <input
                    type="email"
                    name="email"
                    placeholder="Your email"
                    class="flex-1 px-4 py-3 rounded border border-rule bg-white text-ink placeholder:text-inkMuted focus:outline-none focus:border-accent transition-colors"
                    required
                />
                <button type="submit" class="bg-accent text-white px-5 py-3 rounded font-medium hover:bg-ink transition-colors">
                    Get it
                </button>
            </form>
        </section>

        <!-- CTA hook -->
        <section class="px-6 py-6 border-t border-rule">
            <a href="mailto:hello@luminait.app?subject=Essay%20help%20-%20{title}" class="block bg-accentLight rounded p-5 flex items-center justify-between hover:bg-accentLight/70 transition-colors group">
                <div>
                    <p class="font-serif font-medium text-ink group-hover:text-accent transition-colors">Need help with your {title} essay?</p>
                    <p class="text-sm text-accent mt-1">Learn the method &rarr;</p>
                </div>
                <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
            </a>
        </section>

        <!-- Footer -->
        <footer class="px-6 py-6 border-t border-rule">
            <p class="text-xs text-inkMuted text-center"><a href="/" class="hover:text-accent transition-colors">&larr; LumintAIT</a> &middot; <a href="/about.html" class="hover:text-accent transition-colors">About</a> &middot; &copy; 2024</p>
        </footer>
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
                setTimeout(() => {{ btn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Copy'; }}, 2000);
            }});
        }}
    </script>
</body>
</html>
'''

# Section template with climax detection
SECTION_TEMPLATE = '''<div class="p-4 rounded {bg_class}">
    <p class="text-xs tracking-wide uppercase mb-2 {label_class}">{section}</p>
    <p class="text-ink text-sm leading-relaxed">{meaning}</p>
</div>'''

# Device card template
DEVICE_TEMPLATE = '''<div class="p-4 bg-cream rounded border-l-2 border-accent">
    <div class="flex justify-between items-start mb-2">
        <p class="text-xs tracking-wide text-accent uppercase font-medium">{name}</p>
        <p class="text-xs text-inkMuted">Ch. {chapter}</p>
    </div>
    <p class="font-serif text-ink italic mb-3">"{quote}"</p>
    <p class="text-sm text-inkLight leading-relaxed">{effect}</p>
</div>'''


INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5-Minute Literary Analysis</title>
    <meta name="description" content="Understand VCE texts in 5 minutes. Plain-language analysis with thesis, quotes, and essay evidence.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        cream: '#FAF9F6',
                        ink: '#1a1a1a',
                        inkLight: '#4a4a4a',
                        inkMuted: '#767676',
                        accent: '#9f1239',
                        accentLight: '#fff1f2',
                        rule: '#E8E4E0',
                    }},
                    fontFamily: {{
                        serif: ['Playfair Display', 'Georgia', 'serif'],
                        sans: ['Source Sans 3', 'system-ui', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-cream min-h-screen font-sans text-ink">
    <div class="max-w-lg mx-auto bg-white min-h-screen shadow-sm border-x border-rule">
        
        <!-- Header -->
        <header class="px-6 pt-10 pb-8 border-b border-rule">
            <p class="text-xs tracking-widest text-inkMuted uppercase mb-3">Literary Analysis</p>
            <h1 class="font-serif text-3xl font-semibold text-ink leading-tight mb-3">Five-Minute<br>Analysis</h1>
            <p class="text-inkLight text-base leading-relaxed">Understand your texts. Plain language. Usable thesis. Essay evidence.</p>
        </header>
        
        <!-- Text List -->
        <main class="px-6 py-8">
            <p class="text-xs tracking-widest text-inkMuted uppercase mb-6">Available Texts</p>
            
            <div class="divide-y divide-rule">
                {text_links}
            </div>
        </main>
        
        <!-- Footer -->
        <footer class="px-6 py-8 border-t border-rule">
            <p class="text-xs text-inkMuted text-center">&copy; 2024</p>
        </footer>
    </div>
</body>
</html>
'''

TEXT_LINK_TEMPLATE = '''<a href="{slug}.html" class="block py-5 group">
    <p class="font-serif text-xl font-medium text-ink group-hover:text-accent transition-colors">{title}</p>
    <p class="text-sm text-inkMuted mt-1">{author}</p>
</a>'''


def slugify(title: str) -> str:
    """Convert title to URL-safe slug."""
    return title.lower().replace(' ', '-').replace("'", '').replace('"', '').replace(':', '').replace('.', '')


def generate_sections_html(sections: list) -> str:
    """Generate HTML for all sections with climax highlighting."""
    html_parts = []
    climax_sections = ['climax', 'crisis']
    
    for section in sections:
        section_lower = section['section'].lower()
        is_climax = any(c in section_lower for c in climax_sections)
        
        html_parts.append(SECTION_TEMPLATE.format(
            section=section['section'],
            meaning=section['meaning'],
            bg_class='bg-accentLight border border-accent/20' if is_climax else 'bg-cream',
            label_class='text-accent font-medium' if is_climax else 'text-inkMuted'
        ))
    return ''.join(html_parts)


def generate_devices_html(devices: list) -> str:
    """Generate HTML for all device cards."""
    if not devices:
        return '<p class="text-inkMuted italic">No devices available.</p>'
    
    html_parts = []
    for device in devices:
        html_parts.append(DEVICE_TEMPLATE.format(
            name=device['name'],
            chapter=device.get('chapter', '?'),
            quote=device['quote'],
            effect=device['effect']
        ))
    return ''.join(html_parts)


def generate_page(content: dict) -> str:
    """Generate full HTML page from content JSON."""
    
    sections_html = generate_sections_html(content['layer_2_meaning_by_section'])
    devices_html = generate_devices_html(content.get('devices', []))
    
    return HTML_TEMPLATE.format(
        title=content['metadata']['title'],
        author=content['metadata']['author'],
        who_tells_it=content['layer_1_whats_happening']['who_tells_it'],
        what_we_experience=content['layer_1_whats_happening']['what_we_experience'],
        how_it_feels=content['layer_1_whats_happening']['how_it_feels'],
        sections_html=sections_html,
        devices_html=devices_html,
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
        
        with open(json_file, 'r', encoding='utf-8') as f:
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
