#!/usr/bin/env python3
"""Prepare SWT-bench instances with generated (rewritten) problem statements for trae-agent.

For each of the 5 issue-rewriting styles, this script:
1. Loads the SWT-bench Verified dataset from HuggingFace
2. Loads the corresponding generated issue JSON
3. Replaces `problem_statement` with `generated_problem_statement`
4. Outputs a JSON file compatible with trae-agent's evaluation pipeline

Usage:
    python prepare_generated_issues.py [--output-dir OUTPUT_DIR]
"""

import argparse
import json
from pathlib import Path

from datasets import load_dataset

GENERATED_ISSUES_DIR = Path("/home/v-haoliu3/haoliu/Generate-issue/result")
STYLES = ["simple", "standard", "dropCode", "initPatch", "initTest"]
DATASET_NAME = "princeton-nlp/SWE-bench_Verified"
SPLIT = "test"


def main():
    parser = argparse.ArgumentParser(description="Prepare generated issue datasets for trae-agent")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "prepared_data",
        help="Directory to write output JSON files",
    )
    parser.add_argument(
        "--styles",
        nargs="+",
        default=STYLES,
        help=f"Styles to process (default: {STYLES})",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset: {DATASET_NAME}, split={SPLIT}")
    ds = list(load_dataset(DATASET_NAME, split=SPLIT))
    print(f"Loaded {len(ds)} instances")

    dataset_by_id = {inst["instance_id"]: dict(inst) for inst in ds}

    for style in args.styles:
        gen_path = GENERATED_ISSUES_DIR / f"generated_issues_{style}_gpt-5-mini.json"
        print(f"\nProcessing style: {style}")
        print(f"  Loading: {gen_path}")

        if not gen_path.exists():
            print(f"  SKIP: {gen_path} not found")
            continue

        with open(gen_path) as f:
            generated = json.load(f)

        output_instances = []
        skipped = 0

        for iid, orig_inst in dataset_by_id.items():
            if iid not in generated:
                skipped += 1
                continue
            gen_entry = generated[iid]
            if gen_entry.get("status") != "success":
                skipped += 1
                continue

            new_inst = dict(orig_inst)
            new_inst["problem_statement"] = gen_entry["generated_problem_statement"]
            output_instances.append(new_inst)

        output_path = args.output_dir / f"swtbench_{style}.json"
        with open(output_path, "w") as f:
            json.dump(output_instances, f, indent=2)

        print(f"  Written {len(output_instances)} instances to {output_path}")
        if skipped:
            print(f"  Skipped {skipped} instances (not in generated or failed)")

    print("\nDone!")


if __name__ == "__main__":
    main()
