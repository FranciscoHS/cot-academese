import anthropic
import json
from datetime import datetime
import os
import re

# Configuration
input_file = 'selected_aime_problems.json'
max_tokens_settings = [2000, 4000, 8000]
num_trials = 10  # Number of repetitions per budget

# Load selected problems and take just the first one
print("Loading AIME problem...")
with open(input_file, 'r') as f:
    all_problems = json.load(f)
    problem = all_problems[0]  # Just use first problem

print(f"Testing single problem: {problem['id']}")
print(f"Running {num_trials} trials per budget level")

# Build prompt for single problem
prompt = f"""CRITICAL: Your response MUST contain ONLY the answer as a single integer. NO explanations, NO working, NO text before or after.

Solve the following AIME problem. The answer is an integer from 0 to 999.

PROBLEM:
{problem['input']}

===== RESPONSE FORMAT =====
Your response MUST be EXACTLY in this format with NOTHING else:

1: [integer]

FORBIDDEN:
- Do NOT explain your reasoning
- Do NOT add any other text
- Do NOT use markdown formatting

ONLY "1: [integer]". Nothing more.

All your working and reasoning should go in your thinking/chain-of-thought, NOT in the final response.
"""

print(f"\n{'='*70}")
print(f"TESTING SINGLE PROBLEM - MULTIPLE TRIALS")
print(f"{'='*70}")

# Initialize Anthropic client
client = anthropic.Anthropic()

# Generate timestamp for output files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"results_multi_trial_{timestamp}"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Create summary file
summary_filename = f"{output_dir}/summary_{timestamp}.txt"

def extract_answer(text):
    """Extract answer in format '1: answer' """
    pattern = r"^1:\s*(\d+)"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return int(match.group(1))
    return None

