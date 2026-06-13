# Two-phase agent tool: signals transition from exploration to test writing

from typing import override

from trae_agent.tools.base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class ReadyToWriteTestTool(Tool):
    """Signal that exploration is complete and the agent is ready to write tests."""

    def __init__(self, model_provider: str | None = None) -> None:
        super().__init__(model_provider)

    @override
    def get_model_provider(self) -> str | None:
        return self._model_provider

    @override
    def get_name(self) -> str:
        return "ready_to_write_test"

    @override
    def get_description(self) -> str:
        return (
            "Signal that you have finished exploring and are ready to write tests. "
            "You MUST call this tool before creating or editing test files. "
            "After calling this tool, your available tools will switch to test-writing mode. "
            "Your summary should include: bug location, root cause, expected vs actual behavior, "
            "reproduction steps, reference tests examined, and test plan."
        )

    @override
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="summary",
                type="string",
                description=(
                    "A detailed summary of your exploration findings. MUST address ALL six aspects below:\n"
                    "1. BUG LOCATION: The exact file paths and function/method names where the bug originates.\n"
                    "2. ROOT CAUSE: A clear explanation of WHY the bug occurs (the logical error or missing handling).\n"
                    "3. EXPECTED vs ACTUAL BEHAVIOR: What the correct behavior should be, and what the buggy code actually produces.\n"
                    "4. REPRODUCTION: The minimal steps or inputs needed to trigger the bug.\n"
                    "5. EXISTING TESTS EXAMINED: Which test files/classes you looked at, and what conventions they follow (framework, naming, imports, fixtures).\n"
                    "6. TEST PLAN: Exactly what test file to create, what test functions to write, and what assertions they will make to demonstrate the bug."
                ),
                required=True,
            ),
        ]

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        summary = arguments.get("summary", "")
        if not summary or len(str(summary)) < 50:
            return ToolExecResult(
                error="Summary too short. Provide a detailed summary (200-2000 chars) of your exploration findings.",
                error_code=-1,
            )
        return ToolExecResult(
            output=(
                "Phase transition successful. You are now in TEST WRITING mode.\n"
                "Available tools: str_replace_based_edit_tool, bash, sequentialthinking, task_done.\n"
                "RPG/exploration tools are no longer available.\n"
                "Write your reproduction test now."
            )
        )
