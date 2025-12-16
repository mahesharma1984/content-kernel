# Stage 3 Reasoning Validation Template

**Date:** [Fill in]  
**Validator:** [Your name]  
**Messages file:** TKAM_stage_3_messages.json

---

## Instructions

For each reference flagged as "manual review needed", assess:

1. **Location in kernel:** Where does this concept appear?
2. **Exact match?** Is the exact phrase in the kernel?
3. **Semantic match?** Does it accurately describe a kernel concept?
4. **Reasonable?** Is this a standard way to refer to the concept?
5. **Verdict:** ACCURATE, QUESTIONABLE, or INACCURATE

---

## Example Assessment

### Reference: "Dual Consciousness"

**Location:** `alignment_pattern.reader_effect: "Readers experience dual consciousness - seeing through child's eyes while grasping adult implications"`

**Exact match?** YES - exact phrase appears

**Semantic match?** N/A (it's exact)

**Reasonable?** YES - it's the kernel's own term

**Verdict:** ✓ ACCURATE

---

### Reference: "Child Narrator"

**Location:** 
- `macro_variables.narrative.voice.pov: "FP"` (first-person)
- `macro_variables.narrative.voice.pov_description: "First person narration from Scout's perspective throughout"`
- `macro_variables.narrative.voice.focalization_description: "Limited to Scout's child perspective"`

**Exact match?** NO - not a single field

**Semantic match?** YES - accurate summary of FP + child perspective

**Reasonable?** YES - standard literary term for this narrative configuration

**Verdict:** ✓ ACCURATE (semantic match)

---

### Reference: "Retrospective Distance"

**Location:**
- `macro_variables.narrative.voice.temporal_distance: "RETRO"`
- `alignment_pattern.core_dynamic: "...retrospective distance creates dramatic irony..."`

**Exact match?** PARTIAL - "retrospective" appears, "distance" is the variable name

**Semantic match?** YES - combines temporal_distance variable with kernel language

**Reasonable?** YES - standard narratology term

**Verdict:** ✓ ACCURATE (concept match)

---

## Flagged References for Review

[Copy the list from validation script output, then assess each one using the template above]

### Reference: "[NAME]"

**Location:** 

**Exact match?**

**Semantic match?**

**Reasonable?**

**Verdict:**

---

[Repeat for each flagged reference]

---

## Summary

**Total flagged:** [Number]

**Breakdown:**
- Accurate (exact): [Count]
- Accurate (semantic): [Count]
- Questionable: [Count]
- Inaccurate: [Count]

**Action needed:**
- [ ] None - all references accurate
- [ ] Revise [X] questionable references
- [ ] Regenerate due to inaccuracies

---

## Questionable/Inaccurate References

[List any that need revision and explain why]

**Example:**
- Angle 10: "Framework" - Too generic, doesn't specifically reference kernel structure
- Angle 14: "Teaching Toolkit" - Pedagogy application, not in kernel (that's Stage 3, not analysis)

---

## Overall Assessment

Does the message matrix derive from the kernel or feel imposed?

[Your assessment]

Can you see the kernel's pattern and devices flowing into the messages?

[Your assessment]

Are there any messages that seem to ignore the kernel entirely?

[Your assessment]

**Ready to proceed to Phase 2?** [Yes/No - Explain]

