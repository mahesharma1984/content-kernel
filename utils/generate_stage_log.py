# utils/generate_stage_log.py
# Version: 1.0
# Date: December 17, 2025
# Purpose: Generate .md logs from stage outputs

import json
import os
import sys
from datetime import datetime

LOG_TEMPLATES = {
    "1": """# Stage 1: Audience Mapping

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete

---

## Summary

Generated {segment_count} audience segments with high-intent search terms.

## Segments

{segments_list}

## High-Intent Searches

{searches_list}

## Observations

{observations}

## Validation

- Segments generated: {segment_count}
- Search terms generated: {search_count}
""",

    "3": """# Stage 3: Message Derivation

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete

---

## Summary

Generated {angle_count} message angles across {channel_count} channels.

## Angles by Channel

{angles_by_channel}

## Observations

{observations}

## Validation

- Total angles: {angle_count}
- Channels covered: {channel_list}
""",

    "5A": """# Stage 5A: Exploratory Drafts

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete

---

## Summary

Generated {draft_count} drafts from selected angles.

## Selection Rationale

{selection_rationale}

## Drafts by Channel

{drafts_by_channel}

## Observations

- Strongest angles: {strongest}
- Weakest angles: {weakest}
- Cross-channel potential: {cross_channel}
""",

    "4": """# Stage 4: Thread Selection

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete

---

## Summary

Selected winning thread with score {total_score}/40.

## Winning Thread

**Core Message:** {core_message}

**Agitation Register:**
{agitation_register}

**Solution Register:**
{solution_register}

**Selection Rationale:**
{selection_rationale}

**Source Angle:** {source_angle}

## Evaluation Scores

{evaluation_summary}
""",

    "2": """# Stage 2: Channel Strategy

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete  
**Human Review:** {review_status}

---

## Summary

Defined jobs and constraints for {channel_count} channels.

## Thread

{thread_summary}

## Channel Definitions

{channel_definitions}

## Human Review Notes

{review_notes}
""",

    "5B": """# Stage 5B: Constrained Refinement

**Book:** {book_title}  
**Date:** {date}  
**Status:** Complete

---

## Summary

Refined content for {channel_count} channels against constraints.

## Content Blocks

{content_blocks}

## Validation

- All constraints met: {constraints_met}
- Ready for rendering: {ready}

## Issues

{issues}
"""
}

