#!/bin/bash
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config-gpt5.yaml \
  --run-id gpt5-twophase-full \
  --mode expr \
  --max_workers 4 \
  --agent-type two_phase_agent \
  --instance_ids django__django-11099 django__django-13212 django__django-15277 matplotlib__matplotlib-24177
