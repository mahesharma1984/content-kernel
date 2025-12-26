# Literary Analysis Site

A static site for literary analysis content, deployed to Netlify.

## Directory Structure

```
/
├── dist/                        # Publish directory (Netlify serves this)
│   ├── index.html               # Homepage (auto-generated)
│   ├── sitemap.xml              # Sitemap (auto-generated)
│   ├── robots.txt               # Static
│   ├── _headers                 # Netlify headers
│   └── [book-slug]/             # Book folders (manually added)
│       ├── index.html           # Analysis page
│       ├── themes/              # Theme pages
│       │   └── [theme-slug]/
│       │       └── index.html
│       └── essay-guide/         # Essay guide page
│           └── index.html
├── scripts/
│   ├── build-homepage.js        # Generates dist/index.html
│   └── build-sitemap.js         # Generates dist/sitemap.xml
├── templates/
│   └── homepage.html            # Template for index.html
├── netlify.toml                 # Netlify config
├── package.json                 # Scripts: npm run build
└── README.md                    # This file
```

## Adding a New Page

1. Create your HTML file for the book analysis
2. Create the book folder in `dist/`:
   ```bash
   mkdir -p dist/[book-slug]
   ```
3. Copy your HTML file:
   ```bash
   cp your-book-analysis.html dist/[book-slug]/index.html
   ```
4. Run the build to update homepage and sitemap:
   ```bash
   npm run build
   ```
5. Commit and push — Netlify deploys automatically

## Build Scripts

### Full Build
```bash
npm run build
```
Generates both homepage and sitemap.

### Homepage Only
```bash
npm run build:homepage
```
Scans `dist/` for book folders and generates `dist/index.html` with links.

### Sitemap Only
```bash
npm run build:sitemap
```
Walks `dist/` recursively and generates `dist/sitemap.xml` with all pages.

## How It Works

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
- **Build command:** `npm run build`

## Archive

Legacy pipeline scripts and content are preserved in the `archive/` directory.
