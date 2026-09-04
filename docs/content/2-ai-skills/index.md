---
title: "AI Skills"
description: "What AI skills (playbooks) are, why they matter for reliable agents, and how they differ from tools and prompts."
weight: 2
navTitle: "AI Skills"
---

An **AI skill**, or **playbook**, is markdown guidance loaded into the model context for a specific task. It defines which checks to run, which tools and parameters to use, how to interpret results, and when to stop.

**Tools execute operations. Skills direct tool use.** A tool can fetch APM latency or run a Splunk query. A skill tells the model when to call that tool, which service and time range to provide, and what the result does or does not establish. Skills do not execute tools.

In this repository, skills live under `skills/<skill-name>/SKILL.md`. You will edit and run them in [Part 2]({{< relref "8-part2-skill-playbooks" >}}), then inspect per-node loading in [Part 3]({{< relref "9-part3-full-workflow" >}}).

## What skills control

Without a playbook, the model decides the investigation order, parameters, stopping point, and report structure on every run. That flexibility is useful for exploration but produces variable operational results. A skill makes those decisions reviewable and testable.

Use skills to specify:

- Required checks and their order
- Valid tool names, parameters, indexes, and environments
- Interpretation rules for returned metrics, logs, and alert state
- Behavior when a query returns no data or a tool fails
- Evidence required before the agent can state a conclusion
- A stable output structure for downstream review

This does not make an agent deterministic. The model can still choose poorly, tools can return incomplete data, and telemetry can be ambiguous. The benefit is narrower variance: traces show which playbook loaded, which required steps ran, and where execution diverged.

{{< notice title="Workshop tie-in" style="tip" >}}
[Part 1]({{< relref "6-part1-baseline-agent" >}}) establishes the tools-only baseline. Parts 2 and 3 apply playbooks to the same alert so you can compare the execution traces.
{{< /notice >}}

## Prompts, tools, and skills

Keep the responsibilities separate:

| Layer | What it is | General example | Workshop example |
|-------|------------|-----------------|------------------|
| **System prompt** | Standing instructions for every run | Tone, safety, global rules | Base instructions in `prompt.py` |
| **Tools** | Callable functions that fetch data or take action in external systems | `search_tickets`, `get_account_balance`, `run_database_query` | `o11y_get_apm_service_latency`, `splunk_run_query` |
| **Skills** | Task-specific procedures loaded when relevant work starts | Latency investigation sequence | `latency-spike`, `troubleshoot-apm-incidents` |

In a trace, a skill-load event shows that guidance entered the context. An MCP tool span shows that an external operation actually ran. Do not treat skill loading as evidence that the prescribed checks completed.

{{< notice title="Important" style="primary" >}}
A loaded skill is guidance, not execution. Confirm the required MCP calls and their results in the trace.
{{< /notice >}}

## Skill contents

Most skills are plain markdown with a small metadata block. Keep the main file short enough to review:

| Section | Purpose |
|---------|---------|
| **When to use** | Symptoms, alert types, or user intents that match this playbook |
| **Required context** | What the agent must know before acting (IDs, time window, environment) |
| **Steps / tool sequence** | Ordered actions — often mapped to specific tools |
| **Interpretation** | How to read results — not just what to call |
| **Do not** | Guardrails against skipped steps, invalid formats, and invented data |
| **Output format** | How to hand off or report (sometimes a separate reporting skill) |

Use companion files for changing reference data such as field names, index catalogs, and query templates. Keep routing metadata such as name, description, and keywords at the top of the skill.

{{< notice title="Tip" style="tip" >}}
Use short steps, exact tool names, valid parameter examples, and explicit evidence thresholds. Vague guidance produces vague traces.
{{< /notice >}}

## Loading patterns

The orchestration layer decides when playbook text enters the model context:

| Pattern | How it works | When it fits |
|---------|--------------|--------------|
| **Upfront injection** | Match the user's message or alert to a skill, load it before the first model turn | Simple agents, keyword routing, fast prototypes |
| **Per workflow step** | Different skills at different stages (identify → investigate → report) | Production workflows with explicit phases |
| **On demand** | Agent or router calls a "load skill" tool when it recognizes the task | Large skill libraries, dynamic runbooks |

- **Part 2** — one domain skill plus a reporting skill, injected **upfront** via keyword matching
- **Part 3** — different skills at each **graph node** (alert identification, product-specific investigation, final report)

Both parts use the same `SKILL.md` format. The trace should show the different load timing.

## Repository example

This simplified playbook shows the required metadata, context, tool order, and empty-result behavior:

```yaml
---
name: alert-triage
description: Confirm an observability alert is active and capture identifiers for follow-up steps.
---
```

```markdown
# Alert triage

## When to use
Before deeper investigation on any monitoring alert.

## Required context
- Service and environment names (exact values from the alert)
- Time window for the investigation (e.g. last hour)

## Steps
1. Search for matching alerts or incidents — filter by service and environment
2. Record alert ID and status (active / cleared) for later steps

## Do not
- Skip the search when the user pasted partial alert text
- Invent alert IDs if the search returns nothing — say what you tried
```

Full source: [`part2_agent/skills/alert-triage/SKILL.md`](https://github.com/zperrault-splunk/troubleshooting-agent/blob/main/part2_agent/skills/alert-triage/SKILL.md).

The larger repository skills add APM latency checks, log searches, and structured reporting. The same review standard applies: every required conclusion should map to a tool result or be labeled as unverified.

## Authoring checks

- Keep one concern per skill; compose investigation and reporting playbooks when appropriate.
- Use exact exposed tool names. A typo is a failed call, not a minor documentation defect.
- Define empty-result and tool-error behavior. "No data found" is valid; an invented cause is not.
- Version and review skills as code. Operational procedures drift without ownership.
- Never put secrets in skill files. Credentials belong in environment variables or a secrets manager.
- Keep changing catalogs such as index names, field maps, and tenant tables in companion files.

## Workshop path

- [Part 1]({{< relref "6-part1-baseline-agent" >}}): run the tools-only baseline and record missing or unsupported steps.
- [Part 2]({{< relref "8-part2-skill-playbooks" >}}): run upfront skill injection and complete the **`error-rate`** skill lab.
- [Part 3]({{< relref "9-part3-full-workflow" >}}): inspect per-node skill loading, log search, and structured reporting.

Part 2 covers the YAML fields, checklist, and MCP tool names used when you edit `SKILL.md`.

---

**Next:** [Connect to EC2]({{< relref "3-connect-ec2" >}}) to set up the workshop environment, or return to [Overview of AI Agents]({{< relref "1-ai-agents-overview" >}}).
