import anthropic
from datetime import datetime
import os

# Configuration
thinking_budgets = [1024, 2048]

# Problem definition
question = """In a 3 × 3 grid, each cell is empty or contains a penguin. Two penguins
are angry at each other if they occupy diagonally adjacent cells. Compute the number
of ways to fill the grid so that none of the penguins are angry."""

correct_answer = 119

# Create prompt using Epoch's format
prompt = f"""Please solve this AIME problem step by step. The answer is an integer ranging from 000 to 999, inclusive.
{question}
Remember to show your work clearly and end with 'ANSWER: X' where X is your final numerical answer."""

print(f"\n{'='*70}")
print(f"TESTING AIME PROBLEM - Penguin Grid")
print(f"Correct answer: {correct_answer}")
print(f"{'='*70}")

# Initialize Anthropic client
client = anthropic.Anthropic()

# Generate timestamp for output files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"results_aime_{timestamp}"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Create output file
filename = f"{output_dir}/penguin_grid_{timestamp}.txt"

with open(filename, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("AIME PROBLEM: PENGUIN GRID\n")
    f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")
    
    f.write("PROBLEM:\n")
    f.write("-"*70 + "\n")
    f.write(question + "\n\n")
    
    f.write("CORRECT ANSWER:\n")
    f.write("-"*70 + "\n")
    f.write(f"{correct_answer}\n\n")
    
    f.write("PROMPT:\n")
    f.write("-"*70 + "\n")
    f.write(prompt + "\n\n")
    
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
                messages=[{"role": "user", "content": prompt}]
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