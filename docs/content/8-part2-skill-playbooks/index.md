---
title: "Part 2 — Skill Playbooks"
description: "Run the skill-injected ReAct agent, compare Action Completion with Part 1, and author your own latency playbook."
weight: 8
navTitle: "Part 2 — Skill Playbooks"
duration: "30 minutes"
---

Run the same high-error alert from Part 1 through a ReAct loop with markdown playbooks injected into its system prompt. First observe how the supplied `error-rate` playbook changes Action Completion. Then complete and test the separate `latency-spike` skill.

For playbook concepts and design rationale, see [AI Skills]({{< relref "2-ai-skills" >}}).

## Part 1 vs Part 2


| Component                           | Part 1          | Part 2                                                                   |
| ----------------------------------- | --------------- | ------------------------------------------------------------------------ |
| **Agent loop**                      | LangGraph ReAct | Same ReAct loop                                                          |
| **Playbooks**                       | None            | One **domain** skill + always-on `investigation-report`                  |
| **Routing**                         | —               | Keyword match on your chat/alert text (`alert_signals` in SKILL.md YAML) |
| **Extra Agent Observability trace** | —               | `skill_router` — all skills injected **before** the ReAct loop           |


```text
New Workflow: Your message → keyword router → SKILL.md → system prompt → ReAct loop (LLM + MCP tools)
```

Agent code structure:
| File                                    | Purpose                                                   |
| --------------------------------------- | --------------------------------------------------------- |
| `part2_agent/agent.py`                  | Builds prompt with injected skills; logs routing metadata |
| `part2_agent/skill_inject.py`           | Keyword router and prompt assembly                        |
| `part2_agent/skills/`                   | Playbook library — you edit skills here                   |
| `part2_agent/skills/_template/SKILL.md` | Blank template for new playbooks                          |

## Run Part 2 agent

From `part2_agent`, run the **same high-error alert prompt** used in Part 1. Keeping the prompt identical makes the Action Completion comparison meaningful:

{{< notice title="Same agent stream" style="tip" >}} Part 2 sessions appear in the same Agent Stream as Part 1. Look for the `part2_agent` suffix in the session name.
{{< /notice >}}

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part2_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

{{% /tab %}}
{{< /tabs >}}

## Review Part 2 in Splunk Agent Observability

Open **Agent Stream** in the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io). Select the newest session named `chat-… | part2_agent`.

{{< notice title="Skills are prompt injection, not MCP tools" style="primary" >}}
Playbooks are appended to the **system prompt** before the ReAct loop runs. You will **not** see `load_skill:investigation-report` or `load_skill:error-rate` under `Agent` **→** `tools` — those spans only show MCP calls like `o11y_search_alerts_or_incidents`.

To confirm skills loaded, check:

1. **Terminal**: Lines like `[N] Skill loaded: error-rate` and `[N] Skill loaded: investigation-report`
2. **Splunk Agent Observability**: A separate `skill_router` trace in the same session (sibling to `Agent`, not nested inside it)
3. **Chat JSON**: The system message includes `## Active playbook` and `## Reporting requirements`

{{< /notice >}}

### skill_router trace

Part 2 records `skill_router` before the main `Agent` trace in the same session. On the Part 2 high-error session:

- Select `skill_router`. It is a **sibling** of `Agent`, **not a child**.
- Expand `load_skill:error-rate` and `load_skill:investigation-report`. Confirm that each span reports the characters injected into the system prompt.
- Expand `Agent` → `tools`. Confirm calls to `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`.
- Open **Evaluators** and compare **Action Completion (SLM)** with Part 1.



### Main investigation trace

The ReAct trace still contains `Agent:agent`, `tools`, and `should_continue`. For `error-rate`, verify this tool order:

1. `o11y_search_alerts_or_incidents`
2. `o11y_get_apm_service_errors_and_requests`

{{< notice title="Empty Alert" style="tip" >}} An empty alert list is not a stopping condition. {{< /notice >}}

