---
title: "Overview of AI Agents"
description: "A high-level look at the core components of an AI agent — orchestration, models, tools, and observability."
weight: 1
navTitle: "Overview of AI Agents"
---

An AI troubleshooting agent combines a model, an orchestration runtime, tools, and telemetry. The model proposes the next step; the runtime executes it and returns the result. That distinction matters because the final response is only credible when its claims can be traced to tool evidence.

{{< diagram src="images/ai-agent-components.png" alt="High-level diagram of AI agent components: AI models, skills, MCP servers, tools, vector databases, and Splunk Agent Observability and guardrails" caption="Core components of an AI agent and how they interact during a run." width="960" >}}

## Orchestration

The **agent runtime** accepts a goal such as *“investigate this latency alert,”* gives the model access to defined tools, executes requested calls, and returns observations to the model. The cycle repeats until the agent answers or reaches a configured limit.

This workshop uses two orchestration patterns:

- **ReAct:** the model alternates between reasoning and tool calls. Parts 1 and 2 use this loop.
- **Graph workflow:** explicit nodes own stages and state. Part 3 uses LangGraph nodes for identify, categorize, investigate, and report.

[LangChain](https://www.langchain.com/) supplies the model and tool integrations used here. 

[LangGraph](https://www.langchain.com/langgraph) supplies explicit workflow state, branching, and node transitions for Part 3.

Other frameworks package the agent differently:

 [CrewAI](https://www.crewai.com/) emphasizes role-based multi-agent teams;

 [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/) targets Python and .NET with Azure and Entra integration;

 [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) provides a smaller OpenAI-native tool and handoff model;

 [Google ADK](https://google.github.io/adk-docs/) integrates with Vertex AI

 [LlamaIndex Workflows](https://docs.llamaindex.ai/en/stable/module_guides/workflow/) focuses on event-driven retrieval and document workflows. 

Framework choice affects state control, provider coupling, deployment options, and operational complexity. It does not remove the need for clear tool schemas, controlled workflows, and end-to-end traces.

{{< notice title="Concepts transfer" style="tip" >}}
Regardless of framework, verify tool schemas, workflow decisions, and LLM conclusions in the trace.
{{< /notice >}}

The agent implementations live in `part1_agent/`, `part2_agent/`, and `part3_agent/`. Each uses the same shared integrations, which makes trace comparisons meaningful.

## Model behavior

The **model** interprets alerts and user messages, selects available tools, and synthesizes conclusions from returned data. It does not query Splunk Observability directly. The model requests a tool call; the runtime dispatches it, and the tool contract validates its inputs.

Model selection trades reasoning quality against latency, cost, and context capacity. This repository supports Ollama, OpenAI-compatible APIs, and Azure OpenAI through `shared/workshop_shared/llm/`, so the provider can change without rewriting agent logic. A stronger model can improve investigation quality, but it cannot compensate for missing telemetry, ambiguous tool descriptions, or a weak workflow.

{{< notice title="Important" style="primary" >}}
Models can state plausible but unsupported facts. Treat metrics, logs, traces, and alert JSON returned by tools as evidence. Treat the model's prose as a hypothesis or summary until it matches that evidence.
{{< /notice >}}

## Tools and MCP

Each **tool** is a callable function with a name, description, and input schema. The model selects from those definitions; the runtime invokes the selected function and returns structured output.

Tools may retrieve data, discover entities, perform actions, or support processing. They can be native Python functions or capabilities exposed through **MCP (Model Context Protocol)**. In this workshop, Splunk Observability and Splunk Cloud capabilities arrive as MCP tools prefixed with `o11y_`, `splunk_`, and related namespaces.

Tool behavior depends on the contract:

- Names and descriptions must distinguish when each tool applies.
- Structured inputs and outputs reduce parameter and interpretation errors.
- Least-privilege access limits the impact of a bad decision.
- State-changing tools require stronger controls than read-only investigation tools.

**Skills** in Parts 2 and 3 are guidance loaded into the model context. They sequence tool use but do not execute calls.

## Evidence in agent traces

The final answer does not show whether the agent used the right service, time range, environment, or query. **Splunk Agent Observability**, structured terminal traces, and OpenTelemetry expose the execution path needed to make that determination.

Inspect:


| Signal             | Why it matters                                                       |
| ------------------ | -------------------------------------------------------------------- |
| **Traces / spans** | LLM calls, tool invocations, and graph node transitions              |
| **Tool calls**     | APIs called, arguments sent, results returned, and errors            |
| **Decisions**      | Product route, skills loaded, retries, and stop conditions           |
| **Quality**        | Claims supported by tool output, missing checks, and incomplete work |
| **Latency & cost** | Time per step, token use, and tool round trips                       |


Compare Part 1 and Part 3 on the same alert. A useful trace should show whether the agent selected the relevant observability APIs, supplied valid arguments, followed the intended workflow, and based its conclusion on returned data. A polished answer without those properties is not a successful investigation.

Structured traces (`AGENT_LOG_TRACE=true`) provide immediate terminal feedback. Splunk Agent Observability provides session-level analysis across runs.

---

**Next:** [AI Skills]({{< relref "2-ai-skills" >}}) for the playbook format and repository examples.