def generate_stage_1_log(stage_data, book_title, output_path):
    """Generate Stage 1 log."""
    
    segments = stage_data.get('segments', [])
    searches = stage_data.get('high_intent_searches', [])
    
    segments_list = "\n".join([
        f"- **{s.get('name', 'Unnamed')}** ({s.get('awareness_stage', '?')}): {s.get('pain_point', 'No pain point')}"
        for s in segments
    ])
    
    searches_list = "\n".join([f"- {s}" for s in searches[:10]])
    
    content = LOG_TEMPLATES["1"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        segment_count=len(segments),
        segments_list=segments_list,
        searches_list=searches_list,
        observations=stage_data.get('observations', 'None'),
        search_count=len(searches)
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 1 log: {output_path}")

def generate_stage_3_log(stage_data, book_title, output_path):
    """Generate Stage 3 log."""
    
    angles = stage_data.get('angles', [])
    
    # Group by channel
    by_channel = {}
    for angle in angles:
        channel = angle.get('channel', 'Unknown')
        if channel not in by_channel:
            by_channel[channel] = []
        by_channel[channel].append(angle)
    
    angles_text = ""
    for channel, channel_angles in sorted(by_channel.items()):
        angles_text += f"\n### {channel.upper()} ({len(channel_angles)} angles)\n\n"
        for i, angle in enumerate(channel_angles, 1):
            angles_text += f"{i}. {angle.get('message', 'No message')[:80]}...\n"
    
    content = LOG_TEMPLATES["3"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        angle_count=len(angles),
        channel_count=len(by_channel),
        angles_by_channel=angles_text,
        observations=stage_data.get('observations', 'None'),
        channel_list=", ".join(sorted(by_channel.keys()))
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 3 log: {output_path}")

def generate_stage_5a_log(stage_data, book_title, output_path):
    """Generate Stage 5A log."""
    
    drafts = stage_data.get('drafts', [])
    selection = stage_data.get('selection_rationale', {})
    obs = stage_data.get('observations', {})
    
    # Selection rationale
    rationale_text = "\n".join([
        f"- **{channel}:** {reason}"
        for channel, reason in selection.items()
    ])
    
    # Group drafts by channel
    by_channel = {}
    for draft in drafts:
        channel = draft.get('channel', 'Unknown')
        if channel not in by_channel:
            by_channel[channel] = []
        by_channel[channel].append(draft)
    
    drafts_text = ""
    for channel, channel_drafts in sorted(by_channel.items()):
        drafts_text += f"\n### {channel.upper()} ({len(channel_drafts)} drafts)\n\n"
        for draft in channel_drafts:
            msg = draft.get('angle_message', 'No message')[:60]
            drafts_text += f"- {msg}...\n"
    
    content = LOG_TEMPLATES["5A"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        draft_count=len(drafts),
        selection_rationale=rationale_text or "None provided",
        drafts_by_channel=drafts_text,
        strongest=", ".join(str(s) for s in obs.get('strongest_angles', ['Not noted'])),
        weakest=", ".join(str(s) for s in obs.get('weakest_angles', ['Not noted'])),
        cross_channel=", ".join(str(s) for s in obs.get('cross_channel_potential', ['Not noted']))
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 5A log: {output_path}")

def generate_stage_4_log(eval_data, thread_data, book_title, output_path):
    """Generate Stage 4 log."""
    
    # Evaluation summary
    evals = eval_data.get('evaluations', [])
    eval_text = ""
    for e in evals[:5]:  # Top 5
        eval_text += f"- {e.get('angle_id', '?')}: {e.get('total_score', 0)}/40\n"
    
    content = LOG_TEMPLATES["4"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        total_score=thread_data.get('total_score', 0),
        core_message=thread_data.get('core_message', 'None'),
        agitation_register=thread_data.get('agitation_register', 'None'),
        solution_register=thread_data.get('solution_register', 'None'),
        selection_rationale=thread_data.get('selection_rationale', 'None'),
        source_angle=thread_data.get('source_angle', 'Unknown'),
        evaluation_summary=eval_text or "No evaluations"
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 4 log: {output_path}")

def generate_stage_2_log(stage_data, book_title, output_path, review_complete=False):
    """Generate Stage 2 log."""
    
    channels = ['social', 'youtube', 'seo', 'guide']
    
    channel_text = ""
    for channel in channels:
        ch_data = stage_data.get(channel, {})
        channel_text += f"\n### {channel.upper()}\n\n"
        channel_text += f"**Job:** {ch_data.get('job', 'Not defined')}\n\n"
        channel_text += f"**Register:** {ch_data.get('register', 'Not defined')}\n\n"
        channel_text += f"**Must Do:**\n"
        for item in ch_data.get('must_do', [])[:3]:
            channel_text += f"- {item}\n"
        channel_text += f"\n**Must Not Do:**\n"
        for item in ch_data.get('must_not_do', [])[:3]:
            channel_text += f"- {item}\n"
    
    content = LOG_TEMPLATES["2"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        review_status="✓ Complete" if review_complete else "⚠ Pending",
        channel_count=len(channels),
        thread_summary=stage_data.get('thread_summary', 'None'),
        channel_definitions=channel_text,
        review_notes="[Add notes after human review]"
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 2 log: {output_path}")

def generate_stage_5b_log(stage_data, book_title, output_path):
    """Generate Stage 5B log."""
    
    blocks = stage_data.get('content_blocks', {})
    validation = stage_data.get('overall_validation', {})
    
    blocks_text = ""
    for channel, block in blocks.items():
        content = block.get('final_content', block.get('content', ''))
        preview = content[:150] if isinstance(content, str) else str(content)[:150]
        blocks_text += f"\n### {channel.upper()}\n\n"
        blocks_text += f"```\n{preview}...\n```\n"
    
    issues = validation.get('issues_found', [])
    issues_text = "\n".join([f"- {i}" for i in issues]) if issues else "None"
    
    content = LOG_TEMPLATES["5B"].format(
        book_title=book_title,
        date=datetime.now().strftime("%Y-%m-%d"),
        channel_count=len(blocks),
        content_blocks=blocks_text,
        constraints_met=validation.get('all_constraints_met', 'Unknown'),
        ready=validation.get('ready_for_rendering', 'Unknown'),
        issues=issues_text
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Stage 5B log: {output_path}")

# Main dispatcher
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_stage_log.py <stage> <input_json> <book_title> [output_path]")
        print("  stage: 1, 3, 5A, 4, 2, or 5B")
        sys.exit(1)
    
    stage = sys.argv[1]
    input_path = sys.argv[2]
    book_title = sys.argv[3]
    output_path = sys.argv[4] if len(sys.argv) > 4 else f"outputs/logs/stage_{stage.lower()}.md"
    
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    if stage == "1":
        generate_stage_1_log(data, book_title, output_path)
    elif stage == "3":
        generate_stage_3_log(data, book_title, output_path)
    elif stage == "5A":
        generate_stage_5a_log(data, book_title, output_path)
    elif stage == "4":
        # Stage 4 needs both eval and thread files
        print("Note: Stage 4 requires separate eval and thread JSON files")
        print("Use generate_stage_4_log() directly with both inputs")
    elif stage == "2":
        generate_stage_2_log(data, book_title, output_path)
    elif stage == "5B":
        generate_stage_5b_log(data, book_title, output_path)
    else:
        print(f"Unknown stage: {stage}")


