#!/usr/bin/env python3
"""
HTML RENDERER - VERSION 1.0
Transforms content_stage5.json → static HTML site

Usage:
    python render_html_v1_0.py outputs/orbital/
    python render_html_v1_0.py outputs/orbital/ --output-dir dist/
    python render_html_v1_0.py outputs/orbital/ --theme dark
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


# =============================================================================
# CSS STYLESHEET
# =============================================================================

CSS = """
:root {
    --color-bg: #0a0a0f;
    --color-surface: #12121a;
    --color-surface-hover: #1a1a24;
    --color-border: #2a2a3a;
    --color-text: #e8e8ed;
    --color-text-muted: #8888a0;
    --color-accent: #7c6df0;
    --color-accent-soft: rgba(124, 109, 240, 0.15);
    --color-knowledge: #3b82f6;
    --color-pedagogy: #22c55e;
    --color-cta: #f59e0b;
    --color-question: #f59e0b;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--color-bg);
    color: var(--color-text);
    line-height: 1.7;
    min-height: 100vh;
}

.container {
    max-width: 860px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
.page-header {
    text-align: center;
    padding: 3rem 0;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 2rem;
}

.page-header h1 {
    font-size: 2.25rem;
    font-weight: 400;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}

.page-header .subtitle {
    color: var(--color-text-muted);
    font-size: 1.05rem;
}

/* Breadcrumb */
.breadcrumb {
    margin-bottom: 1rem;
    font-size: 0.9rem;
}

.breadcrumb a {
    color: var(--color-text-muted);
    text-decoration: none;
}

.breadcrumb a:hover {
    color: var(--color-accent);
}

.breadcrumb .sep {
    color: var(--color-border);
    margin: 0 0.5rem;
}

/* Zones */
.zone {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.zone-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    margin-bottom: 1.25rem;
}

.zone-knowledge .zone-badge {
    background: rgba(59, 130, 246, 0.12);
    color: var(--color-knowledge);
}

.zone-pedagogy .zone-badge {
    background: rgba(34, 197, 94, 0.12);
    color: var(--color-pedagogy);
}

.zone-cta .zone-badge {
    background: rgba(245, 158, 11, 0.12);
    color: var(--color-cta);
}

.zone h2 {
    font-size: 1.4rem;
    font-weight: 500;
    margin-bottom: 1rem;
    line-height: 1.3;
}

.zone p {
    color: var(--color-text-muted);
    margin-bottom: 1rem;
}

.zone p:last-child {
    margin-bottom: 0;
}

/* === PEDAGOGICAL CONTENT STRUCTURE === */

/* Content blocks with internal structure */
.zone .content-block {
    margin-bottom: 1.5rem;
}

/* Opening statements - slightly larger, sets context */
.zone .opening-statement {
    color: var(--color-text);
    font-size: 1.02rem;
    margin-bottom: 0.75rem;
    line-height: 1.6;
}

/* Concept groups - tighter spacing for related ideas */
.zone .concept-group {
    margin: 0.75rem 0;
    padding-left: 0.5rem;
    border-left: 2px solid var(--color-border);
}

.zone .concept-intro {
    color: var(--color-text);
    margin-bottom: 0.5rem;
    font-size: 0.98rem;
}

/* Bullet lists - visual list treatment */
.zone .bullet-list {
    margin: 0.5rem 0 0.75rem 1.5rem;
    list-style: none;
}

.zone .bullet-list li {
    position: relative;
    padding-left: 1.25rem;
    margin-bottom: 0.35rem;
    color: var(--color-text);
    line-height: 1.6;
}

.zone .bullet-list li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: var(--color-accent);
    font-weight: bold;
}

/* Scaffolding questions - visual emphasis */
.zone .scaffold-question {
    background: rgba(245, 158, 11, 0.08);
    border-left: 3px solid var(--color-question);
    padding: 0.75rem 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}

