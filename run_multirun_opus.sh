#!/bin/bash
# Run naive trae-agent 5 times for Opus, then eval each run
# Output: results/multi-run/opus/

set -euo pipefail
cd /home/v-haoliu3/SWT_Models/trae-agent
source .venv/bin/activate

OUTPUT_DIR="results/multi-run/opus"
MODEL_CONFIG="test_config-opus.yaml"
EVAL_BASE="/home/v-haoliu3/swt-bench-verified/swt-bench"
INFERENCE_DIR="${EVAL_BASE}/inference_output/multi-run/opus"
EVAL_RESULTS_DIR="${EVAL_BASE}/evaluation_results/multi-run/opus"
mkdir -p "${INFERENCE_DIR}" "${EVAL_RESULTS_DIR}"

for i in $(seq 1 5); do
    RUN_ID="opus-naive-run${i}"
    TASK_DIR="${OUTPUT_DIR}/SWE-bench_SWE-bench_Verified_${RUN_ID}"
    JSONL="${INFERENCE_DIR}/${RUN_ID}.jsonl"

    echo ""
    echo "============================================"
    echo "  Running: ${RUN_ID}"
    echo "============================================"

    python -m evaluation.run_evaluation \
        --benchmark SWE-bench \
        --dataset SWE-bench_Verified \
        --config-file "${MODEL_CONFIG}" \
        --run-id "${RUN_ID}" \
        --mode expr \
        --max_workers 4 \
        --output-dir "${OUTPUT_DIR}" \
        --working-dir "./trae-workspace-opus"

    echo "[DONE] Inference: ${RUN_ID}"

    # Convert patches to jsonl
    echo "  Converting to jsonl..."
    python3 -c "
import json, os
with open('/home/v-haoliu3/swt-bench/evaluation_results/claude_opus_4_5_pipeline_phase_agent_diff_summary_all_1.claude-opus-4.5-claude_opus_4_5_pipeline_phase_agent_diff_summary_all_1-20260416.json') as f:
    data = json.load(f)
ids_433 = set(data['resolved_ids'] + data['unresolved_ids'] + data['error_ids'])
folder = '${TASK_DIR}'
results = []
for iid in sorted(ids_433):
    patch_file = os.path.join(folder, iid, f'{iid}.patch')
    if os.path.exists(patch_file):
        with open(patch_file) as f:
            patch = f.read().strip()
        if patch and len(patch) < 100000:
            results.append({'instance_id': iid, 'model_patch': patch, 'model_name_or_path': '${RUN_ID}'})
with open('${JSONL}', 'w') as f:
    for r in results:
        f.write(json.dumps(r) + '\n')
print(f'  Written {len(results)} instances to ${JSONL}')
"

    # Eval
    echo "  Evaluating..."
    cd "${EVAL_BASE}"
    uv run -m src.main \
        --dataset_name princeton-nlp/SWE-bench_Verified \
        --predictions_path "${JSONL}" \
        --max_workers 12 \
        --run_id "${RUN_ID}" \
        --patch_types vanilla \
        --build_mode api

    # Move result to structured dir
    result_file=$(ls evaluation_results/*."${RUN_ID}".json 2>/dev/null | head -1)
    if [ -n "${result_file}" ]; then
        mv "${result_file}" "${EVAL_RESULTS_DIR}/"
        echo "  [DONE] Eval -> ${EVAL_RESULTS_DIR}/$(basename ${result_file})"
    fi

    cd /home/v-haoliu3/SWT_Models/trae-agent
done

echo ""
echo "=== All 5 runs complete ==="
echo "Inference results: ${OUTPUT_DIR}/"
echo "Eval results: ${EVAL_RESULTS_DIR}/"
