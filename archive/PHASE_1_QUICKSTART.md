# Phase 1 Quick Start Guide

## What Was Created

All Phase 1 implementation files have been created:

### Scripts
- ✅ `validation/load_kernel.py` - Inspect kernel structure
- ✅ `phase_1/stage_1_generate.py` - Generate audience profile
- ✅ `validation/validate_stage_1_v2.py` - Validate audience profile (PRECISION checks)
- ✅ `phase_1/stage_3_generate.py` - Generate message matrix
- ✅ `validation/validate_stage_3_v2.py` - Validate message matrix (PRECISION checks)

### Prompts
- ✅ `prompts/phase_1/stage_1_audience.txt` - Stage 1 prompt template
- ✅ `prompts/phase_1/stage_3_messages.txt` - Stage 3 prompt template

### Directories
- ✅ `outputs/manual_exploration/phase_1/` - Output directory
- ✅ `prompts/phase_1/` - Prompt directory
- ✅ `validation/` - Validation scripts
- ✅ `phase_1/` - Generation scripts

## Quick Start

### 1. Set API Key
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. Install Dependencies
```bash
pip install anthropic
```

### 3. Inspect Kernel (Optional)
```bash
python validation/load_kernel.py To_Kill_a_Mockingbird_kernel_v5_1.json
```

### 4. Run Stage 1
```bash
python phase_1/stage_1_generate.py
```

### 5. Validate Stage 1 (PRECISION)
```bash
python validation/validate_stage_1_v2.py outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json
```

This validates PRECISION checks only:
- Device names match (exact)
- Pattern referenced (exact)
- Search term counts (>=3)

Items flagged for manual review are NOT failures - they need human judgment for semantic accuracy.

### 6. Run Stage 3
```bash
python phase_1/stage_3_generate.py
```

### 7. Validate Stage 3 (PRECISION)
```bash
python validation/validate_stage_3_v2.py outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json
```

This validates PRECISION checks only:
- Exact device name matches
- Exact pattern name matches
- Structural completeness

Items flagged for manual review need human judgment for semantic accuracy (e.g., "Dual Consciousness" may not be an exact device name but appears in kernel text).

## Expected Outputs

After running, you should have:
- `outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json`
- `outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json`

## Validation Philosophy

This phase uses split validation:

**PRECISION (automated):**
- Code checks exact string matches
- Binary yes/no on structure
- Fast, deterministic

**REASONING (manual):**
- Human assesses semantic accuracy
- Judgment calls on derivation
- Requires domain knowledge

**Why split?** Code can't judge if "Child Narrator" accurately describes `N_v:FP + focalization:INT`. That's a REASONING task requiring human judgment.

Items flagged for "manual review" are not errors - they're semantic matches that need human confirmation.

## Next Steps

1. Review generated outputs manually
2. Complete manual reasoning review for flagged items:
   - Use `outputs/manual_exploration/phase_1/stage_3_reasoning_validation.md` template
   - Assess semantic accuracy of references
   - Document verdicts (ACCURATE/QUESTIONABLE/INACCURATE)
3. Create observation documents (see `CURSOR_PHASE_1_Audience_Messages.md` for templates)
4. Document what worked/didn't work
5. Proceed to Phase 2 (Selection) once Phase 1 is validated

## Notes

- All scripts use the v5.1 kernel structure (`alignment_pattern`, `micro_devices`)
- Scripts handle JSON extraction from Claude responses automatically
- Validation scripts (v2) provide detailed feedback with precision/reasoning split
- Manual review is required for semantic accuracy - this is expected, not a bug
- See `phase_1/README.md` for detailed documentation