.zone .scaffold-question-intro {
    color: var(--color-question);
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.zone .scaffold-question-text {
    color: var(--color-text);
    font-style: italic;
    line-height: 1.5;
}

/* Explanatory flow - answer to question */
.zone .explanation {
    margin: 0.75rem 0;
    padding-left: 0.75rem;
}

.zone .explanation-intro {
    color: var(--color-text);
    font-weight: 500;
    margin-bottom: 0.4rem;
}

.zone .explanation-detail {
    color: var(--color-text-muted);
    line-height: 1.6;
}

/* Process flows - step by step */
.zone .process-flow {
    background: var(--color-bg);
    border-radius: 6px;
    padding: 1rem;
    margin: 0.75rem 0;
}

.zone .process-intro {
    color: var(--color-text);
    font-weight: 500;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
}

.zone .process-steps {
    list-style: none;
    margin-left: 0.5rem;
}

.zone .process-steps li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.4rem;
    color: var(--color-text-muted);
}

.zone .process-steps li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--color-pedagogy);
}

/* Emphasis statements - key takeaways */
.zone .emphasis-statement {
    color: var(--color-text);
    font-weight: 500;
    margin: 0.75rem 0;
}

/* Quick Reference */
.quick-reference {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border);
}

.quick-ref-item .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-muted);
    margin-bottom: 0.35rem;
}

.quick-ref-item .value {
    font-size: 0.9rem;
    color: var(--color-text);
    line-height: 1.5;
}

/* Worked Example */
.worked-example {
    background: var(--color-bg);
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    text-align: center;
}

.formula {
    font-size: 1.05rem;
    color: var(--color-accent);
    font-weight: 500;
}

.arrow {
    font-size: 1.4rem;
    color: var(--color-text-muted);
    margin: 0.75rem 0;
}

.effect {
    color: var(--color-text-muted);
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Prompts */
.prompts {
    list-style: none;
    margin-top: 1.25rem;
}

.prompts li {
    padding: 0.75rem 1rem;
    background: var(--color-bg);
    border-radius: 6px;
    margin-bottom: 0.5rem;
    color: var(--color-text-muted);
    font-size: 0.95rem;
}

.prompts li::before {
    content: "→ ";
    color: var(--color-pedagogy);
}

/* Device Examples */
.device-examples {
    margin-top: 1.5rem;
}

.device-examples h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text);
}

.device-example {
    background: var(--color-bg);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border-left: 3px solid var(--color-accent);
}

.device-name {
    font-weight: 600;
    color: var(--color-accent);
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
}

.device-quote {
    font-style: italic;
    color: var(--color-text);
    margin-bottom: 0.75rem;
    padding-left: 1rem;
    border-left: 2px solid var(--color-border);
    line-height: 1.6;
}

.device-effect {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    line-height: 1.5;
}

/* Pattern Connection */
.pattern-connection {
    background: var(--color-accent-soft);
    border-radius: 8px;
    padding: 1.25rem;
    margin: 1.25rem 0;
    border-left: 3px solid var(--color-accent);
}

.pattern-connection-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-accent);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.pattern-connection p {
    color: var(--color-text);
    margin: 0;
}

/* Steps */
.steps {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.step {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.step-number {
    width: 32px;
    height: 32px;
    background: var(--color-accent-soft);
    color: var(--color-accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.step-content h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: var(--color-text);
}

.step-content p {
    font-size: 0.95rem;
    color: var(--color-text-muted);
    margin: 0;
}

/* Thesis Components */
.thesis-components {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.component-box {
    background: var(--color-bg);
    border-radius: 8px;
    padding: 1rem;
}

.component-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-muted);
    margin-bottom: 0.5rem;
}

.component-value {
    color: var(--color-accent);
    font-weight: 500;
}

.component-list {
    list-style: none;
}

.component-list li {
    font-size: 0.9rem;
    color: var(--color-text);
    padding: 0.2rem 0;
}

/* Thesis Examples */
.thesis-examples {
    margin-top: 1.5rem;
}

.thesis-examples h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text);
}

