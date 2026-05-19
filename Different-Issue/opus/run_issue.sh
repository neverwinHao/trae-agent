#!/bin/bash
# Run trae-agent pipeline with a specific issue style
# Usage: bash run_issue.sh <style> [max_workers]
# Styles: simple, standard, dropCode, initPatch, initTest
#
# Output: results/opus/<style>/

STYLE=${1:?"Usage: bash run_issue.sh <style> [max_workers]"}
MAX_WORKERS=${2:-4}
MODEL="opus"

cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

INSTANCES_FILE="Different-Issue/prepared_data/swtbench_${STYLE}.json"
OUTPUT_DIR="results/${MODEL}/${STYLE}"
RUN_ID="${MODEL}-${STYLE}"

if [ ! -f "$INSTANCES_FILE" ]; then
    echo "Instances file not found: $INSTANCES_FILE"
    echo "Run 'python Different-Issue/prepare_generated_issues.py' first."
    exit 1
fi

echo "=== Running trae-agent with issue style: ${STYLE} ==="
echo "Model: ${MODEL}"
echo "Instances file: ${INSTANCES_FILE}"
echo "Output dir: ${OUTPUT_DIR}"
echo "Max workers: ${MAX_WORKERS}"

python -m evaluation.run_evaluation \
  --benchmark SWE-bench \
  --dataset SWE-bench_Verified \
  --config-file test_config-opus.yaml \
  --run-id "$RUN_ID" \
  --mode expr \
  --max_workers "$MAX_WORKERS" \
  --instances-file "$INSTANCES_FILE" \
  --output-dir "$OUTPUT_DIR"

echo "=== Done: ${STYLE} ==="
