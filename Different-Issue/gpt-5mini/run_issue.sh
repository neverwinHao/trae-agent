#!/bin/bash
# Run trae-agent two-phase pipeline with a specific issue style
# Usage: bash run_issue.sh <style> [max_workers]
# Styles: simple, standard, dropCode, initPatch, initTest

STYLE=${1:?"Usage: bash run_issue.sh <style> [max_workers]"}
MAX_WORKERS=${2:-4}

cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

INSTANCES_FILE="Different-Issue/prepared_data/swtbench_${STYLE}.json"
OUTPUT_RUN_ID="gpt5mini-twophase-issue-${STYLE}"

if [ ! -f "$INSTANCES_FILE" ]; then
    echo "Instances file not found: $INSTANCES_FILE"
    echo "Run 'python Different-Issue/prepare_generated_issues.py' first."
    exit 1
fi

echo "=== Running trae-agent two-phase with issue style: ${STYLE} ==="
echo "Instances file: ${INSTANCES_FILE}"
echo "Run ID: ${OUTPUT_RUN_ID}"
echo "Max workers: ${MAX_WORKERS}"

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config.yaml \
  --run-id "$OUTPUT_RUN_ID" \
  --mode expr \
  --max_workers "$MAX_WORKERS" \
  --agent-type two_phase_agent \
  --instances-file "$INSTANCES_FILE"

echo "=== Done: ${STYLE} ==="
