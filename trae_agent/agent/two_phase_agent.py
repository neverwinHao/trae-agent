# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Two-phase TraeAgent: Exploration phase -> Test Writing phase."""

from typing import override

from trae_agent.agent.trae_agent import TraeAgent
from trae_agent.prompt.agent_prompt import TWOPHASE_SYSTEM_PROMPT_PHASE1, TWOPHASE_SYSTEM_PROMPT_PHASE2
from trae_agent.tools import tools_registry
from trae_agent.tools.base import Tool, ToolCall, ToolResult
from trae_agent.utils.config import TraeAgentConfig
from trae_agent.utils.llm_clients.llm_basics import LLMMessage, LLMResponse


# Phase 1: exploration only (view-only editor, no file creation/editing)
PHASE1_TOOL_NAMES = [
    "view_only_edit_tool",
    "bash",
    "sequentialthinking",
    "ready_to_write_test",
]

# Phase 2: test writing tools (full editing capability)
PHASE2_TOOL_NAMES = [
    "str_replace_based_edit_tool",
    "bash",
    "sequentialthinking",
    "task_done",
]


class TwoPhaseTraeAgent(TraeAgent):
    """TraeAgent with two-phase architecture: Exploration -> Test Writing."""

    def __init__(
        self,
        trae_agent_config: TraeAgentConfig,
        docker_config: dict | None = None,
        docker_keep: bool = True,
    ):
        super().__init__(trae_agent_config, docker_config, docker_keep)
        self._current_phase = 1
        self._phase_transition_summary: str | None = None

    @override
    def new_task(
        self,
        task: str,
        extra_args: dict[str, str] | None = None,
        tool_names: list[str] | None = None,
    ):
        """Create a new task, starting in Phase 1."""
        self._current_phase = 1
        # Force phase 1 tools before calling super
        provider = self._model_config.model_provider.provider
        self._tools = [
            tools_registry[tool_name](model_provider=provider)
            for tool_name in PHASE1_TOOL_NAMES
        ]
        # Reset tool caller with phase 1 tools
        from trae_agent.tools.base import ToolExecutor
        if self.docker_manager:
            from trae_agent.tools.docker_tool_executor import DockerToolExecutor
            original_executor = ToolExecutor(self._tools)
            self._tool_caller = DockerToolExecutor(
                original_executor=original_executor,
                docker_manager=self.docker_manager,
                docker_tools=["bash", "str_replace_based_edit_tool", "json_edit_tool"],
                host_workspace_dir=self.docker_config.get("workspace_dir") if self.docker_config else None,
                container_workspace_dir=self.docker_manager.container_workspace,
            )
        else:
            self._tool_caller = ToolExecutor(self._tools)
        # Call parent but it won't override tools since self._tools is not empty
        super().new_task(task, extra_args, tool_names=PHASE1_TOOL_NAMES)

    @override
    def get_system_prompt(self) -> str:
        """Get phase-appropriate system prompt."""
        if self._current_phase == 1:
            return TWOPHASE_SYSTEM_PROMPT_PHASE1
        return TWOPHASE_SYSTEM_PROMPT_PHASE2

    def _switch_to_phase2(self, summary: str):
        """Switch from exploration to test writing phase."""
        self._current_phase = 2
        self._phase_transition_summary = summary

        # Replace tools with phase 2 tools
        provider = self._model_config.model_provider.provider
        self._tools = [
            tools_registry[tool_name](model_provider=provider)
            for tool_name in PHASE2_TOOL_NAMES
        ]
        # Reset tool caller
        from trae_agent.tools.base import ToolExecutor
        if self.docker_manager:
            from trae_agent.tools.docker_tool_executor import DockerToolExecutor
            original_executor = ToolExecutor(self._tools)
            self._tool_caller = DockerToolExecutor(
                original_executor=original_executor,
                docker_manager=self.docker_manager,
                docker_tools=["bash", "str_replace_based_edit_tool", "json_edit_tool"],
                host_workspace_dir=self.docker_config.get("workspace_dir") if self.docker_config else None,
                container_workspace_dir=self.docker_manager.container_workspace,
            )
        else:
            self._tool_caller = ToolExecutor(self._tools)

    @override
    async def _tool_call_handler(
        self, tool_calls: list[ToolCall] | None, step
    ) -> list[LLMMessage]:
        """Handle tool calls with phase transition detection."""
        if not tool_calls or len(tool_calls) <= 0:
            return [
                LLMMessage(
                    role="user",
                    content="It seems that you have not completed the task.",
                )
            ]

        # Check if ready_to_write_test is being called
        phase_transition_call = None
        other_calls = []
        blocked_calls = []
        for tc in tool_calls:
            if tc.name == "ready_to_write_test":
                phase_transition_call = tc
            elif self._current_phase == 1 and tc.name == "task_done":
                blocked_calls.append(tc)
            else:
                other_calls.append(tc)

        # Execute non-transition calls first
        from trae_agent.agent.agent_basics import AgentStepState
        step.state = AgentStepState.CALLING_TOOL
        step.tool_calls = tool_calls
        self._update_cli_console(step)

        messages: list[LLMMessage] = []

        # Handle blocked calls (e.g. task_done in Phase 1)
        for tc in blocked_calls:
            blocked_result = ToolResult(
                call_id=tc.call_id,
                name=tc.name,
                success=False,
                error=(
                    "`task_done` is NOT available yet. You are in the EXPLORATION phase. "
                    "You MUST call the `ready_to_write_test` tool with a summary parameter to transition to the test writing phase first."
                ),
                id=tc.id,
            )
            messages.append(LLMMessage(role="user", tool_result=blocked_result))
            if step.tool_results is None:
                step.tool_results = [blocked_result]
            else:
                step.tool_results.append(blocked_result)

        if other_calls:
            if self._model_config.parallel_tool_calls:
                tool_results = await self._tool_caller.parallel_tool_call(other_calls)
            else:
                tool_results = await self._tool_caller.sequential_tool_call(other_calls)
            step.tool_results = tool_results
            for tool_result in tool_results:
                messages.append(LLMMessage(role="user", tool_result=tool_result))

        # Handle phase transition
        if phase_transition_call:
            summary = str(phase_transition_call.arguments.get("summary", ""))
            # Execute the tool to get its response
            result = await self._tool_caller.execute_tool_call(phase_transition_call)

            if result.success:
                self._switch_to_phase2(summary)
                transition_msg = (
                    "Phase transition successful. You are now in TEST WRITING mode.\n\n"
                    f"## Your Exploration Summary:\n{summary}\n\n"
                    "## Available Tools:\n"
                    "- str_replace_based_edit_tool (full create/view/edit/insert)\n"
                    "- bash\n"
                    "- sequentialthinking\n"
                    "- task_done (call when tests are complete)\n\n"
                    "Now write your reproduction test based on your exploration findings."
                )
                result = ToolResult(
                    call_id=phase_transition_call.call_id,
                    name=phase_transition_call.name,
                    success=True,
                    result=transition_msg,
                    id=phase_transition_call.id,
                )

            messages.append(LLMMessage(role="user", tool_result=result))
            if step.tool_results:
                step.tool_results.append(result)
            else:
                step.tool_results = [result]

        self._update_cli_console(step)

        # Reflection
        all_results = step.tool_results or []
        reflection = self.reflect_on_result(all_results)
        if reflection:
            from trae_agent.agent.agent_basics import AgentStepState
            step.state = AgentStepState.REFLECTING
            step.reflection = reflection
            self._update_cli_console(step)
            messages.append(LLMMessage(role="assistant", content=reflection))

        return messages

    @override
    def llm_indicates_task_completed(self, llm_response: LLMResponse) -> bool:
        """Only task_done in Phase 2 indicates completion."""
        if llm_response.tool_calls is None:
            return False
        if self._current_phase == 1:
            return False
        return any(tool_call.name == "task_done" for tool_call in llm_response.tool_calls)
