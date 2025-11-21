# cot-academese

Repo supporting https://ffsilva.io/academese-cot/

## What this is

- Runs Claude Sonnet on mock AIME problems with different thinking budgets
- Logs:
  - success/fail on a fixed problem
  - how many tokens it actually used
  - what the visible CoT looks like
- Used to check whether the “academese phase” is:
  - real thinking getting better (faithfulness drop), or
  - actual reasoning degradation

## Files

- `script.py` — main experiment runner
- `script_legacy_sonnet.py` — version for Sonnet 3.7, single run
- `mock_aime_data.json` / `selected_aime_problems.json` — preprocessed AIME data (from Evan Chen’s mocks)
- `sample_dataset.py` — sample some subset of problems in dataset, filters for image-free problems
- `results_*` / `test_*` dirs — saved runs

## How to use

1. Run `sample_dataset.py`
2. Set your Anthropic key: `export ANTHROPIC_API_KEY=...`
3. Pick a model / budgets / trial counts at the top of `script.py`.
4. Run: `python script.py`