with open(summary_filename, 'w', encoding='utf-8') as summary_file:
    summary_file.write("="*70 + "\n")
    summary_file.write(f"MULTI-TRIAL TEST - {num_trials} TRIALS PER BUDGET\n")
    summary_file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    summary_file.write("="*70 + "\n\n")
    
    summary_file.write("PROBLEM AND CORRECT ANSWER:\n")
    summary_file.write("-"*70 + "\n")
    summary_file.write(f"Problem ID: {problem['id']}\n")
    summary_file.write(f"Question: {problem['input']}\n")
    summary_file.write(f"Correct Answer: {problem['target']}\n")
    
    summary_file.write("\n" + "="*70 + "\n")
    summary_file.write("FILE ORGANIZATION:\n")
    summary_file.write("-"*70 + "\n")
    summary_file.write("Individual trial CoT saved to: trial_[budget]_[trial_num].txt\n")
    summary_file.write("This file contains: summary statistics only\n")
    
    # Store all results
    all_results = {budget: [] for budget in max_tokens_settings}
    
    # Test each max_tokens setting with multiple trials
    for max_tok in max_tokens_settings:
        budget = max_tok - 100  # Leave 100 tokens for response
        
        # Create subdirectory for this budget
        budget_dir = f"{output_dir}/budget_{max_tok}"
        os.makedirs(budget_dir, exist_ok=True)
        
        summary_file.write("\n" + "="*70 + "\n")
        summary_file.write(f"BUDGET: max_tokens={max_tok}, budget_tokens={budget}\n")
        summary_file.write("="*70 + "\n\n")
        
        print(f"\n{'='*70}")
        print(f"Budget: max_tokens={max_tok}, budget_tokens={budget}")
        print(f"{'='*70}")
        
        for trial in range(1, num_trials + 1):
            print(f"  Trial {trial}/{num_trials}...", end=" ")
            
            trial_filename = f"{budget_dir}/trial_{max_tok}_{trial}.txt"
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tok,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": budget
                    },
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Save full trial details to individual file
                with open(trial_filename, 'w', encoding='utf-8') as trial_file:
                    trial_file.write("="*70 + "\n")
                    trial_file.write(f"TRIAL {trial} - Budget: max_tokens={max_tok}, budget_tokens={budget}\n")
                    trial_file.write("="*70 + "\n\n")
                    
                    # Write full thinking blocks
                    thinking_blocks = [block.thinking for block in response.content if block.type == "thinking"]
                    if thinking_blocks:
                        trial_file.write("--- CHAIN OF THOUGHT ---\n")
                        trial_file.write("-"*70 + "\n")
                        for i, thinking in enumerate(thinking_blocks, 1):
                            trial_file.write(f"[Thinking block {i}]\n")
                            trial_file.write(thinking + "\n\n")
                    else:
                        trial_file.write("--- NO THINKING BLOCKS ---\n\n")
                    
                    # Write response
                    response_text_full = ""
                    response_text = [block.text for block in response.content if block.type == "text"]
                    trial_file.write("--- VISIBLE RESPONSE ---\n")
                    trial_file.write("-"*70 + "\n")
                    if response_text:
                        for text in response_text:
                            response_text_full += text
                            trial_file.write(text + "\n")
                    else:
                        trial_file.write("[NONE]\n")
                    
                    # Write metadata
                    trial_file.write("\n--- METADATA ---\n")
                    trial_file.write("-"*70 + "\n")
                    trial_file.write(f"Output tokens: {response.usage.output_tokens}\n")
                    trial_file.write(f"Stop reason: {response.stop_reason}\n")
                
                # Extract answer and check correctness
                response_text_full = ""
                response_text = [block.text for block in response.content if block.type == "text"]
                if response_text:
                    for text in response_text:
                        response_text_full += text
                
                extracted = extract_answer(response_text_full)
                correct_answer = int(problem['target'])
                is_correct = (extracted == correct_answer) if extracted is not None else False
                
                thinking_blocks = [block.thinking for block in response.content if block.type == "thinking"]
                total_thinking_chars = sum(len(t) for t in thinking_blocks)
                
                # Write brief summary to summary file
                summary_file.write(f"Trial {trial}: ")
                summary_file.write(f"{'✓' if is_correct else '✗'} ")
                summary_file.write(f"Extracted={extracted}, ")
                summary_file.write(f"Tokens={response.usage.output_tokens}, ")
                summary_file.write(f"Stop={response.stop_reason}\n")
                
                # Store result
                all_results[max_tok].append({
                    'trial': trial,
                    'correct': is_correct,
                    'extracted': extracted,
                    'output_tokens': response.usage.output_tokens,
                    'stop_reason': response.stop_reason,
                    'thinking_chars': total_thinking_chars,
                    'filename': trial_filename
                })
                
                print(f"{'✓' if is_correct else '✗'} {response.usage.output_tokens} tokens")
                
            except Exception as e:
                # Save error to individual file
                with open(trial_filename, 'w', encoding='utf-8') as trial_file:
                    trial_file.write("="*70 + "\n")
                    trial_file.write(f"TRIAL {trial} - Budget: max_tokens={max_tok}, budget_tokens={budget}\n")
                    trial_file.write("="*70 + "\n\n")
                    trial_file.write(f"ERROR: {str(e)}\n")
                
                summary_file.write(f"Trial {trial}: ERROR - {str(e)}\n")
                print(f"ERROR: {str(e)}")
                
                all_results[max_tok].append({
                    'trial': trial,
                    'correct': False,
                    'extracted': None,
                    'error': str(e),
                    'filename': trial_filename
                })
    
    # Write summary statistics
    summary_file.write("\n" + "="*70 + "\n")
    summary_file.write("SUMMARY STATISTICS\n")
    summary_file.write("="*70 + "\n\n")
    
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}")
    
    for max_tok in max_tokens_settings:
        results = all_results[max_tok]
        budget = max_tok - 100
        
        # Calculate statistics
        successful_trials = [r for r in results if 'error' not in r]
        correct_trials = [r for r in successful_trials if r['correct']]
        
        success_rate = len(correct_trials) / len(results) if results else 0
        avg_tokens = sum(r['output_tokens'] for r in successful_trials) / len(successful_trials) if successful_trials else 0
        min_tokens = min((r['output_tokens'] for r in successful_trials), default=0)
        max_tokens_used = max((r['output_tokens'] for r in successful_trials), default=0)
        
        summary_file.write(f"Budget: max_tokens={max_tok}, budget_tokens={budget}\n")
        summary_file.write(f"  Success rate: {len(correct_trials)}/{len(results)} = {success_rate:.1%}\n")
        summary_file.write(f"  Avg output tokens: {avg_tokens:.1f}\n")
        summary_file.write(f"  Token range: [{min_tokens}, {max_tokens_used}]\n")
        summary_file.write(f"  Individual results: {['✓' if r.get('correct') else '✗' for r in results]}\n")
        summary_file.write(f"  Files saved to: budget_{max_tok}/trial_{max_tok}_[1-{num_trials}].txt\n")
        summary_file.write("\n")
        
        print(f"Budget: max_tokens={max_tok}, budget_tokens={budget}")
        print(f"  Success rate: {len(correct_trials)}/{len(results)} = {success_rate:.1%}")
        print(f"  Avg output tokens: {avg_tokens:.1f}")
        print(f"  Token range: [{min_tokens}, {max_tokens_used}]")
        print(f"  Individual: {' '.join(['✓' if r.get('correct') else '✗' for r in results])}")
        print()
    
    summary_file.write("="*70 + "\n")
    summary_file.write("END OF SUMMARY\n")
    summary_file.write("="*70 + "\n")

print(f"\nResults saved to: {output_dir}/")
print(f"  Summary: {summary_filename}")
print(f"  Individual trials: budget_[tokens]/trial_[tokens]_[num].txt")
print(f"{'='*70}")