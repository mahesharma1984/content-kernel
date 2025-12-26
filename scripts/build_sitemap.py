#!/usr/bin/env python3
"""
Build Sitemap
Walks dist/ recursively and generates sitemap.xml from all index.html files.
"""

from pathlib import Path

DIST_DIR = Path('./dist')
OUTPUT_FILE = DIST_DIR / 'sitemap.xml'
BASE_URL = 'https://luminait.app'


def find_all_pages():
    """Find all index.html files in dist/."""
    pages = []
    for index_file in DIST_DIR.rglob('index.html'):
        # Get path relative to dist
        rel_path = index_file.relative_to(DIST_DIR)
        # Convert to URL path
        url_path = str(rel_path.parent)
        if url_path == '.':
            url_path = ''
        pages.append(url_path)
    return sorted(pages)


def generate_sitemap():
    """Generate sitemap.xml."""
    pages = find_all_pages()
    
    urls = []
    for page in pages:
        if page == '':
            url = f'{BASE_URL}/'
        else:
            url = f'{BASE_URL}/{page}/'
        urls.append(f'  <url><loc>{url}</loc></url>')
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    
    OUTPUT_FILE.write_text(sitemap, encoding='utf-8')
    print(f'Sitemap generated with {len(pages)} URLs')


if __name__ == '__main__':
    generate_sitemap()


