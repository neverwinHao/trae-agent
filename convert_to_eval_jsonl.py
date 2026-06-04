#!/usr/bin/env python3
"""Convert trae-agent results to SWT-bench evaluation JSONL format.

Supports both Different-Issue results and direct run results (e.g. twophase).

Usage:
    # Different-Issue style (nested directory structure: results/model/style/SWE-bench_xxx/)
    python convert_to_eval_jsonl.py --model gpt-5mini --style simple
    python convert_to_eval_jsonl.py --model opus --style standard

    # Direct results directory (flat structure: results/SWE-bench_xxx/instance_id/)
    python convert_to_eval_jsonl.py --results-dir results/SWE-bench_SWE-bench_Verified_gpt5mini-twophase-full --name gpt5mini_twophase

Output: a .jsonl file in swt-bench inference_output/
"""

import argparse
import json
from pathlib import Path

RESULTS_BASE = Path("/home/v-haoliu3/SWT_Models/trae-agent/results")
OUTPUT_BASE = Path("/home/v-haoliu3/swt-bench-verified/swt-bench/inference_output")
FILTER_IDS_FILE = Path("/home/v-haoliu3/SWT_Models/trae-agent/Different-Issue/prepared_data/swtbench_simple.json")


def load_filter_ids() -> set[str]:
    """Load the 433 instance IDs used in Different-Issue experiments."""
    with open(FILTER_IDS_FILE) as f:
        data = json.load(f)
    return {d["instance_id"] for d in data}


def collect_patches(task_dir: Path, filter_ids: set[str] | None = None) -> list[dict]:
    records = []
    for instance_dir in sorted(task_dir.iterdir()):
        if not instance_dir.is_dir():
            continue
        instance_id = instance_dir.name
        if filter_ids and instance_id not in filter_ids:
            continue
        patch_file = instance_dir / f"{instance_id}.patch"
        if not patch_file.exists():
            continue
        patch = patch_file.read_text()
        records.append({
            "instance_id": instance_id,
            "model_patch": patch,
        })
    return records


def main():
    parser = argparse.ArgumentParser(description="Convert trae-agent results to SWT-bench JSONL")
    parser.add_argument("--model", help="Model name (e.g. gpt-5mini, opus) — for Different-Issue mode")
    parser.add_argument("--style", help="Issue style (e.g. simple, standard, dropCode, initPatch, initTest) — for Different-Issue mode")
    parser.add_argument("--results-dir", type=Path, help="Direct path to results directory containing instance folders")
    parser.add_argument("--name", help="Output name identifier (used for filename and model_name_or_path)")
    parser.add_argument("--results-base", type=Path, default=RESULTS_BASE, help="Base results directory")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_BASE, help="Output directory for JSONL")
    parser.add_argument("--model-name-or-path", default=None, help="Override model_name_or_path field in output")
    parser.add_argument("--no-filter", action="store_true", help="Don't filter to the 433 instance IDs (include all)")
    args = parser.parse_args()

    if args.results_dir:
        # Direct mode
        task_dir = args.results_dir
        if not task_dir.exists():
            print(f"Results directory not found: {task_dir}")
            return
        name = args.name or task_dir.name
        model_name = args.model_name_or_path or f"trae-agent__{name}"
        output_filename = f"trae-agent_{name}_verified.jsonl"
    elif args.model and args.style:
        # Different-Issue mode
        results_dir = args.results_base / args.model / args.style
        if not results_dir.exists():
            print(f"Results directory not found: {results_dir}")
            return
        inner_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
        if not inner_dirs:
            print(f"No task directory found in {results_dir}")
            return
        task_dir = inner_dirs[0]
        name = f"{args.model}_{args.style}"
        model_name = args.model_name_or_path or f"trae-agent__{args.model}__{args.style}"
        output_filename = f"trae-agent_{name}_verified.jsonl"
    else:
        parser.error("Either --results-dir (with --name) or --model + --style is required")
        return

    filter_ids = None if args.no_filter else load_filter_ids()
    records = collect_patches(task_dir, filter_ids)
    for r in records:
        r["model_name_or_path"] = model_name

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / output_filename
    with open(output_file, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Written {len(records)} predictions to {output_file}")


if __name__ == "__main__":
    main()