The agent must still call the error/request metrics tool and format the final reply with `investigation-report` headings. Stopping after alert search or asking whether to pull metrics is an incomplete run.

The `error-rate` playbook tells the agent to omit `severity` unless requested, continue after an empty alert search, and interpret error count relative to request volume.

### Compare Action Completion to Part 1

On the **Evaluators** tab, compare **Action Completion (SLM)** and its explanation with the Part 1 session. Because both runs use the same alert prompt, differences are more likely to reflect the playbook rather than a change in the task.

{{< notice title="Tip" style="tip" >}}
Filter Agent Stream by session name suffix `part2_agent`, or use the session picker to compare `part1_agent` vs `part2_agent` runs side by side.
{{< /notice >}}

## Anatomy of a [SKILL.md](http://SKILL.md)

Every playbook lives in `part2_agent/skills/<skill-name>/SKILL.md`. Open the supplied `skills/error-rate/SKILL.md` as the reference while you work.

The file starts with YAML between `---` lines:


| Field           | Purpose                                                               |
| --------------- | --------------------------------------------------------------------- |
| `name`          | Skill identifier (usually matches the folder name)                    |
| `description`   | One line: when to use this playbook                                   |
| `alert_signals` | Keywords matched against your chat/alert text (lowercase)             |
| `mcp_tools`     | Tools the playbook expects (guides the model)                         |
| `rule_patterns` | (Optional) document detector name patterns (reference only in Part 2) |


Example from `error-rate`:

```yaml
---
name: error-rate
description: Investigate error-rate alerts using o11y_get_apm_service_errors_and_requests.
alert_signals:
  - error
  - errors
  - 5xx
mcp_tools:
  - o11y_search_alerts_or_incidents
  - o11y_get_apm_service_errors_and_requests
---
```

Below the YAML block, the markdown body defines the playbook:


| Section            | Purpose                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------- |
| **When to use**    | Symptoms or alert types that match                                                        |
| **Tool sequence**  | Ordered MCP steps with parameter hints (`service_name`, `environment_name`, `time_range`) |
| **Interpretation** | How to read the metrics                                                                   |
| **Do not**         | Guardrails (wrong params, skipping steps, inventing data)                                 |


Part 2 also loads `investigation-report` automatically. It is not selected by keywords, but defines the **final answer format** for every run.

{{< notice title="Important" style="primary" >}}
Tool names must match `mcp-doctor` exactly (`o11y_*` prefix). Time ranges belong inside a `params` object: `{"start": "-1h", "stop": "now"}`.
{{< /notice >}}

## Part 2 Lab: Complete the latency-spike skill

Complete `part2_agent/skills/latency-spike/SKILL.md` so the router selects `latency-spike` for latency, duration, p99, or slow-service signals.

Use the supplied `error-rate/SKILL.md` as the structural reference, but specify latency signals, tools, and interpretation.

Before you pick tools, review what the MCP servers expose. Your instance should match `troubleshooting-agent mcp-doctor` (see [Configure Environment]({{< relref "5-configure-agent-environment" >}})). The latency lab expects `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_latency`.

{{< collapse title="Splunk Observability MCP tools (o11y_*) - click to expand" >}}


| Tool                                       | What it's for                                                                             |
| ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `o11y_search_alerts_or_incidents`          | Find active or recent alerts and incidents by service, environment, detector, or keywords |
| `o11y_get_apm_service_errors_and_requests` | Error count and request volume time series for one service                                |
| `o11y_get_apm_service_latency`             | Latency percentiles (p50/p90/p99) for a service                                           |
| `o11y_get_apm_services`                    | Aggregate request, error, and latency metrics across services                             |
| `o11y_get_apm_service_dependencies`        | Upstream and downstream APM dependencies for a service                                    |
| `o11y_get_apm_exemplar_traces`             | Sample trace IDs linked to latency buckets or errors                                      |
| `o11y_get_apm_trace_tool`                  | Full trace detail for a specific `trace_id`                                               |
| `o11y_get_apm_environments`                | List APM environment names when the user did not specify one                              |
| `o11y_get_metric_names`                    | Discover metric names available for SignalFlow queries                                    |
| `o11y_get_metric_metadata`                 | Units and dimensions for a named metric                                                   |
| `o11y_generate_signalflow_program`         | Build a SignalFlow program from a natural-language description                            |
| `o11y_execute_signalflow_program`          | Run SignalFlow and return metric time series                                              |
| {{< /collapse >}}                          |                                                                                           |


