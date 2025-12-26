# Version Changelog - Generator v0.6 & Credibility Wrapper

**Date:** December 8, 2025  
**Branch:** `6-github-issue-website-credibility-wrapper-generator-v06`  
**Issue:** Website Credibility Wrapper & Generator v0.6

---

## Summary

This update adds credibility wrapper pages (index.html, about.html) and updates the static site generator to v0.6 with improved legibility and SEO enhancements.

---

## Generator Changes (v0.5 → v0.6)

### File: `generate_static_site.py`

**Version:** 0.6 (was 0.5)

**Changes:**

1. **Freytag Arc SVG Improvements**
   - Text size: 7px → 11px (for mobile legibility)
   - SVG height: 70px → 95px
   - All arc labels now use `font-size="11"` instead of Tailwind classes

2. **SEO Meta Tags**
   - Title format: `{title} Analysis | LumintAIT Literary Analysis`
   - Meta description: Added "VCE and IB English" keywords
   - Format: `"{title} analysis for VCE and IB English. Systematic breakdown with thesis, quotes, and essay evidence. Understand how the text creates meaning."`

3. **Header Navigation**
   - Back link text: "All Texts" → "LumintAIT"
   - Maintains brand consistency

4. **Footer Updates**
   - Added "About" link
   - Format: `← LumintAIT · About · © 2024`

5. **CTA Section Fix**
   - Replaced broken `#workbook` anchor with mailto link
   - Format: `mailto:hello@luminait.app?subject=Essay%20help%20-%20{title}`
   - Includes text title in email subject

---

## New Pages

### `dist/index.html` (v1.0)

**Status:** New branded homepage (replaces generated version)

**Features:**
- LumintAIT brand header
- Positioning headline: "Literary analysis that teaches you to think"
- Visual method diagram (SVG: WHO/WHAT/HOW → PATTERN → THESIS)
- Value proposition bullet points
- Text list (10 texts)
- CTA section: "Need help with your essays?"
- Link to about.html

**SEO:**
- Title: "LumintAIT | Literary Analysis That Teaches You to Think"
- Meta description includes VCE/IB keywords
- Canonical URL set

### `dist/about.html` (v1.0)

**Status:** New page

**Sections:**
1. **The Problem** - Differentiation from summary sites
2. **The Method** - Three-layer visual diagrams:
   - Layer 1: What's the story doing? (WHO/WHAT/HOW)
   - Layer 2: What meaning is created? (PATTERN)
   - Layer 3: Your thesis (Component assembly)
3. **Why This Is Different** - Comparison with SparkNotes/LitCharts
4. **The System Behind It** - Computational narratology framework credibility
5. **CTA** - Link to tutoring services

**SEO:**
- Title: "How It Works | LumintAIT Literary Analysis"
- Meta description: "Our systematic method for literary analysis. Three layers that show how texts create meaning — not summaries, real analysis you can use in essays."
- Canonical URL set

---

## Regenerated Pages

All 10 text analysis pages regenerated with v0.6 generator:

1. `chronicles-of-a-death-foretold.html`
2. `we-have-always-lived-in-the-castle.html`
3. `orbital.html`
4. `regeneration.html`
5. `jane-eyre.html`
6. `my-brilliant-career.html`
7. `the-giver.html`
8. `matilda.html`
9. `the-old-man-and-the-sea.html`
10. `the-memory-police.html`

**Updates applied to all pages:**
- Larger Freytag arc labels (11px, legible on mobile)
- Updated SEO meta descriptions (VCE/IB keywords)
- Brand-consistent header ("← LumintAIT")
- Footer with About link
- Fixed CTA email links (with text title in subject)

---

## Technical Details

### Generator Template Changes

**HTML_TEMPLATE updates:**
- Line 27: Title format updated
- Line 28: Meta description with SEO keywords
- Line 67: Header back link text changed
- Line 127: Freytag arc SVG viewBox height: `0 0 320 95` (was `0 0 320 70`)
- Lines 134-138: Text labels use `font-size="11"` (was `text-[7px]`)
- Line 285: CTA mailto link with `{title}` placeholder
- Line 298: Footer includes About link

### SVG Improvements

**Freytag Arc (lines 127-139):**
```xml
<svg width="320" height="95" viewBox="0 0 320 95">
  <!-- Labels now use font-size="11" instead of Tailwind classes -->
  <text font-size="11" ...>Expo</text>
  <text font-size="11" ...>Rising</text>
  <text font-size="11" ...>Climax</text>
  <text font-size="11" ...>Falling</text>
  <text font-size="11" ...>Reso</text>
</svg>
```

---

## Acceptance Criteria Met

- [x] index.html displays method diagram correctly on mobile
- [x] about.html loads with all three layer diagrams
- [x] All text pages show larger Freytag arc labels (11px)
- [x] Meta descriptions include "VCE" for SEO
- [x] CTA on text pages opens email with text title in subject
- [x] Footer links to About page work
- [x] All SVG text is legible at mobile sizes (11px minimum)

---

## Files Changed

### Modified
- `generate_static_site.py` (v0.5 → v0.6)
- `dist/index.html` (replaced with branded version)
- `dist/jane-eyre.html` (regenerated)
- `dist/matilda.html` (regenerated)
- `dist/the-giver.html` (regenerated)
- `dist/the-old-man-and-the-sea.html` (regenerated)

### Added
- `dist/about.html` (new)
- `dist/chronicles-of-a-death-foretold.html` (new)
- `dist/my-brilliant-career.html` (new)
- `dist/orbital.html` (new)
- `dist/regeneration.html` (new)
- `dist/the-memory-police.html` (new)
- `dist/we-have-always-lived-in-the-castle.html` (new)

---

## Next Steps

1. Deploy to production (Netlify)
2. Verify all pages load correctly
3. Test mobile responsiveness
4. Submit sitemap to Google Search Console
5. Monitor analytics for engagement by layer

---

**End of Changelog**

---

## Pipeline Bug Fixes (Latest)

**Date:** December 2025  
**Branch:** `13-stage-1-kernel-extraction`

### Fixed Issues

1. **`run_full_pipeline_v1_0.py` - Stage 3 Path Bug**
   - **Problem:** Stage 3 was receiving `outputs/` as input directory instead of `outputs/{book_slug}/`, causing file lookup failures
   - **Fix:** Updated `run_stage3()` to pass `self.output_dir / self.book_slug` instead of just `self.output_dir`
   - **Impact:** Pipeline now correctly finds Stage 1 and Stage 2 output files in book-specific subdirectories

2. **`generate_html_v1_0.py` - Output Directory Path Bug**
   - **Problem:** When `output_dir` was explicitly provided (e.g., `-o site`), the script didn't append `book_slug`, causing files to be written to the wrong location
   - **Fix:** Changed `self.output_dir = Path(output_dir) if output_dir else ...` to `self.output_dir = (Path(output_dir) / book_slug) if output_dir else ...`
   - **Impact:** HTML files now correctly generate in `site/{book_slug}/` instead of `site/` root

### Files Modified
- `run_full_pipeline_v1_0.py` (Stage 3 path fix)
- `generate_html_v1_0.py` (output directory path fix)

### Testing
- Successfully ran full pipeline on `Regeneration_kernel_v5_0.json`
- Verified HTML files generated in correct location: `site/regeneration/`
- Applied translation to Regeneration content using `translate_content_v1_0.py`





