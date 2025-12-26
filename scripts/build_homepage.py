#!/usr/bin/env python3
"""
Build Homepage
Scans dist/ for book folders and generates index.html with links.
"""

import re
from pathlib import Path

DIST_DIR = Path('./dist')
TEMPLATE_DIR = Path('./templates')
OUTPUT_FILE = DIST_DIR / 'index.html'


def get_book_folders():
    """Find all book folders (directories with index.html)."""
    books = []
    for item in DIST_DIR.iterdir():
        if item.is_dir() and (item / 'index.html').exists():
            books.append(item.name)
    return sorted(books)


def extract_title(slug):
    """Extract title from book's index.html <title> tag."""
    index_path = DIST_DIR / slug / 'index.html'
    try:
        html = index_path.read_text(encoding='utf-8')
        match = re.search(r'<title>([^<]+)</title>', html)
        if match:
            title = match.group(1)
            # Remove common suffixes (match JS behavior)
            title = title.replace(' — Analysis', '')
            return title
    except Exception:
        pass
    # Fallback: use slug as-is
    return slug


def generate_homepage():
    """Generate the homepage HTML."""
    books = get_book_folders()
    
    # Generate book links (match JS output format)
    links = []
    for slug in books:
        title = extract_title(slug)
        links.append(f'<li><a href="/{slug}/">{title}</a></li>')
    
    links_html = '\n'.join(links)
    
    # Read template
    template_path = TEMPLATE_DIR / 'homepage.html'
    template = template_path.read_text(encoding='utf-8')
    html = template.replace('{{BOOK_LINKS}}', links_html)
    
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f'Homepage generated with {len(books)} books')


if __name__ == '__main__':
    generate_homepage()