{{< collapse title="Splunk Cloud MCP tools (splunk_*) - click to expand" >}}


| Tool                  | What it's for                                      |
| --------------------- | -------------------------------------------------- |
| `splunk_run_query`    | Run read-only SPL against Splunk Cloud             |
| `splunk_get_indexes`  | List indexes and storage tiers                     |
| `splunk_get_metadata` | Field names, event types, and sources for an index |
| `splunk_get_info`     | Splunk instance version and identity               |


Part 2 playbooks focus on `o11y_*` tools. Log search skills use `splunk_*` in Part 3.
{{< /collapse >}}

1. Open `skills/latency-spike/SKILL.md` in your editor.
2. Replace the `TODO` entries:
  - `description` one line: investigate APM latency alerts using service latency metrics
  - `alert_signals` include `latency`, `duration`, `p99`, and `slow`
  - `mcp_tools` list `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_latency`
3. **When to use**: when the alert or user message mentions high latency, duration, p99, or a slow service.
4. **Tool sequence**: two steps
  - Search alerts / incidents: capture `eventId` when present; **if empty, continue to step 2**
  - Get APM service latency: **required**; `service_name`, `environment_name`, and `time_range` in `params`
5. **Interpretation**: at least two bullets (for example: widening p50-to-p99 indicates tail latency; compare the current window with any baseline in the alert).
6. **Do not**: at least one rule (for example: do not stop after an empty alert search; always retrieve latency metrics).
7. Save the file.

{{< notice title="Check your routing" style="tip" >}}
The router counts how many `alert_signals` appear in your message. A prompt with `latency`, `p99`, or `slow` should select `latency-spike`.
{{< /notice >}}

## Run Part 2 with your skill

After saving `latency-spike/SKILL.md`, run this separate latency investigation:

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent/part2_agent
troubleshooting-agent chat "Investigate high p99 latency on paymentservice in the splunk-hipster environment"
```

{{% /tab %}}
{{< /tabs >}}

### Confirm in Splunk Agent Observability

1. Open the new `part2_agent` session in Agent Stream.
2. Expand `skill_router` : expect `load_skill:latency-spike` and `load_skill:investigation-report`.
3. Expand the main trace : expect at least `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_latency` under `tools` spans.

{{< notice title="Tip" style="tip" >}}
If the wrong skill loads, check `alert_signals` spelling and re-run with clearer keywords (`latency`, `p99`, `slow`) in the prompt.
{{< /notice >}}

## Part 2 Recap

- Ran the same high-error alert from Part 1 with the supplied `error-rate` playbook and compared Action Completion.
- Inspected `skill_router` to see the domain and reporting playbooks injected before the ReAct loop.
- Completed the `latency-spike` playbook with routing signals, required tools, interpretation guidance, and guardrails.
- Ran a separate latency investigation to verify that your playbook routed correctly and guided the expected MCP calls.
- Part 2 keeps the Part 1 ReAct graph; skills change the system prompt rather than the Python workflow.
- `alert_signals` selects one domain skill, while `investigation-report` supplies a consistent response format for every run.
- A playbook makes investigation steps more explicit and repeatable without becoming an MCP tool itself.
- Action Completion and trace evidence together show whether added guidance helped the agent finish more of the same high-error investigation.

---

**Next:** [Part 3 — Full Workflow]({{< relref "9-part3-full-workflow" >}}) — same alert through a structured LangGraph pipeline; skills load **per step**, not upfront like Part 2.