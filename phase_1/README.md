# Phase 1: Audience & Messages (Stages 1 + 3)

This directory contains scripts and prompts for Phase 1 of the Content Kernel KDD implementation.

## Overview

Phase 1 is manual exploration to understand:
- Stage 1: Audience Mapping
- Stage 3: Message Derivation

**Goal:** Understand what these stages produce and validate the reasoning/precision split.

## Prerequisites

1. Python 3.7+
2. `anthropic` package installed: `pip install anthropic`
3. `ANTHROPIC_API_KEY` environment variable set
4. To Kill a Mockingbird kernel file: `To_Kill_a_Mockingbird_kernel_v5_1.json`

## Directory Structure

```
phase_1/
├── stage_1_generate.py      # Generate audience profile
├── stage_3_generate.py      # Generate message matrix
└── README.md                # This file

prompts/phase_1/
├── stage_1_audience.txt     # Stage 1 prompt template
└── stage_3_messages.txt     # Stage 3 prompt template

validation/
├── load_kernel.py           # Load and display kernel structure
├── validate_stage_1.py      # Validate audience profile
└── validate_stage_3.py      # Validate message matrix

outputs/manual_exploration/phase_1/
├── TKAM_stage_1_audience.json    # Stage 1 output
└── TKAM_stage_3_messages.json    # Stage 3 output
```

## Workflow

### Step 1: Load and Inspect Kernel

```bash
python validation/load_kernel.py To_Kill_a_Mockingbird_kernel_v5_1.json
```

This displays key kernel elements to understand what we're working with.

### Step 2: Generate Stage 1 (Audience Profile)

```bash
python phase_1/stage_1_generate.py
```

Or with custom paths:
```bash
python phase_1/stage_1_generate.py \
    To_Kill_a_Mockingbird_kernel_v5_1.json \
    prompts/phase_1/stage_1_audience.txt \
    outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json
```

This will:
- Load the text kernel
- Call Claude API with Stage 1 prompt
- Generate audience profile with 3-5 segments
- Save to JSON file

### Step 3: Validate Stage 1 Output

```bash
python validation/validate_stage_1.py \
    outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json
```

This validates:
- Kernel references exist
- Device names are valid
- Search terms are present
- Pain points connect to kernel

### Step 4: Generate Stage 3 (Message Matrix)

```bash
python phase_1/stage_3_generate.py
```

Or with custom paths:
```bash
python phase_1/stage_3_generate.py \
    To_Kill_a_Mockingbird_kernel_v5_1.json \
    outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json \
    prompts/phase_1/stage_3_messages.txt \
    outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json
```

This will:
- Load text kernel and audience profile
- Call Claude API with Stage 3 prompt
- Generate 12-20 message angles (3-5 per channel)
- Save to JSON file

### Step 5: Validate Stage 3 Output

```bash
python validation/validate_stage_3.py \
    outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json
```

This validates:
- Kernel element references
- Pain point connections
- Channel distribution (3+ angles per channel)

## Manual Review & Documentation

After validation, create observation documents:

1. `outputs/manual_exploration/phase_1/stage_1_observations.md`
   - What worked/didn't work
   - Prompt effectiveness
   - Kernel integration quality

2. `outputs/manual_exploration/phase_1/stage_3_observations.md`
   - Angle quality assessment
   - Derived vs imposed messages
   - Channel differentiation

See `CURSOR_PHASE_1_Audience_Messages.md` for observation templates.

## Troubleshooting

### API Key Not Set
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### JSON Parse Errors
- Check for `.raw` file with full API response
- Manually extract JSON if needed
- Verify prompt format

### Validation Failures
- Review invalid kernel references
- Check device name spelling
- Ensure pain points connect to audience segments

### Missing Dependencies
```bash
pip install anthropic
```

## Next Steps

After Phase 1 is complete:
- Phase 2: Selection (Stages 4 + 2)
- Phase 3: Refinement (Stage 5)
- Phase 4: Schema Definition
- Phase 5: Automation


