#!/bin/bash
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id gpt5mini-experiment-hao \
  --mode expr \
  --max_workers 4 \
  --instance_ids astropy__astropy-12907
