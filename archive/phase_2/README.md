# Phase 2: Selection (Stages 4, 2, and 5B)

**Goal:** Select winning thread, derive channel jobs, and refine content to meet constraints  
**Book:** To Kill a Mockingbird (TKAM)

## Overview

Phase 2 runs KDD Stages 4, 2, and 5B to:
1. Evaluate message angles against 4 selection criteria (Stage 4)
2. Select the ONE thread that will unify the funnel (Stage 4)
3. Derive channel jobs from the selected thread (Stage 2)
4. Refine winning angle's drafts to meet channel constraints (Stage 5B)

## Prerequisites

You must have completed Phase 1:
- `outputs/manual_exploration/phase_1/TKAM_stage_1_audience.json` exists
- `outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json` exists (12-20 angles)
- `outputs/manual_exploration/phase_1/TKAM_stage_5a_drafts.json` exists (optional for Stage 5B)
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

### Stage 5B: Constrained Refinement

1. **Select winning angle's drafts:**
   ```bash
   python phase_2/select_winning_drafts.py
   ```
   This finds the drafts from the winning angle in Phase 1's Stage 5A output.

2. **Review inputs:**
   ```bash
   python phase_2/review_5b_inputs.py
   ```
   Verify you have all inputs (thread, channels, starting drafts).

3. **Refine content with constraints:**
   ```bash
   python phase_2/stage_5b_refine.py
   ```
   This will:
   - Load starting drafts from winning angle
   - Apply channel constraints from Stage 2
   - Refine each channel's content to meet constraints
   - Save to `outputs/manual_exploration/phase_2/TKAM_stage_5b_content.json`

4. **Validate refined content:**
   ```bash
   python validation/validate_stage_5b.py
   ```
   Check that all constraints are met.

5. **Document observations:**
   Create `outputs/manual_exploration/phase_2/stage_5b_observations.md` (see instructions template)

## The 4 Selection Criteria

Every angle is scored 0-10 on each criterion:

1. **MEMORABLE (0-10)**: Can a student repeat it to a friend?
2. **DIFFERENTIATING (0-10)**: Does it separate us from competitors?
3. **PATTERN-ANCHORED (0-10)**: Does it lead to kernel's pattern?
4. **FUNNEL-CONTINUOUS (0-10)**: Can it stretch from agitation to delivery?

The highest total score (max 40) wins.

## Files Created

### Stage 4 (Thread Selection)
- `phase_2/review_messages.py` - Review Phase 1 message angles
- `phase_2/stage_4_evaluate.py` - Evaluate angles and select thread
- `phase_2/extract_thread.py` - Extract winning thread
- `validation/validate_stage_4.py` - Validate thread selection
- `prompts/phase_2/stage_4_selection.txt` - Stage 4 evaluation prompt

### Stage 2 (Channel Strategy)
- `phase_2/stage_2_generate.py` - Generate channel strategy
- `validation/validate_stage_2.py` - Validate channel strategy
- `prompts/phase_2/stage_2_channels.txt` - Stage 2 channel prompt

### Stage 5B (Constrained Refinement)
- `phase_2/select_winning_drafts.py` - Find winning angle's drafts
- `phase_2/review_5b_inputs.py` - Review Stage 5B inputs
- `phase_2/stage_5b_refine.py` - Refine content with constraints
- `validation/validate_stage_5b.py` - Validate refined content
- `prompts/phase_2/stage_5b_constrained.txt` - Stage 5B refinement prompt

## Outputs

### Stage 4
- `outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json` - All angles scored
- `outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json` - Winning thread
- `outputs/manual_exploration/phase_2/stage_4_observations.md` - Selection notes

### Stage 2
- `outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json` - Channel strategy
- `outputs/manual_exploration/phase_2/stage_2_observations.md` - Strategy notes

### Stage 5B
- `outputs/manual_exploration/phase_2/TKAM_stage_5b_starting_drafts.json` - Winning angle's drafts
- `outputs/manual_exploration/phase_2/TKAM_stage_5b_content.json` - Refined content blocks
- `outputs/manual_exploration/phase_2/stage_5b_observations.md` - Refinement notes

## Phase 2 Completion Checklist

### Stage 4 Complete
- [ ] `TKAM_stage_4_evaluations.json` created
- [ ] All angles scored against 4 criteria
- [ ] ONE winner selected with rationale
- [ ] `stage_4_observations.md` documented

### Stage 2 Complete
- [ ] `TKAM_stage_2_channels.json` created
- [ ] Each channel has ONE job
- [ ] Must do / must not do defined
- [ ] Jobs derive from thread
- [ ] `stage_2_observations.md` documented

### Stage 5B Complete
- [ ] `TKAM_stage_5b_starting_drafts.json` created (winning angle's drafts)
- [ ] `TKAM_stage_5b_content.json` created (refined content)
- [ ] All constraints validated
- [ ] Thread visible in all channels
- [ ] `stage_5b_observations.md` documented

### Phase 2 Overall
- [ ] Selection complete (thread + channels)
- [ ] Refinement complete (final content blocks)
- [ ] Ready for asset rendering

## Next Steps

Once Phase 2 is complete:
1. **Content kernel is ready** — all stages (1, 3, 5A, 4, 2, 5B) complete
2. **Proceed to rendering** — use content blocks to create assets (Layer 1)
3. **Asset creation** is Layer 1 (application), not kernel work

See the full instructions in `/Users/mahesh/Downloads/CURSOR_PHASE_2_Selection.md` and `/Users/mahesh/Downloads/ADDENDUM_PHASE_2_Stage_5B.md` for detailed guidance.
