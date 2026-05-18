#!/bin/bash
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id gpt5mini-twophase-test \
  --mode expr \
  --max_workers 1 \
  --agent-type two_phase_agent \
  --instance_ids astropy__astropy-12907
