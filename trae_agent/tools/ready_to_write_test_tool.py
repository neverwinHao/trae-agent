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
                name="thinking",
                type="string",
                description="Your structured reasoning: PROGRESS, CURRENT HYPOTHESIS, TOOL CHOICE JUSTIFICATION, EXPECTED OUTCOME & NEXT STEP",
                required=True,
            ),
            ToolParameter(
                name="summary",
                type="string",
                description="Detailed summary covering: bug location, root cause, expected vs actual behavior, reproduction steps, reference tests examined, and test plan. Must be 200-2000 chars.",
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
