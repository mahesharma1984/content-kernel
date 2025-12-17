# phase_2/stage_4_evaluate.py

import os
import json
import sys
from anthropic import Anthropic

def evaluate_and_select_thread(messages_path, kernel_path, prompt_path, output_path):
    """Evaluate all angles and select winning thread."""
    
    # Load inputs
    with open(messages_path, 'r') as f:
        messages = json.load(f)
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    with open(prompt_path, 'r') as f:
        prompt_template = f.read()
    
    # Fill prompt
    num_angles = len(messages['angles'])
    
    # Extract kernel pattern (v5.1 structure)
    alignment = kernel.get('alignment_pattern', {})
    pattern_name = alignment.get('pattern_name', 'Not found')
    core_dynamic = alignment.get('core_dynamic', 'Not found')
    reader_effect = alignment.get('reader_effect', 'Not found')
    
    kernel_pattern = f"Pattern: {pattern_name}\nCore Dynamic: {core_dynamic}\nReader Effect: {reader_effect}"
    
    prompt = prompt_template.format(
        num_angles=num_angles,
        json_of_all_angles=json.dumps(messages['angles'], indent=2),
        kernel_pattern=kernel_pattern
    )
    
    # Call Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    print("Calling Claude API for Stage 4: Thread Selection...")
    print(f"Evaluating {num_angles} angles...")
    print("(This may take 90-120 seconds)\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=0.5,  # Lower temp for evaluation
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            json_text = response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            json_text = response_text[start:end].strip()
        else:
            json_text = response_text.strip()
        
        # Try to find JSON object if not in code block
        if not json_text.startswith('{'):
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
        
        try:
            evaluations = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON")
            print(f"JSONDecodeError: {e}")
            with open(f"{output_path}.raw", 'w') as f:
                f.write(response_text)
            raise e
        
        # Save full evaluation
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(evaluations, f, indent=2)
        
        print(f"✓ Evaluations saved to: {output_path}")
        
        # Display winner
        winner = evaluations['winner']
        print(f"\n{'='*60}")
        print("WINNING THREAD:")
        print('='*60)
        print(f"\nMessage: {winner['core_message']}")
        print(f"Total Score: {winner['total_score']}/40")
        print(f"\nAgitation: {winner['agitation_register'][:80]}...")
        print(f"\nSolution: {winner['solution_register'][:80]}...")
        print(f"\nWhy it wins: {winner['why_it_wins'][:150]}...")
        
        return evaluations
        
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        print("Check:")
        print("  1. ANTHROPIC_API_KEY is set")
        print("  2. Prompt length < 100k tokens")
        print("  3. Internet connection working")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    messages_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/manual_exploration/phase_1/TKAM_stage_3_messages.json"
    kernel_path = sys.argv[2] if len(sys.argv) > 2 else "To_Kill_a_Mockingbird_kernel_v5_1.json"
    prompt_path = sys.argv[3] if len(sys.argv) > 3 else "prompts/phase_2/stage_4_selection.txt"
    output_path = sys.argv[4] if len(sys.argv) > 4 else "outputs/manual_exploration/phase_2/TKAM_stage_4_evaluations.json"
    
    evaluations = evaluate_and_select_thread(messages_path, kernel_path, prompt_path, output_path)
