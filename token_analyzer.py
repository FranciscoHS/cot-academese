"""
token_analyzer.py - Fixed version that analyzes each budget separately

Helper script to analyze thinking blocks in Claude output files and provide
token counts for manual annotation, separated by budget.

Usage:
    python token_analyzer.py <filename>
    python token_analyzer.py results_20251121_143022/problem_1_*.txt

Requirements:
    pip install tiktoken
"""

import tiktoken
import re
import sys
import glob

def count_tokens(text):
    """Count tokens using Claude's tokenizer (cl100k_base)"""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def find_text_position(full_text, search_text):
    """Find token position of a specific piece of text"""
    encoding = tiktoken.get_encoding("cl100k_base")
    
    char_pos = full_text.lower().find(search_text.lower())
    if char_pos == -1:
        return None
    
    text_before = full_text[:char_pos]
    return len(encoding.encode(text_before))

def analyze_thinking_file(filename):
    """Extract thinking blocks and provide detailed token analysis per budget"""
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filename}")
        return
    
    # Extract problem metadata
    problem_match = re.search(r'PROBLEM (\d+) - ID: (\w+), Type: ([\w_]+)', content)
    if problem_match:
        prob_num, prob_id, prob_type = problem_match.groups()
    else:
        prob_num = prob_id = prob_type = "Unknown"
    
    print("\n" + "="*70)
    print(f"ANALYZING FILE: {filename}")
    print(f"Problem {prob_num} (ID: {prob_id}) - Type: {prob_type}")
    print("="*70)
    
    # Split by budget sections
    budget_sections = re.split(r'={70}\nTHINKING BUDGET: (\d+) tokens\n={70}', content)
    
    # First element is the header, then alternating budget/content pairs
    if len(budget_sections) < 3:
        print("ERROR: Could not find budget sections in file")
        return
    
    # Process each budget section
    for i in range(1, len(budget_sections), 2):
        if i >= len(budget_sections) - 1:
            break
            
        budget = budget_sections[i]
        section_content = budget_sections[i + 1]
        
        # Extract thinking blocks from this section
        thinking_pattern = r'\[Thinking block \d+\](.*?)(?=\[Thinking block|\-\-\- VISIBLE RESPONSE|\-\-\- TOKEN USAGE|$)'
        thinking_blocks = re.findall(thinking_pattern, section_content, re.DOTALL)
        
        if not thinking_blocks:
            print(f"\nBudget {budget}: No thinking blocks found")
            continue
        
        # Combine all thinking
        full_thinking = "\n\n".join(block.strip() for block in thinking_blocks)
        
        # Analysis
        print("\n" + "-"*70)
        print(f"BUDGET: {budget} tokens")
        print("-"*70)
        
        total_tokens = 0
        block_info = []
        
        for j, block in enumerate(thinking_blocks, 1):
            block = block.strip()
            tokens = count_tokens(block)
            block_info.append({
                'num': j,
                'tokens': tokens,
                'cumulative': total_tokens + tokens,
                'preview': block[:80].replace('\n', ' ')
            })
            total_tokens += tokens
        
        # Print block summary
        print("\nThinking Blocks:")
        for info in block_info:
            print(f"  Block {info['num']}: {info['tokens']:4d} tokens (cumulative: {info['cumulative']:4d})")
            print(f"    Preview: {info['preview']}...")
        
        print(f"\n  TOTAL THINKING TOKENS: {total_tokens}")
        
        # Percentage markers
        print("\n  Annotation markers:")
        print(f"    10% mark: ~{int(total_tokens * 0.10):4d} tokens")
        print(f"    25% mark: ~{int(total_tokens * 0.25):4d} tokens")
        print(f"    50% mark: ~{int(total_tokens * 0.50):4d} tokens")
        print(f"    75% mark: ~{int(total_tokens * 0.75):4d} tokens")
        print(f"    90% mark: ~{int(total_tokens * 0.90):4d} tokens")
    
    print("\n" + "="*70)

def main():
    if len(sys.argv) < 2:
        print("Usage: python token_analyzer.py <filename>")
        print("Example: python token_analyzer.py results_*/problem_1_*.txt")
        sys.exit(1)
    
    # Handle glob patterns
    pattern = sys.argv[1]
    files = glob.glob(pattern)
    
    if not files:
        print(f"No files matching pattern: {pattern}")
        sys.exit(1)
    
    for filename in files:
        analyze_thinking_file(filename)
        if len(files) > 1:
            print("\n" + "#"*70 + "\n")

if __name__ == "__main__":
    main()