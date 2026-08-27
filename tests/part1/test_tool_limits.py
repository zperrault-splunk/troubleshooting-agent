"""Tests for ReAct subgraph tool call limits."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool

from part1_agent.agent import _build_limited_tool_node, build_react_subgraph


@tool
def echo_tool(text: str) -> str:
    """Echo input."""
    return text


@pytest.mark.asyncio
async def test_react_subgraph_skips_duplicate_tool_calls() -> None:
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=llm)
    llm.ainvoke = AsyncMock(
        side_effect=[
            AIMessage(
                content="",
                tool_calls=[{"name": "echo_tool", "args": {"text": "first"}, "id": "call-1"}],
            ),
            AIMessage(
                content="",
                tool_calls=[{"name": "echo_tool", "args": {"text": "second"}, "id": "call-2"}],
            ),
            AIMessage(content="finished"),
        ]
    )

    graph = build_react_subgraph(
        llm,
        [echo_tool],
        system_prompt="test",
        tool_call_limits={"echo_tool": 1},
    )
    app = graph.compile()
    result = await app.ainvoke({"messages": []})

    assert result["messages"][-1].content == "finished"
    assert llm.ainvoke.await_count == 3
    skipped = [
        message
        for message in result["messages"]
        if hasattr(message, "content") and "SKIPPED" in str(message.content)
    ]
    assert skipped


@pytest.mark.asyncio
async def test_limited_tool_node_forwards_runnable_config() -> None:
    mock_tool_node = MagicMock()
    mock_tool_node.ainvoke = AsyncMock(return_value={"messages": []})

    with patch("part1_agent.agent.ToolNode", return_value=mock_tool_node):
        limited = _build_limited_tool_node([echo_tool], tool_call_limits={"echo_tool": 2})

    state: dict[str, list] = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": "echo_tool", "args": {"text": "probe"}, "id": "call-1"}],
            )
        ]
    }
    config = RunnableConfig(recursion_limit=10)
    await limited(state, config)

    mock_tool_node.ainvoke.assert_awaited_once()
    call_args = mock_tool_node.ainvoke.await_args
    assert call_args is not None
    passed_config = (
        call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs.get("config")
    )
    assert passed_config is config
