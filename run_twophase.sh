#!/bin/bash
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id gpt5mini-twophase-full-run2 \
  --mode expr \
  --max_workers 4 \
  --agent-type two_phase_agent


python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id gpt5mini-twophase-full-run3 \
  --mode expr \
  --max_workers 4 \
  --agent-type two_phase_agent

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id gpt5mini-twophase-full-run4 \
  --mode expr \
  --max_workers 4 \
  --agent-type two_phase_agent