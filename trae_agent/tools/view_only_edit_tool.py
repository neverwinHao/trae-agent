# View-only version of str_replace_based_edit_tool for exploration phase

from pathlib import Path
from typing import override

from trae_agent.tools.base import Tool, ToolCallArguments, ToolExecResult, ToolParameter
from trae_agent.tools.edit_tool import TextEditorTool


class ViewOnlyEditorTool(TextEditorTool):
    """View-only editor tool for the exploration phase. Only supports 'view' command."""

    @override
    def get_name(self) -> str:
        return "str_replace_based_edit_tool"

    @override
    def get_description(self) -> str:
        return """File viewing tool for inspecting files and directories (READ-ONLY).
* If `path` is a file, `view` displays the result of applying `cat -n`. If `path` is a directory, `view` lists non-hidden files and directories up to 2 levels deep.
* This tool is READ-ONLY in the exploration phase. You can only use the `view` command.
* To create or edit files, you must first call `ready_to_write_test` to transition to the test writing phase.
"""

    @override
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="command",
                type="string",
                description="The command to run. Only 'view' is allowed in exploration phase.",
                required=True,
                enum=["view"],
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Absolute path to file or directory, e.g. `/repo/file.py` or `/repo`.",
                required=True,
            ),
            ToolParameter(
                name="view_range",
                type="array",
                description="Optional parameter when `path` points to a file. If provided, the file will be shown in the indicated line number range, e.g. [11, 12] will show lines 11 and 12. Indexing at 1 to start. Setting `[start_line, -1]` shows all lines from `start_line` to the end of the file.",
                items={"type": "integer"},
                required=False,
            ),
        ]

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        command = str(arguments.get("command", ""))
        if command != "view":
            return ToolExecResult(
                error="Only the 'view' command is available in the exploration phase. Call `ready_to_write_test` to transition to test writing mode.",
                error_code=-1,
            )
        path = str(arguments["path"]) if "path" in arguments else None
        if path is None:
            return ToolExecResult(error="No path provided.", error_code=-1)
        _path = Path(path)
        try:
            self.validate_path(command, _path)
            return await self._view_handler(arguments, _path)
        except Exception as e:
            return ToolExecResult(error=str(e), error_code=-1)
