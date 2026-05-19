#!/usr/bin/env python3
"""Convert trae-agent trajectory JSON to SWE-agent style readable log."""

import json
import sys
from datetime import datetime


def convert_trajectory(json_path: str, output_path: str | None = None):
    with open(json_path) as f:
        traj = json.load(f)

    lines = []

    def log(level, logger, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S,000")
        lines.append(f"{ts} - {level} - {logger} - {msg}")

    instance_id = json_path.split("/")[-1].replace(".json", "")
    logger = f"trae-agent-{instance_id}"

    # Header
    log("INFO", logger, f"Task: {traj.get('task', 'unknown')}")
    log("INFO", logger, f"Model: {traj.get('model', 'unknown')}")
    log("INFO", logger, f"Provider: {traj.get('provider', 'unknown')}")
    log("INFO", logger, f"Max steps: {traj.get('max_steps', 'unknown')}")
    log("INFO", logger, f"Start time: {traj.get('start_time', 'unknown')}")
    lines.append("")

    # System prompt from first LLM interaction
    interactions = traj.get("llm_interactions", [])
    if interactions:
        first = interactions[0]
        msgs = first.get("messages", [])
        for m in msgs:
            if m.get("role") == "system":
                log("INFO", logger, f"SYSTEM PROMPT\n{m.get('content', '')}")
                lines.append("")
                break

    # Agent steps
    steps = traj.get("agent_steps", [])
    for step in steps:
        step_num = step.get("step_number", "?")
        state = step.get("state", "unknown")

        lines.append(f"{'=' * 25} STEP {step_num} {'=' * 25}")

        # LLM response
        llm_resp = step.get("llm_response", {})
        if llm_resp:
            content = llm_resp.get("content", "")
            if content:
                log("INFO", logger, f"💭 THOUGHT\n{content}")
                lines.append("")

        # Tool calls
        tool_calls = step.get("tool_calls") or []
        for tc in tool_calls:
            name = tc.get("name", "unknown")
            args = tc.get("arguments", {})

            # Format like SWE-agent
            log("INFO", logger, f"🎬 ACTION")
            lines.append(json.dumps({"tool_name": name, "parameters": args}, indent=2))
            lines.append("")

        # Tool results
        tool_results = step.get("tool_results") or []
        for tr in tool_results:
            name = tr.get("name", "unknown")
            success = tr.get("success", False)
            result = tr.get("result", "")
            error = tr.get("error", "")

            log("INFO", logger, "🤖 OBSERVATION")
            if success and result:
                # Truncate very long results
                if len(result) > 3000:
                    result = result[:3000] + "\n... [truncated]"
                lines.append(result)
            elif error:
                lines.append(f"ERROR: {error}")
            else:
                lines.append("(no output)")
            lines.append("")

        # Reflection
        reflection = step.get("reflection")
        if reflection:
            log("INFO", logger, f"🔄 REFLECTION\n{reflection}")
            lines.append("")

        # Error
        err = step.get("error")
        if err:
            log("ERROR", logger, f"Step error: {err}")
            lines.append("")

    # Footer
    lines.append("=" * 60)
    log("INFO", logger, f"Success: {traj.get('success', False)}")
    log("INFO", logger, f"Execution time: {traj.get('execution_time', 0):.1f}s")
    log("INFO", logger, f"Final result: {str(traj.get('final_result', ''))[:500]}")

    output = "\n".join(lines)

    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Written to {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_traj_to_log.py <trajectory.json> [output.log]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert_trajectory(json_path, output_path)
