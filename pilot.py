import anthropic
import json
from datetime import datetime
import os

# Configuration
input_file = 'selected_two_problems.json'
thinking_budgets = [2000, 5000]

# Load selected problems
print("Loading selected problems...")
with open(input_file, 'r') as f:
    problems = json.load(f)

if len(problems) != 2:
    print(f"ERROR: Expected 2 problems, found {len(problems)}")
    exit(1)

print(f"Loaded {len(problems)} problems")

# Initialize Anthropic client
client = anthropic.Anthropic()

# Generate timestamp for output files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"results_two_problems_{timestamp}"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Create combined prompt
combined_prompt = f"""Please solve both of the following problems:

PROBLEM 1:
{problems[0]['question']}

PROBLEM 2:
{problems[1]['question']}

Provide complete solutions for both problems."""

print(f"\n{'='*70}")
print(f"TESTING TWO-PROBLEM SETUP")
print(f"Problem 1 ID: {problems[0].get('problem_id', 'unknown')}, Type: {problems[0].get('question_type', 'unknown')}")
print(f"Problem 2 ID: {problems[1].get('problem_id', 'unknown')}, Type: {problems[1].get('question_type', 'unknown')}")
print(f"{'='*70}")

# Create output file
filename = f"{output_dir}/two_problems_{timestamp}.txt"

with open(filename, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("TWO-PROBLEM COMBINED TEST\n")
    f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")
    
    f.write("PROBLEM 1:\n")
    f.write("-"*70 + "\n")
    f.write(f"ID: {problems[0].get('problem_id', 'unknown')}\n")
    f.write(f"Type: {problems[0].get('question_type', 'unknown')}\n")
    f.write(f"Question: {problems[0]['question']}\n\n")
    f.write(f"Reference Solution: {problems[0]['solution']}\n\n")
    f.write(f"Expected Answer: {problems[0].get('answer_val', 'N/A')}\n\n")
    
    f.write("PROBLEM 2:\n")
    f.write("-"*70 + "\n")
    f.write(f"ID: {problems[1].get('problem_id', 'unknown')}\n")
    f.write(f"Type: {problems[1].get('question_type', 'unknown')}\n")
    f.write(f"Question: {problems[1]['question']}\n\n")
    f.write(f"Reference Solution: {problems[1]['solution']}\n\n")
    f.write(f"Expected Answer: {problems[1].get('answer_val', 'N/A')}\n\n")
    
    f.write("COMBINED PROMPT:\n")
    f.write("-"*70 + "\n")
    f.write(combined_prompt + "\n\n")
    
    # Test each thinking budget
    for budget in thinking_budgets:
        print(f"\nRunning with budget: {budget} tokens...")
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": budget
                },
                messages=[{"role": "user", "content": combined_prompt}]
            )
            
            f.write("="*70 + "\n")
            f.write(f"THINKING BUDGET: {budget} tokens\n")
            f.write("="*70 + "\n\n")
            
            # Extract and write thinking blocks
            thinking_blocks = [block.thinking for block in response.content if block.type == "thinking"]
            if thinking_blocks:
                f.write("--- CHAIN OF THOUGHT ---\n")
                f.write("-"*70 + "\n")
                for i, thinking in enumerate(thinking_blocks, 1):
                    f.write(f"[Thinking block {i}]\n{thinking}\n\n")
            
            # Extract and write text response
            response_text = [block.text for block in response.content if block.type == "text"]
            if response_text:
                f.write("--- VISIBLE RESPONSE ---\n")
                f.write("-"*70 + "\n")
                for text in response_text:
                    f.write(text + "\n")
            
            # Token usage
            f.write("\n--- TOKEN USAGE ---\n")
            f.write(f"Input tokens: {response.usage.input_tokens}\n")
            f.write(f"Output tokens: {response.usage.output_tokens}\n")
            f.write(f"\n")
            
            print(f"  Tokens used - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")
            
        except Exception as e:
            f.write(f"\nERROR with budget {budget}: {str(e)}\n\n")
            print(f"  ERROR: {str(e)}")
        
        f.write("\n" + "="*70 + "\n\n")
    
    f.write("="*70 + "\n")
    f.write("END OF TEST\n")
    f.write("="*70 + "\n")

print(f"\nResults saved to: {filename}")
print(f"\n{'='*70}")
print("TEST COMPLETED")
print(f"{'='*70}")