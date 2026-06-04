#!/usr/bin/env python3
"""Convert trae-agent Different-Issue results to SWT-bench evaluation JSONL format.

Usage:
    python convert_to_eval_jsonl.py --model gpt-5mini --style simple
    python convert_to_eval_jsonl.py --model opus --style standard --output-dir /path/to/output

Output: a .jsonl file compatible with swt-bench's --predictions_path
"""

import argparse
import json
from pathlib import Path

RESULTS_BASE = Path("/home/v-haoliu3/SWT_Models/trae-agent/results")
OUTPUT_BASE = Path("/home/v-haoliu3/swt-bench-verified/swt-bench/inference_output")


def main():
    parser = argparse.ArgumentParser(description="Convert trae-agent results to SWT-bench JSONL")
    parser.add_argument("--model", required=True, help="Model name (e.g. gpt-5mini, opus)")
    parser.add_argument("--style", required=True, help="Issue style (e.g. simple, standard, dropCode, initPatch, initTest)")
    parser.add_argument("--results-base", type=Path, default=RESULTS_BASE, help="Base results directory")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_BASE, help="Output directory for JSONL")
    parser.add_argument("--model-name-or-path", default=None, help="Override model_name_or_path field (default: trae-agent__{model}__{style})")
    args = parser.parse_args()

    results_dir = args.results_base / args.model / args.style
    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}")
        return

    # Find the inner task directory (e.g. SWE-bench_SWE-bench_Verified_gpt-5mini-simple)
    inner_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if not inner_dirs:
        print(f"No task directory found in {results_dir}")
        return
    task_dir = inner_dirs[0]

    model_name = args.model_name_or_path or f"trae-agent__{args.model}__{args.style}"

    records = []
    for instance_dir in sorted(task_dir.iterdir()):
        if not instance_dir.is_dir():
            continue
        instance_id = instance_dir.name
        patch_file = instance_dir / f"{instance_id}.patch"
        if not patch_file.exists():
            continue
        patch = patch_file.read_text()
        records.append({
            "instance_id": instance_id,
            "model_name_or_path": model_name,
            "model_patch": patch,
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / f"trae-agent_{args.model}_{args.style}_verified.jsonl"
    with open(output_file, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Written {len(records)} predictions to {output_file}")


if __name__ == "__main__":
    main()
