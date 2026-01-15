# Pedagogy

This folder contains pedagogical research and content development work using the KDD (Kernel-Driven Derivation) methodology.

**Status:** This work is separate from the core build pipeline and will eventually be extracted to its own repository.

## Structure

```
pedagogy/
├── phase_1/        # Audience mapping + message derivation
├── phase_2/        # Selection + refinement
├── prompts/        # Prompt templates for generation stages
├── validation/     # Validation scripts for stage outputs
└── outputs/        # Generated content from pipeline runs
```

## Phase 1: Audience Mapping

- `stage_1_generate.py` - Generate audience profiles (Year 10-12 students)
- `stage_3_generate.py` - Derive message angles for students
- `stage_5a_generate.py` - Create exploratory drafts

## Phase 2: Selection & Refinement

- `stage_2_generate.py` - Derive channel-specific jobs
- `stage_4_evaluate.py` - Evaluate angles on 4 criteria
- `stage_5b_refine.py` - Refine content to meet channel constraints

## Usage

This pipeline is not currently integrated with the main build. See individual stage files for usage instructions.
