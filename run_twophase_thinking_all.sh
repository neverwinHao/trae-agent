#!/bin/bash
# Run twophase+thinking for all 3 models, then convert and eval each
# Usage: bash run_twophase_thinking_all.sh

set -euo pipefail
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

EVAL_BASE="/home/v-haoliu3/swt-bench-verified/swt-bench"
INFERENCE_DIR="${EVAL_BASE}/inference_output/twophase-thinking"
mkdir -p "${INFERENCE_DIR}"

# Filter IDs file (433 instances)
FILTER_IDS="/home/v-haoliu3/SWT_Models/trae-agent/Different-Issue/prepared_data/swtbench_simple.json"

run_and_eval() {
    local model_name=$1
    local config_file=$2
    local workspace=$3
    local run_id="${model_name}-twophase-thinking"
    local task_dir="results/SWE-bench_SWE-bench_Verified_${run_id}"
    local jsonl="${INFERENCE_DIR}/trae-agent_${run_id}_verified.jsonl"

    echo ""
    echo "============================================"
    echo "  TwoPhase+Thinking: ${model_name}"
    echo "============================================"

    # Inference
    python -m evaluation.run_evaluation \
      --benchmark SWE-bench \
      --dataset SWE-bench_Verified \
      --config-file "${config_file}" \
      --working-dir "./${workspace}" \
      --run-id "${run_id}" \
      --mode expr \
      --max_workers 4 \
      --agent-type two_phase_agent

    echo "[DONE] Inference: ${run_id}"

    # Convert to jsonl (filtered to 433)
    echo "  Converting to jsonl..."
    python convert_to_eval_jsonl.py \
      --results-dir "${task_dir}" \
      --name "${run_id}" \
      --output-dir "${INFERENCE_DIR}"

    # Eval
    echo "  Evaluating..."
    cd "${EVAL_BASE}"
    uv run -m src.main \
        --dataset_name princeton-nlp/SWE-bench_Verified \
        --predictions_path "${jsonl}" \
        --max_workers 12 \
        --run_id "${run_id}" \
        --patch_types vanilla \
        --build_mode api

    echo "[DONE] Eval: ${run_id}"
    cd /home/v-haoliu3/SWT_Models/trae-agent
}

run_and_eval "gpt5mini" "test_config.yaml" "trae-workspace-gpt5mini-twophase"
run_and_eval "opus" "test_config-opus.yaml" "trae-workspace-opus-twophase"
run_and_eval "gpt5" "test_config-gpt5.yaml" "trae-workspace-gpt5-twophase"

echo ""
echo "=== All 3 models complete ==="
