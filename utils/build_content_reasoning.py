# utils/build_content_reasoning.py
# Version: 1.0
# Date: December 17, 2025

import json
import os
import sys
from datetime import datetime

REASONING_TEMPLATE = """## 1. Thread Selection

**Core Message**: {core_message}

**Why This Thread**: {selection_rationale}

**Source Angle**: {source_angle}

**Kernel Connection**: {kernel_pattern_reference}

## 2. Channel Strategy

**Social**: {social_job}
- Register: {social_register}
- Must do: {social_must_do}
- Must not: {social_must_not}

**YouTube**: {youtube_job}
- Register: {youtube_register}
- Must do: {youtube_must_do}
- Must not: {youtube_must_not}

**SEO**: {seo_job}
- Register: {seo_register}
- Must do: {seo_must_do}
- Must not: {seo_must_not}

**Guide**: {guide_job}
- Register: {guide_register}
- Must do: {guide_must_do}
- Must not: {guide_must_not}

## 3. Content Summary

**Social**: {social_preview}

**YouTube**: {youtube_preview}

**SEO**: {seo_preview}

**Guide**: {guide_preview}

## 4. Derivation Summary

This content strategy derives from the **{pattern_name}** pattern identified in the text kernel.

**Thread ← Pattern**: The core message "{core_message_short}" directly translates the pattern's core dynamic into audience-facing language.

**Agitation Register**: {agitation_register}

**Solution Register**: {solution_register}

Each channel adapts this thread to its platform constraints while maintaining derivation from the source kernel.
"""

def extract_pattern_name(thread):
    """Extract pattern name from thread data."""
    # Try to find "Maturing Moral Witness" or similar pattern names
    solution_register = thread.get('solution_register', '')
    kernel_ref = thread.get('kernel_pattern_reference', '')
    
    # Look for common pattern name patterns
    import re
    pattern_match = re.search(r'(\w+(?:\s+\w+){1,3})\s+pattern', solution_register + ' ' + kernel_ref, re.IGNORECASE)
    if pattern_match:
        return pattern_match.group(1)
    
    # Fallback: try splitting kernel_pattern_reference
    if ':' in kernel_ref:
        return kernel_ref.split(':')[0].strip()
    
    # Last resort: return a shortened version
    if len(kernel_ref) > 50:
        return kernel_ref[:50] + "..."
    
    return kernel_ref if kernel_ref else "Unknown"

def build_content_reasoning(content_kernel_path, output_path):
    """Build reasoning doc from content kernel."""
    
    with open(content_kernel_path, 'r') as f:
        kernel = json.load(f)
    
    thread = kernel.get('thread', {})
    channels = kernel.get('channels', {})
    blocks = kernel.get('content_blocks', {})
    
    def get_preview(channel):
        block = blocks.get(channel, blocks.get(channel.capitalize(), {}))
        content = block.get('final_content', block.get('content', ''))
        if isinstance(content, str):
            return content[:150] + "..." if len(content) > 150 else content
        return str(content)[:150] + "..."
    
    def format_list(items):
        if not items:
            return "None specified"
        return ", ".join(items[:3])
    
    content = REASONING_TEMPLATE.format(
        core_message=thread.get('core_message', 'Not defined'),
        selection_rationale=thread.get('selection_rationale', 'Not provided'),
        source_angle=thread.get('source_angle', 'Unknown'),
        kernel_pattern_reference=thread.get('kernel_pattern_reference', 'Not specified'),
        
        social_job=channels.get('social', {}).get('job', 'Not defined'),
        social_register=channels.get('social', {}).get('register', 'Not defined'),
        social_must_do=format_list(channels.get('social', {}).get('must_do', [])),
        social_must_not=format_list(channels.get('social', {}).get('must_not_do', [])),
        
        youtube_job=channels.get('youtube', {}).get('job', 'Not defined'),
        youtube_register=channels.get('youtube', {}).get('register', 'Not defined'),
        youtube_must_do=format_list(channels.get('youtube', {}).get('must_do', [])),
        youtube_must_not=format_list(channels.get('youtube', {}).get('must_not_do', [])),
        
        seo_job=channels.get('seo', {}).get('job', 'Not defined'),
        seo_register=channels.get('seo', {}).get('register', 'Not defined'),
        seo_must_do=format_list(channels.get('seo', {}).get('must_do', [])),
        seo_must_not=format_list(channels.get('seo', {}).get('must_not_do', [])),
        
        guide_job=channels.get('guide', {}).get('job', 'Not defined'),
        guide_register=channels.get('guide', {}).get('register', 'Not defined'),
        guide_must_do=format_list(channels.get('guide', {}).get('must_do', [])),
        guide_must_not=format_list(channels.get('guide', {}).get('must_not_do', [])),
        
        social_preview=get_preview('social'),
        youtube_preview=get_preview('youtube'),
        seo_preview=get_preview('seo'),
        guide_preview=get_preview('guide'),
        
        pattern_name=extract_pattern_name(thread),
        core_message_short=thread.get('core_message', '')[:60] + "..." if len(thread.get('core_message', '')) > 60 else thread.get('core_message', ''),
        agitation_register=thread.get('agitation_register', 'Not defined'),
        solution_register=thread.get('solution_register', 'Not defined')
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Reasoning doc: {output_path}")

if __name__ == "__main__":
    book_code = sys.argv[1] if len(sys.argv) > 1 else "TKAM"
    
    content_kernel_path = f"outputs/kernels/{book_code}_content_kernel_v1_0.json"
    output_path = f"outputs/kernels/{book_code}_content_reasoning_v1_0.md"
    
    # Allow override
    if len(sys.argv) > 2:
        content_kernel_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    
    build_content_reasoning(content_kernel_path, output_path)

