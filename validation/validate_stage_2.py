# validation/validate_stage_2.py

import json
import sys

def validate_channel_strategy(channels_path, thread_path):
    """Validate that channel jobs derive from and use the thread."""
    
    with open(channels_path, 'r') as f:
        channels = json.load(f)
    
    with open(thread_path, 'r') as f:
        thread = json.load(f)
    
    print("="*60)
    print("STAGE 2 VALIDATION: Channel Strategy")
    print("="*60)
    
    # Extract thread keywords
    thread_words = set(thread['core_message'].lower().split())
    
    issues = []
    
    for channel, strategy in channels.items():
        print(f"\n{channel.upper()}:")
        print(f"  Job: {strategy['job']}")
        
        # Check: Does job mention thread?
        job_words = set(strategy['job'].lower().split())
        thread_overlap = thread_words & job_words
        
        if len(thread_overlap) > 0:
            print(f"  ✓ Uses thread keywords: {list(thread_overlap)[:3]}")
        else:
            print(f"  ⚠ Job may not use thread")
            issues.append(f"{channel}: Job doesn't clearly use thread")
        
        # Check: Thread usage field
        if 'thread_usage' in strategy:
            print(f"  → Usage: {strategy['thread_usage'][:60]}...")
        else:
            print(f"  ✗ No thread_usage explanation")
        
        # Check: Register specified
        if 'register' in strategy:
            print(f"  Register: {strategy['register']}")
        
        # Check: Constraints exist
        must_do = strategy.get('must_do', [])
        must_not_do = strategy.get('must_not_do', [])
        
        if len(must_do) >= 2:
            print(f"  ✓ {len(must_do)} requirements defined")
        else:
            print(f"  ⚠ Only {len(must_do)} requirement(s)")
            issues.append(f"{channel}: Needs more 'must do' requirements")
        
        if len(must_not_do) >= 2:
            print(f"  ✓ {len(must_not_do)} constraints defined")
        else:
            print(f"  ⚠ Only {len(must_not_do)} constraint(s)")
            issues.append(f"{channel}: Needs more 'must not do' constraints")
        
        # Check: Success metric
        if 'success_metric' in strategy and strategy['success_metric']:
            print(f"  ✓ Success metric: {strategy['success_metric'][:50]}...")
        else:
            print(f"  ✗ No success metric")
    
    # Check: Are jobs different?
    print(f"\n{'='*60}")
    print("DIFFERENTIATION CHECK:")
    print('='*60)
    
    jobs = {channel: strategy['job'] for channel, strategy in channels.items()}
    
    # Simple check: no two jobs identical
    job_list = list(jobs.values())
    if len(job_list) == len(set(job_list)):
        print("✓ All jobs are different")
    else:
        print("✗ Some jobs may be duplicates")
        issues.append("Jobs not sufficiently differentiated")
    
    # Display for manual review
    for channel, job in jobs.items():
        print(f"\n{channel}: {job}")
    
    # Summary
    print(f"\n{'='*60}")
    if issues:
        print("VALIDATION ISSUES:")
        for issue in issues:
            print(f"  • {issue}")
        print("\nStatus: NEEDS REVIEW")
        return False
    else:
        print("✓ BASIC CHECKS PASSED")
        print("\nManual review needed:")
        print("  - Do jobs actually use the thread?")
        print("  - Are jobs meaningfully different?")
        print("  - Can you visualize the funnel flow?")
        return True

# Usage
if __name__ == "__main__":
    channels_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_2/TKAM_stage_2_channels.json"
    thread_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/manual_exploration/phase_2/TKAM_stage_4_thread.json"
    
    validate_channel_strategy(channels_path, thread_path)

