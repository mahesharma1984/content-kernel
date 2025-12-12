# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-01-XX

### Refactor: Staged Kernel Extraction Pipeline (Stage 1)

#### Major Changes

**Removed:**
- Old `Content_Pedagogical/` directory structure with device-specific JSON files
- Old single-file output format (`*_content_v1.0.json` files)
- Deprecated scripts:
  - `convert_kernel_to_content_v0_3.py`
  - `generate_static_site.py`

**Added:**

**New Pipeline Scripts:**
- `extract_kernel_v1_0.py` - Stage 1: Pure data extraction from kernels (no API calls)
- `convert_kernel_to_content_v2_0.py` - Staged pipeline orchestrator (Stage 1 → Stage 2 → Stage 3)
- `assemble_pages_v1_0.py` - Stage 3: Page assembly and final content generation
- `translate_content_v1_0.py` - Translation support for content
- `run_pipeline_all_kernels.py` - Batch processing script for multiple kernels

**New Directory Structure:**
- `prompts/` - Prompt templates for API-driven content derivation
- `site/` - Static site generation assets
- `outputs/` - Restructured with per-book subdirectories:
  - Each book has its own directory (e.g., `brideshead_revisited/`, `jane_eyre/`)
  - Each book directory contains:
    - `hub.json` - Central navigation hub
    - `essay_guide.json` - Essay writing guide
    - `stages/` - Stage outputs:
      - `stage1_extraction.json` - Pure extraction results
      - `stage2_derivations.json` - API-derived content (themes, thesis)
    - `themes/` - Individual theme JSON files

**Updated Files:**
- `dist/_headers` - Site configuration headers
- `dist/about.html` - About page updates
- `dist/robots.txt` - Robots.txt configuration

#### Architecture

This refactoring implements a clean three-stage pipeline:

1. **Stage 1: Extraction** (`extract_kernel_v1_0.py`)
   - Pure data extraction from kernel JSON files
   - No API calls, no transformations
   - Extracts all data required by Stage 2 Content Taxonomy

2. **Stage 2: Derivation** (`convert_kernel_to_content_v2_0.py`)
   - API-driven content derivation
   - Generates themes, thesis statements, and analytical content
   - Uses Anthropic Claude API

3. **Stage 3: Assembly** (`assemble_pages_v1_0.py`)
   - Assembles final page JSONs
   - Combines extracted and derived content
   - No API calls

#### Benefits

- **Separation of Concerns**: Each stage has a single, well-defined responsibility
- **Resumability**: Pipeline can resume from any stage using `--resume-from` flag
- **Modularity**: Each stage can be run independently
- **Better Organization**: Output structure is organized by book with clear separation of stages
- **Maintainability**: Cleaner codebase with deprecated code moved to archive directories

#### Migration Notes

- Old output files have been moved to `outputs/Old 12:10 Staged implementation/`
- Old `Content_Pedagogical/` structure moved to `Old 12:12 Staged implementation/Content_Pedagogical/`
- Old scripts archived in `Old 12:12 Staged implementation/`
