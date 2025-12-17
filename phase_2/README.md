# Phase 2: Selection (Stages 4 + 2)

**Goal:** Test selection criteria and derive channel jobs from winning thread  
**Book:** To Kill a Mockingbird (TKAM)

## Overview

Phase 2 runs KDD Stages 4 and 2 to:
1. Evaluate message angles against 4 selection criteria
2. Select the ONE thread that will unify the funnel
3. Derive channel jobs from the selected thread
4. Understand whether selection can be automated or needs human judgment

## Prerequisites

You must have completed Phase 1:
- `outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json` exists
- `outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json` exists (12-20 angles)
- `To_Kill_a_Mockingbird_kernel_v5_1.json` exists

## Quick Start

### Stage 4: Thread Selection

1. **Review messages:**
   ```bash
   python phase_2/review_messages.py
   ```

2. **Evaluate and select thread:**
   ```bash
   python phase_2/stage_4_evaluate.py
   ```
   This will:
   - Load all message angles from Stage 3
   - Score each angle on 4 criteria (Memorable, Differentiating, Pattern-anchored, Funnel-continuous)
   - Select the winning thread
   - Save to `outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json`

3. **Validate selection:**
   ```bash
   python validation/validate_stage_4.py
   ```
   Review the top 5 scoring angles and confirm the winner.

4. **Extract core thread:**
   ```bash
   python phase_2/extract_thread.py
   ```
   Creates `outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json`

5. **Document observations:**
   Create `outputs/manual_exploration/phase_2/stage_4_observations.md` (see instructions template)

### Stage 2: Channel Strategy

1. **Generate channel strategy:**
   ```bash
   python phase_2/stage_2_generate.py
   ```
   This will:
   - Load the selected thread from Stage 4
   - Derive ONE job for each channel (Social, YouTube, SEO, Guide)
   - Save to `outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json`

2. **Validate channel strategy:**
   ```bash
   python validation/validate_stage_2.py
   ```
   Check that jobs derive from thread and are differentiated.

3. **Document observations:**
   Create `outputs/manual_exploration/phase_2/stage_2_observations.md` (see instructions template)

## The 4 Selection Criteria

Every angle is scored 0-10 on each criterion:

1. **MEMORABLE (0-10)**: Can a student repeat it to a friend?
2. **DIFFERENTIATING (0-10)**: Does it separate us from competitors?
3. **PATTERN-ANCHORED (0-10)**: Does it lead to kernel's pattern?
4. **FUNNEL-CONTINUOUS (0-10)**: Can it stretch from agitation to delivery?

The highest total score (max 40) wins.

## Files Created

- `phase_2/review_messages.py` - Review Phase 1 message angles
- `phase_2/stage_4_evaluate.py` - Evaluate angles and select thread
- `phase_2/extract_thread.py` - Extract winning thread
- `phase_2/stage_2_generate.py` - Generate channel strategy
- `validation/validate_stage_4.py` - Validate thread selection
- `validation/validate_stage_2.py` - Validate channel strategy
- `prompts/phase_2/stage_4_selection.txt` - Stage 4 evaluation prompt
- `prompts/phase_2/stage_2_channels.txt` - Stage 2 channel prompt

## Outputs

- `outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json` - All angles scored
- `outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json` - Winning thread
- `outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json` - Channel strategy
- `outputs/manual_exploration/phase_2/stage_4_observations.md` - Selection notes
- `outputs/manual_exploration/phase_2/stage_2_observations.md` - Strategy notes

## Next Steps

Once Phase 2 is complete, proceed to **Phase 3: Content Generation** where you'll:
1. Generate content drafts for each channel
2. Apply constraints to refine content
3. Validate that content does the ONE job

See the full instructions in `/Users/mahesh/Downloads/CURSOR_PHASE_2_Selection.md` for detailed guidance.

