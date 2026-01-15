# Literary Analysis Site

A static site for literary analysis content, deployed to Netlify.

## Directory Structure

```
/
├── dist/                        # Publish directory (Netlify serves this)
│   ├── index.html               # Homepage (auto-generated)
│   ├── sitemap.xml              # Sitemap (auto-generated)
│   └── [book-slug]/             # Book folders
│       └── index.html           # Analysis page
├── kernels/                     # Source kernel JSON files
│   └── [Book]_kernel_v*.json
├── scripts/
│   ├── generate_page.py         # Converts kernel → HTML page
│   ├── build_homepage.py        # Generates dist/index.html
│   ├── build_sitemap.py         # Generates dist/sitemap.xml
│   └── build_all.py             # Runs homepage + sitemap builds
├── templates/
│   └── homepage.html            # Template for index.html
├── pedagogy/                    # Pedagogical research (separate concern)
│   └── README.md                # See pedagogy/README.md for details
├── netlify.toml                 # Netlify config
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Generating a Page from a Kernel

```bash
python scripts/generate_page.py kernels/[Book]_kernel_v*.json
```

This uses Claude API to transform the kernel into a student-friendly HTML page.

## Build Scripts

### Full Build
```bash
python scripts/build_all.py
```
Generates both homepage and sitemap.

### Homepage Only
```bash
python scripts/build_homepage.py
```
Scans `dist/` for book folders and generates `dist/index.html` with links.

### Sitemap Only
```bash
python scripts/build_sitemap.py
```
Walks `dist/` recursively and generates `dist/sitemap.xml` with all pages.

## How It Works

### Page Generation
- Reads kernel JSON (pattern, devices, narrative structure)
- Calls Claude API to generate student-friendly HTML
- Applies pedagogy framework for Year 10-12 students
- Outputs to `dist/[book-slug]/index.html`

### Homepage Generation
- Scans `dist/` for directories containing `index.html`
- Extracts the page title from each book's `<title>` tag
- Generates a homepage with links to each book

### Sitemap Generation
- Recursively walks `dist/` directory
- Finds all `index.html` files
- Generates XML sitemap with all page URLs

## Deployment

The site deploys automatically to Netlify on push. Configuration is in `netlify.toml`:
- **Publish directory:** `dist`
- **Build command:** `python scripts/build_all.py`

## Requirements

```bash
pip install -r requirements.txt
```

Requires `anthropic` SDK for page generation.
