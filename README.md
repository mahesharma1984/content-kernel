# Content Kernel Pipeline

A staged pipeline for generating literary analysis content from kernel JSON files.

## Overview

The pipeline consists of 4 main stages plus an optional translation stage:

1. **Stage 1: Kernel Extraction** - Extracts data from kernel JSON files
2. **Stage 2: Content Derivation** - Generates themes and theses (requires API key)
3. **Stage 3: Page Assembly** - Assembles pages from Stage 1 and Stage 2 outputs
4. **Stage 3A: Translation** (Optional) - Translates content for Year 10-12 students
5. **Stage 4: HTML Generation** - Generates static HTML files

## Quick Start

### Run Full Pipeline

```bash
# Run all stages on a kernel
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json

# Skip Stage 2 (if you already have derivations)
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json --skip-stage2

# Resume from a specific stage
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json --resume-from stage3
```

### Individual Stages

```bash
# Stage 1: Extract kernel data
python3 extract_kernel_v1_0.py Regeneration_kernel_v5_0.json -o outputs/

# Stage 2: Derive themes and theses (requires ANTHROPIC_API_KEY)
python3 convert_kernel_to_content_v2_0.py Regeneration_kernel_v5_0.json -o outputs/

# Stage 3: Assemble pages
python3 assemble_pages_v1_0.py regeneration -i outputs/regeneration -o outputs/regeneration

# Stage 3A: Translate content (requires ANTHROPIC_API_KEY)
python3 translate_content_v1_0.py regeneration -i outputs/regeneration

# Stage 4: Generate HTML
python3 generate_html_v1_0.py regeneration -i outputs/regeneration -o site
```

## Directory Structure

```
.
├── outputs/                    # JSON outputs from pipeline stages
│   └── {book_slug}/
│       ├── stage1_extraction.json
│       ├── stages/
│       │   ├── stage1_extraction.json
│       │   └── stage2_derivations.json
│       ├── hub.json
│       ├── themes/
│       │   └── {theme-slug}.json
│       └── essay_guide.json
├── site/                       # Generated HTML files
│   └── {book_slug}/
│       ├── index.html
│       ├── themes/
│       │   └── {theme-slug}/
│       │       └── index.html
│       └── essay-guide/
│           └── index.html
└── {book}_kernel_v*.json       # Kernel input files
```

## Environment Variables

- `ANTHROPIC_API_KEY` - Required for Stage 2 (content derivation) and Stage 3A (translation)

## Pipeline Scripts

### `run_full_pipeline_v1_0.py`
Main pipeline orchestrator that runs all stages sequentially.

**Usage:**
```bash
python3 run_full_pipeline_v1_0.py <kernel_file> [options]
```

**Options:**
- `-o, --output-dir` - Output directory for JSON files (default: `outputs`)
- `-s, --site-dir` - Output directory for HTML files (default: `site`)
- `--skip-stage2` - Skip Stage 2 (content derivation)
- `--resume-from` - Resume from specific stage (`stage2`, `stage3`, `stage4`)

### `extract_kernel_v1_0.py`
Stage 1: Extracts required data from kernel JSON files.

**Usage:**
```bash
python3 extract_kernel_v1_0.py <kernel_file> -o <output_dir>
```

### `convert_kernel_to_content_v2_0.py`
Stage 2: Derives themes and theses from Stage 1 extraction (requires API).

**Usage:**
```bash
python3 convert_kernel_to_content_v2_0.py <kernel_file> -o <output_dir> [--resume-from stage2]
```

### `assemble_pages_v1_0.py`
Stage 3: Assembles final page JSONs from Stage 1 and Stage 2 outputs.

**Usage:**
```bash
python3 assemble_pages_v1_0.py <book_slug> -i <input_dir> -o <output_dir>
```

### `translate_content_v1_0.py`
Stage 3A: Translates dense academic content into pedagogically structured text for Year 10-12 students.

**Usage:**
```bash
python3 translate_content_v1_0.py <book_slug> -i <input_dir>
```

**Note:** This modifies the JSON files in place. Run before Stage 4 to see translated content in HTML.

### `generate_html_v1_0.py`
Stage 4: Generates static HTML files from Stage 3 page JSONs.

**Usage:**
```bash
python3 generate_html_v1_0.py <book_slug> -i <input_dir> -o <output_dir>
```

## Known Issues & Fixes

### Fixed: Stage 3 Path Issue
- **Problem:** Pipeline was passing base `outputs/` directory instead of book-specific subdirectory
- **Status:** Fixed in `run_full_pipeline_v1_0.py`

### Fixed: HTML Output Path Issue
- **Problem:** HTML files were generated in `site/` root instead of `site/{book_slug}/`
- **Status:** Fixed in `generate_html_v1_0.py`

## Examples

### Complete Pipeline Run
```bash
# 1. Extract kernel
python3 extract_kernel_v1_0.py Regeneration_kernel_v5_0.json -o outputs/

# 2. Derive content (if needed)
python3 convert_kernel_to_content_v2_0.py Regeneration_kernel_v5_0.json -o outputs/

# 3. Assemble pages
python3 assemble_pages_v1_0.py regeneration -i outputs/regeneration -o outputs/regeneration

# 4. Translate (optional but recommended)
python3 translate_content_v1_0.py regeneration -i outputs/regeneration

# 5. Generate HTML
python3 generate_html_v1_0.py regeneration -i outputs/regeneration -o site
```

### Using Full Pipeline Script
```bash
# All stages
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json

# Skip Stage 2 (already have derivations)
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json --skip-stage2

# Resume from Stage 3 (after translation)
python3 run_full_pipeline_v1_0.py Regeneration_kernel_v5_0.json --resume-from stage3
```

## Notes

- Stage 2 and Stage 3A require `ANTHROPIC_API_KEY` environment variable
- Translation (Stage 3A) should be run after Stage 3 but before Stage 4
- HTML files are generated in `site/{book_slug}/` directory structure
- All JSON outputs are saved in `outputs/{book_slug}/` directory structure
