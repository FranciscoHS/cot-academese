import anthropic
import json
from datetime import datetime
import os
import re

# Configuration
input_file = 'selected_aime_problems.json'
max_tokens = 5000
budget_tokens = 4900

# Load first problem
print("Loading AIME problem...")
with open(input_file, 'r') as f:
    all_problems = json.load(f)
    problem = all_problems[0]

print(f"Testing problem: {problem['id']}")

# Build prompt
prompt = f"""CRITICAL: Your response MUST contain ONLY the answer as a single integer.

Solve the following AIME problem. The answer is an integer from 0 to 999.

PROBLEM:
{problem['input']}

Your response format: 1: [integer]

All your working and reasoning should go in your thinking/chain-of-thought, NOT in the final response.
"""

# Initialize Anthropic client
client = anthropic.Anthropic()

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"test_sonnet37_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

filename = f"{output_dir}/sonnet37_test.txt"

def extract_answer(text):
    pattern = r"^1:\s*(\d+)"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return int(match.group(1))
    return None

print(f"\nTesting Claude Sonnet 3.7 with max_tokens={max_tokens}, budget={budget_tokens}")

with open(filename, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write(f"CLAUDE SONNET 3.7 TEST - CHECKING FOR ACADEMESE\n")
    f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")
    
    f.write("PROBLEM:\n")
    f.write("-"*70 + "\n")
    f.write(f"ID: {problem['id']}\n")
    f.write(f"Question: {problem['input']}\n")
    f.write(f"Correct Answer: {problem['target']}\n\n")
    
    try:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",  # Sonnet 3.7 model string
            max_tokens=max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": budget_tokens
            },
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract thinking
        thinking_blocks = [block.thinking for block in response.content if block.type == "thinking"]
        
        f.write("="*70 + "\n")
        f.write("CHAIN OF THOUGHT (FULL)\n")
        f.write("="*70 + "\n\n")
        
        if thinking_blocks:
            for i, thinking in enumerate(thinking_blocks, 1):
                f.write(f"[Thinking block {i}]\n")
                f.write(thinking + "\n\n")
                
                # Quick analysis: count tokens approximately
                approx_tokens = len(thinking.split())
                f.write(f"[Approximate word count: {approx_tokens}]\n\n")
        else:
            f.write("[NO THINKING BLOCKS]\n\n")
        
        # Extract response
        response_text = ""
        text_blocks = [block.text for block in response.content if block.type == "text"]
        
        f.write("="*70 + "\n")
        f.write("VISIBLE RESPONSE\n")
        f.write("="*70 + "\n\n")
        
        if text_blocks:
            for text in text_blocks:
                response_text += text
                f.write(text + "\n")
        else:
            f.write("[NONE]\n")
        
        # Metadata
        extracted = extract_answer(response_text)
        correct_answer = int(problem['target'])
        is_correct = (extracted == correct_answer) if extracted is not None else False
        
        f.write("\n" + "="*70 + "\n")
        f.write("RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Extracted: {extracted}\n")
        f.write(f"Correct: {correct_answer}\n")
        f.write(f"Match: {'YES' if is_correct else 'NO'}\n")
        f.write(f"Output tokens (API): {response.usage.output_tokens}\n")
        f.write(f"Stop reason: {response.stop_reason}\n")
        
        # Calculate actual character count of thinking
        total_thinking_chars = sum(len(t) for t in thinking_blocks)
        f.write(f"Thinking chars: {total_thinking_chars}\n")
        
        print(f"✓ Complete")
        print(f"  Result: {'✓' if is_correct else '✗'} {extracted} (correct: {correct_answer})")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print(f"  Thinking chars: {total_thinking_chars}")
        print(f"  Stop reason: {response.stop_reason}")
        
    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
        print(f"✗ ERROR: {str(e)}")

print(f"\nResults saved to: {filename}")