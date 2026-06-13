# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Wrapper that injects a 'thinking' parameter into any tool for structured reasoning."""

from typing import override

from trae_agent.tools.base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class ThinkingToolWrapper(Tool):
    """Wraps any Tool to add a required 'thinking' parameter.

    The thinking parameter forces the model to output structured reasoning
    before each tool call. The thinking content is stripped before passing
    arguments to the underlying tool.
    """

    def __init__(self, tool: Tool):
        super().__init__(model_provider=tool.get_model_provider())
        self._inner_tool = tool

    @override
    def get_name(self) -> str:
        return self._inner_tool.get_name()

    @override
    def get_description(self) -> str:
        return self._inner_tool.get_description()

    @override
    def get_parameters(self) -> list[ToolParameter]:
        thinking_param = ToolParameter(
            name="thinking",
            type="string",
            description=(
                "Your structured reasoning. MUST contain: "
                "1) PROGRESS: what you learned so far; "
                "2) CURRENT HYPOTHESIS: your theory about the bug; "
                "3) TOOL CHOICE JUSTIFICATION: why this tool now; "
                "4) EXPECTED OUTCOME & NEXT STEP: what you expect and what's next."
            ),
            required=True,
        )
        return [thinking_param] + self._inner_tool.get_parameters()

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        inner_args = {k: v for k, v in arguments.items() if k != "thinking"}
        return await self._inner_tool.execute(inner_args)

    async def close(self):
        return await self._inner_tool.close()