.thesis-example {
    background: var(--color-bg);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

.thesis-focus {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-accent);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.thesis-statement {
    color: var(--color-text);
    margin-bottom: 0.75rem;
    line-height: 1.6;
}

.thesis-notes {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    font-style: italic;
}

/* CTA Links */
.cta-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.cta-link {
    display: inline-block;
    padding: 0.75rem 1.25rem;
    background: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    color: var(--color-text);
    text-decoration: none;
    font-size: 0.95rem;
    transition: all 0.15s ease;
}

.cta-link:hover {
    background: var(--color-accent-soft);
    border-color: var(--color-accent);
}

.cta-link.emphasis {
    background: var(--color-accent);
    border-color: var(--color-accent);
    color: white;
    font-weight: 500;
}

.cta-link.emphasis:hover {
    background: #6b5ce0;
}

/* Emphasis */
.emphasis {
    color: var(--color-text);
    font-weight: 500;
}

/* Responsive */
@media (max-width: 640px) {
    .container {
        padding: 1rem;
    }
    
    .quick-reference,
    .thesis-components {
        grid-template-columns: 1fr;
    }
    
    .page-header h1 {
        font-size: 1.75rem;
    }
}
"""


def base_template(title: str, content: str, breadcrumb: str = "") -> str:
    """Wrap content in base HTML structure."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="container">
        {breadcrumb}
        {content}
    </div>
</body>
</html>"""


# =============================================================================
# HTML RENDERER
# =============================================================================

class HTMLRenderer:
    """Renders content_stage5.json to static HTML."""
    
    def __init__(self, content_dir: str, output_dir: Optional[str] = None, theme: str = "default"):
        self.content_dir = Path(content_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("dist")
        self.theme = theme
        
        # Loaded content
        self.content = None
        self.metadata = None
        self.book_slug = None
    
    def load_content(self) -> bool:
        """Load content_stage5.json and stage1_extraction.json for metadata."""
        stage5_path = self.content_dir / "stages" / "content_stage5.json"
        
        if not stage5_path.exists():
            print(f"❌ Content not found: {stage5_path}")
            return False
        
        with open(stage5_path, 'r', encoding='utf-8') as f:
            self.content = json.load(f)
        
        # Extract book_slug from content
        self.book_slug = self.content.get("hub", {}).get("book_slug", "unknown")
        
        # Load metadata from stage1_extraction.json
        # Try stages/stage1_extraction.json first, then stage1_extraction.json in root
        stage1_path = self.content_dir / "stages" / "stage1_extraction.json"
        if not stage1_path.exists():
            stage1_path = self.content_dir / "stage1_extraction.json"
        
        if stage1_path.exists():
            with open(stage1_path, 'r', encoding='utf-8') as f:
                stage1_data = json.load(f)
            self.metadata = stage1_data.get("metadata", {})
        else:
            # Fallback: use defaults
            self.metadata = {"title": self.book_slug.replace("_", " ").title(), "author": "Unknown"}
            print(f"⚠️  stage1_extraction.json not found, using defaults")
        
        print(f"✓ Loaded content for: {self.metadata.get('title', self.book_slug)}")
        return True
    
    def validate_content(self) -> bool:
        """Validate content structure."""
        required = ["hub", "themes", "essay_guide"]
        for key in required:
            if key not in self.content:
                print(f"❌ Missing required key: {key}")
                return False
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
    
    def _render_hub_html(self, data: dict, book_title: str, book_author: str) -> str:
        """Render hub page with block support."""
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
        z = data["zones"]
        k, p, c = z["knowledge"], z["pedagogy"], z["cta"]
        
        tc = k["thesis_components"]
        
        # Theme list
        themes_list = "".join(f"<li>{t}</li>" for t in tc["themes"])
        
        # Device list
        devices_list = "".join(f"<li>{d}</li>" for d in tc["devices"])
        
        # Thesis examples
        theses = ""
        for thesis in k.get("example_theses", []):
            theses += f"""
        <div class="thesis-example">
            <div class="thesis-focus">{thesis["focus"]}</div>
            <div class="thesis-statement">{thesis["statement"]}</div>
            <div class="thesis-notes">{thesis["structure_notes"]}</div>
        </div>"""
        
        # Steps
        steps = ""
        for step in p.get("four_steps", []):
            steps += f"""
        <div class="step">
            <div class="step-number">{step["step"]}</div>
            <div class="step-content">
                <h3>{step["title"]}</h3>
                <p>{step["content"]}</p>
            </div>
        </div>"""
        
        breadcrumb = f"""
        <nav class="breadcrumb">
            <a href="/{book_slug}/">{book_title}</a>
            <span class="sep">›</span>
            Essay Guide
        </nav>
    """
        
        content = f"""
        <header class="page-header">
            <h1>{k["heading"]}</h1>
            <p class="subtitle">Building Your Thesis</p>
        </header>

        <section class="zone zone-knowledge">
            <span class="zone-badge">{k["badge"]}</span>
            <h2>Thesis Components</h2>
            
            <div class="thesis-components">
                <div class="component-box">
                    <div class="component-label">Pattern</div>
                    <div class="component-value">{tc["pattern"]}</div>
                </div>
                <div class="component-box">
                    <div class="component-label">Themes</div>
                    <ul class="component-list">{themes_list}</ul>
                </div>
                <div class="component-box">
                    <div class="component-label">Key Devices</div>
                    <ul class="component-list">{devices_list}</ul>
                </div>
            </div>
            
            <div class="thesis-examples">
                <h3>Example Theses</h3>
                {theses}
            </div>
        </section>

        <section class="zone zone-pedagogy">
            <span class="zone-badge">{p["badge"]}</span>
            <h2>From Pattern to Thesis</h2>
            <div class="steps">{steps}</div>
        </section>

        <section class="zone zone-cta">
            <span class="zone-badge">{c["badge"]}</span>
            <div class="cta-links">
                <a href="#" class="cta-link emphasis">{c["primary"]}</a>
                <a href="#" class="cta-link">{c["secondary"]}</a>
            </div>
        </section>
    """
        
        return base_template(f"Essay Guide | {book_title}", content, breadcrumb)
    
    def render(self) -> bool:
        """Generate all HTML files."""
        if not self.content:
            print("❌ No content loaded")
            return False
        
        # Create output directory
        output_path = self.output_dir / self.book_slug
        output_path.mkdir(parents=True, exist_ok=True)
        
        book_title = self.metadata.get("title", "Unknown")
        book_author = self.metadata.get("author", "Unknown")
        
        # Render hub
        hub_html = self._render_hub_html(self.content["hub"], book_title, book_author)
        (output_path / "index.html").write_text(hub_html, encoding='utf-8')
        print(f"  ✓ index.html")
        
        # Render themes
        themes_dir = output_path / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        for theme in self.content["themes"]:
            theme_slug = theme.get("theme_slug", "unknown")
            theme_html = self._render_theme_html(theme, book_title, self.book_slug)
            (themes_dir / theme_slug).mkdir(parents=True, exist_ok=True)
            (themes_dir / theme_slug / "index.html").write_text(theme_html, encoding='utf-8')
            print(f"  ✓ themes/{theme_slug}/index.html")
        
        # Render essay guide
        essay_html = self._render_essay_guide_html(self.content["essay_guide"], book_title, self.book_slug)
        (output_path / "essay-guide").mkdir(parents=True, exist_ok=True)
        (output_path / "essay-guide" / "index.html").write_text(essay_html, encoding='utf-8')
        print(f"  ✓ essay-guide/index.html")
        
        print(f"\n✅ Render complete: {output_path}/")
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='HTML Renderer v1.0 - Render content to static HTML'
    )
    parser.add_argument('content_dir', help='Path to content directory (e.g., outputs/orbital/)')
    parser.add_argument('-o', '--output-dir', default='dist', help='Output directory')
    parser.add_argument('--theme', default='default', help='Theme name')
    
    args = parser.parse_args()
    
    renderer = HTMLRenderer(args.content_dir, args.output_dir, args.theme)
    
    if not renderer.load_content():
        return 1
    
    if not renderer.validate_content():
        return 1
    
    if not renderer.render():
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())


