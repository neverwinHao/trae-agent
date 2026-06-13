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
            "You must fill in ALL six required parameters to demonstrate thorough understanding of the bug."
        )

    @override
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="bug_location",
                type="string",
                description="The exact file paths and function/method names where the bug originates. Include line numbers if known.",
                required=True,
            ),
            ToolParameter(
                name="root_cause",
                type="string",
                description="A clear explanation of WHY the bug occurs — the logical error, missing handling, or incorrect assumption in the code.",
                required=True,
            ),
            ToolParameter(
                name="expected_and_actual",
                type="string",
                description="What the correct behavior should be vs. what the buggy code actually produces. Be specific with values/types/exceptions.",
                required=True,
            ),
            ToolParameter(
                name="reproduction",
                type="string",
                description="The minimal steps, inputs, or code snippet needed to trigger the bug.",
                required=True,
            ),
            ToolParameter(
                name="existing_tests",
                type="string",
                description="Which test files/classes you examined and what conventions they follow (framework, naming, imports, directory structure, fixtures).",
                required=True,
            ),
            ToolParameter(
                name="test_plan",
                type="string",
                description="Exactly what test file to create, what test functions to write, and what assertions they will make to demonstrate the bug.",
                required=True,
            ),
        ]

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        required_fields = ["bug_location", "root_cause", "expected_and_actual", "reproduction", "existing_tests", "test_plan"]
        missing = [f for f in required_fields if not arguments.get(f) or len(str(arguments.get(f, ""))) < 20]
        if missing:
            return ToolExecResult(
                error=f"Insufficient detail in fields: {missing}. Each field must have at least 20 characters of substantive content.",
                error_code=-1,
            )
        return ToolExecResult(
            output=(
                "Phase transition successful. You are now in TEST WRITING mode.\n"
                "Available tools: str_replace_based_edit_tool, bash, sequentialthinking, task_done.\n"
                "Write your reproduction test now based on your analysis above."
            )
        )
