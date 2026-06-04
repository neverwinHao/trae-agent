#!/bin/bash
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config-opus.yaml \
  --run-id opus-twophase-full \
  --mode expr \
  --max_workers 4 \
  --agent-type two_phase_agent
