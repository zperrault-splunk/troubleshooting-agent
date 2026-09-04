---
title: "Troubleshooting Agent Workshop"
description: "Build and instrument an AI troubleshooting agent with LangChain, MCP, and OpenTelemetry."
weight: 1
duration: "90 minutes"
---

Build a **troubleshooting agent** that investigates observability alerts with an LLM and structured tool access. You will run three implementations against the same service, inspect the resulting traces and tool output, and determine whether each conclusion is supported by telemetry.

**By the end of the workshop, you will be able to:**

- Run a minimal ReAct agent and identify which observability checks it performs, skips, or executes incorrectly
- Add **skill playbooks** that specify investigation order, required parameters, interpretation rules, and stop conditions
- Run and inspect a **multi-node LangGraph workflow** with identify → categorize → investigate → report stages
- Use **Splunk Agent Observability** to verify LLM calls, tool arguments and results, retries, skill loading, and graph transitions
- Compare final claims with returned metrics, logs, and alert data to detect unsupported conclusions
- Evaluate whether the agent selected the right tools, completed the investigation, and produced a report that the evidence supports

## What you'll build

The repository contains **three agent implementations** with the same CLI and integrations. Reusing the service, environment, and alert scenario reduces input variance when you compare orchestration and playbook behavior. Live telemetry and model output can still change between runs.

| Part | Focus | Agent shape |
|------|-------|-------------|
| **Part 1** | Baseline MCP-only agent | Single ReAct loop — tools only, no playbooks |
| **Part 2** | Skill playbooks | Same ReAct loop + keyword-injected `SKILL.md` playbooks |
| **Part 3** | Structured workflow | Four-node LangGraph graph + full skill library |

Run `troubleshooting-agent` from the directory for the part you are testing. Shared LLM, MCP, and observability integrations live in `shared/workshop_shared/` and are pre-built for you.

## Prerequisites

You need access to your workshop instance (see [Connect to EC2]({{< relref "3-connect-ec2" >}})). The repository and credentials are already set up on the instance — complete [Configure Environment]({{< relref "5-configure-agent-environment" >}}) before Part 1.

## Getting started

The repository is at `~/troubleshooting-agent` on your instance. Follow the workshop steps in order:

1. [Connect to EC2]({{< relref "3-connect-ec2" >}})
2. [Configure Environment]({{< relref "5-configure-agent-environment" >}})
3. [Part 1 — Baseline Agent]({{< relref "6-part1-baseline-agent" >}})
4. [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}})
5. [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}})
6. [Part 3 — Full Workflow]({{< relref "9-part3-full-workflow" >}})
7. [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}) *(optional)*
8. [FAQ]({{< relref "11-faq" >}})

{{< notice title="Tips" style="tip" >}}
- Run commands from the **part directory** (`part1_agent/`, `part2_agent/`, `part3_agent/`) — the CLI picks up the agent for that part automatically.
- Workshop demo defaults: service **`paymentservice`**, environment **`splunk-hipster`** — include both in chat prompts during Parts 1 and 2.
- Use `troubleshooting-agent chat "your question"` for investigations during the workshop.
- If a tool call fails, check `troubleshooting-agent mcp-doctor` first — most issues are credential or gateway configuration.
- Compare Part 1 and Part 3 responses on the **same alert** to see the impact of skills and graph structure.
{{< /notice >}}
