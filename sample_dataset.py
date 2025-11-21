import json
import random

# Load dataset
input_file = 'mock_aime_data.json'
output_file = 'selected_aime_problems.json'

print("Loading AIME dataset...")
with open(input_file, 'r') as f:
    data = json.load(f)

print(f"Total problems in dataset: {len(data)}")

# Filter out problems with images
problems_without_images = [p for p in data if p['image'] is None]
print(f"Problems without images: {len(problems_without_images)}")

# Sample 5 problems
n_samples = 5
if len(problems_without_images) < n_samples:
    print(f"WARNING: Only {len(problems_without_images)} problems available, sampling all")
    selected = problems_without_images
else:
    selected = random.sample(problems_without_images, n_samples)

# Save selected problems
print("\n" + "="*70)
print("SELECTED PROBLEMS")
print("="*70)

for i, problem in enumerate(selected, 1):
    print(f"\nProblem {i} [ID: {problem['id']}]:")
    print(f"  Question: {problem['input'][:100]}...")
    print(f"  Answer: {problem['target']}")

with open(output_file, 'w') as f:
    json.dump(selected, f, indent=2)

print(f"\n{len(selected)} problems saved to: {output_file}")