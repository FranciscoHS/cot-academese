import json
import random
from collections import Counter

# Load dataset
input_file = 'HARDMath_mini.json'
output_file = 'selected_two_problems.json'

print("Loading dataset...")
with open(input_file, 'r') as f:
    data_dict = json.load(f)

# Convert to list of problems (with IDs preserved)
data = []
for problem_id, problem in data_dict.items():
    problem['problem_id'] = problem_id
    data.append(problem)

print(f"Total problems in dataset: {len(data)}")

# Explore question_type distribution
print("\n" + "="*70)
print("QUESTION TYPE DISTRIBUTION")
print("="*70)

question_types = [problem.get('question_type', 'unknown') for problem in data]
type_counts = Counter(question_types)

for qtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {qtype}: {count} problems")

# Group by question_type
types = {}
for problem in data:
    qtype = problem.get('question_type', 'unknown')
    if qtype not in types:
        types[qtype] = []
    types[qtype].append(problem)

# Sample 2 problems - try to get different types if possible
print("\n" + "="*70)
print("SAMPLING STRATEGY")
print("="*70)

n_samples = 2
n_types = len(types)

if n_types >= n_samples:
    # Sample 1 from each of two different types
    most_common_types = [qtype for qtype, _ in type_counts.most_common(n_samples)]
    selected = []
    for qtype in most_common_types:
        problem = random.choice(types[qtype])
        selected.append(problem)
        print(f"Selected 1 problem from type: {qtype} (ID: {problem['problem_id']})")
else:
    # Just sample 2 random problems
    selected = random.sample(data, n_samples)
    for p in selected:
        print(f"Selected problem ID: {p['problem_id']}, type: {p.get('question_type', 'unknown')}")

# Save selected problems
print("\n" + "="*70)
print("SAVING SELECTED PROBLEMS")
print("="*70)

with open(output_file, 'w') as f:
    json.dump(selected, f, indent=2)

print(f"Saved {len(selected)} problems to: {output_file}")

# Print summary
print("\n" + "="*70)
print("SELECTED PROBLEMS SUMMARY")
print("="*70)

for i, problem in enumerate(selected, 1):
    qtype = problem.get('question_type', 'unknown')
    prob_id = problem.get('problem_id', 'unknown')
    question = problem.get('question', '')[:100] + '...' if len(problem.get('question', '')) > 100 else problem.get('question', '')
    print(f"\nProblem {i} [ID: {prob_id}, Type: {qtype}]:")
    print(f"  Question: {question}")