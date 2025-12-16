# Phase 1 Quick Start Guide

## What Was Created

All Phase 1 implementation files have been created:

### Scripts
- ✅ `validation/load_kernel.py` - Inspect kernel structure
- ✅ `phase_1/stage_1_generate.py` - Generate audience profile
- ✅ `validation/validate_stage_1.py` - Validate audience profile
- ✅ `phase_1/stage_3_generate.py` - Generate message matrix
- ✅ `validation/validate_stage_3.py` - Validate message matrix

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

### 5. Validate Stage 1
```bash
python validation/validate_stage_1.py outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json
```

### 6. Run Stage 3
```bash
python phase_1/stage_3_generate.py
```

### 7. Validate Stage 3
```bash
python validation/validate_stage_3.py outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json
```

## Expected Outputs

After running, you should have:
- `outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json`
- `outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json`

## Next Steps

1. Review generated outputs manually
2. Create observation documents (see `CURSOR_PHASE_1_Audience_Messages.md` for templates)
3. Document what worked/didn't work
4. Proceed to Phase 2 (Selection) once Phase 1 is validated

## Notes

- All scripts use the v5.1 kernel structure (`alignment_pattern`, `micro_devices`)
- Scripts handle JSON extraction from Claude responses automatically
- Validation scripts provide detailed feedback on kernel references
- See `phase_1/README.md` for detailed documentation


