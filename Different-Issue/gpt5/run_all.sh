#!/bin/bash
# Run all 5 issue styles sequentially for gpt5
# Usage: bash run_all.sh [max_workers]

MAX_WORKERS=${1:-4}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

STYLES=("simple" "standard" "dropCode" "initPatch" "initTest")

for style in "${STYLES[@]}"; do
    echo ""
    echo "============================================"
    echo "  Running style: ${style}"
    echo "============================================"
    bash "$SCRIPT_DIR/run_issue.sh" "$style" "$MAX_WORKERS"
    if [ $? -ne 0 ]; then
        echo "FAILED: ${style}"
    fi
done

echo ""
echo "All styles completed."
