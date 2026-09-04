---
title: "Configure Agent Stream Evaluators"
description: "Enable Agent Observability evaluators on your agent stream to score agent responses, tool selection, hallucination risk, and investigation quality."
weight: 7
navTitle: "Configure Evaluators"
duration: "15 minutes"
---

Enable agent stream evaluators, then apply them to the Part 1 session already in your stream. Splunk Agent Observability will score that existing investigation. You do not need to re-run Part 1.

Use the scores to verify:

- Whether the selected MCP tools match the alert and available signals
- Whether invalid inputs or execution errors caused tool failures
- Whether the final answer is grounded in tool output
- Whether the agent completed the investigation or stopped early

## Before you start


| Requirement                                                               | Why                                                                        |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [Part 1 investigation completed]({{< relref "6-part1-baseline-agent" >}}) | Provides the session that evaluators will score                            |
| `.env` Agent Observability settings saved                                 | Same `GALILEO_PROJECT` and `GALILEO_LOG_STREAM` you used in Part 1         |
| Splunk Agent Observability console access                                 | Open the shared project `sre-agent-wkshp`, then your instance Agent Stream |


Most built-in evaluators score traces with an **SLM** (Luna) or an **LLM-as-a-judge**. Select **SLM** when available. Your workshop instance should already have an LLM integration. If a session remains unscored after several minutes, ask your facilitator to verify **Integrations** in the Splunk Agent Observability console.

## Open your agent stream

1. Sign in to the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io).
2. Open **Projects** and select the shared project `sre-agent-wkshp`.
3. Select **Agent Stream** in the sidebar. Open the stream named after your instance (for example, `shw-2cb1` from `echo $INSTANCE`).
4. Confirm you see at least one session from Part 1 (for example, `chat-9265e3375c8b | part1_agent`).



## Configure evaluators

1. From the agent stream view, click **Configure Evaluators**.
2. Search or filter the evaluator list.
3. Turn on the evaluators in the tables below.
4. When the console offers **LLM** or **SLM** (Luna), select **SLM**. It provides the same scoring intent with lower workshop latency and cost.
5. Click **Apply** to save your evaluator selections. Toggles alone do not take effect until you apply.
6. When Agent Observability asks whether to compute evaluators on **past logs** or existing chats, apply them to those existing sessions. Your Part 1 investigation receives scores; do not click **Not Now**.

{{< notice title="Prefer SLM when available" style="tip" >}}
Many built-in evaluators have an **SLM** variant powered by Luna models. Use SLM unless your facilitator asks you to compare it with the full LLM judge. If no SLM option exists for an evaluator, use the LLM variant.
{{< /notice >}}

## Recommended evaluators

Enable evaluators from two categories that map directly to troubleshooting-agent quality. The platform applies each evaluator only to matching node types.

### Agent behavior — tools and progress

These evaluators score the investigation path, including tool choice, execution, and completion.


| Evaluator                                                                                             | Node type | What it tells you                                      | Workshop focus                                                                                  |
| ----------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| **[Tool selection quality](https://docs.galileo.ai/concepts/metrics/agentic/tool-selection-quality)** | LLM span  | Whether the model chose appropriate tools for the task | Did it call `o11y_get_apm_service_errors_and_requests` vs. skipping straight to a vague answer? |
| **[Tool error](https://docs.galileo.ai/concepts/metrics/agentic/tool-error)**                         | Tool span | Failures during tool execution                         | Catches MCP validation errors (for example, missing `environment_name`)                         |
| **[Action Completion](https://docs.galileo.ai/concepts/metrics/agentic/action-completion)**           | Session   | Whether the agent achieved the user's goal             | Did it actually investigate errors, or only ask clarifying questions?                           |


For Part 1, enable at least **Tool selection quality**, **Tool error**, and **Action Completion**.

### Response quality — hallucination and grounding

These evaluators compare the final answer and model behavior with the evidence and instructions available in the trace.


| Evaluator                                                                                                    | Node type | What it tells you                                                      | Workshop focus                                                                                       |
| ------------------------------------------------------------------------------------------------------------ | --------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **[Context Adherence](https://docs.galileo.ai/concepts/metrics/rag/generation-quality/context-adherence)**   | LLM span  | Closed-domain hallucination — claims not supported by provided context | Scores low when the model invents service names, error rates, or root causes not present in MCP JSON |
| **[Instruction Adherence](https://docs.galileo.ai/concepts/metrics/response-quality/instruction-adherence)** | LLM span  | Whether the model followed system instructions                         | Part 1's prompt requires using `o11y_`* tools for live data                                          |


For hallucination and prompt-compliance checks, enable **Context Adherence** and **Instruction Adherence**.

After you click **Apply**, reopen **Configure Evaluators** to confirm your selections. It should look similar to this:

{{< diagram src="images/applyEvals.png" alt="Splunk Agent Observability Configure Evaluators pane with workshop evaluators enabled" >}}

## Review scores on your Part 1 session

After you apply the evaluators and confirm scoring of existing chats, wait for scores to appear on the Part 1 session you already ran. Do not re-run the investigation just to get scores.

### Review the run in Splunk Agent Observability

When scoring finishes, open the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io) and navigate to:

1. **Project:** the shared workshop project (`sre-agent-wkshp`)
2. **Agent Stream:** your instance name from `echo $INSTANCE` (for example, `shw-2cb1`)
3. **Sessions:** open the Part 1 session you already ran (for example, `chat-9265e3375c8b | part1_agent`)

Select that session. A prompt with the environment often produces multiple tool rounds, even when the final answer remains incomplete:

```text
Agent (~20s)
├── Agent:agent
│   ├── should_continue
│   └── tools
│       └── o11y_get_apm_services
├── Agent:agent
│   ├── should_continue
│   └── tools
│       └── o11y_get_apm_service_errors_and_requests
├── Agent:agent
│   └── should_continue
```

If the environment is missing, expect a shallower trace, such as one `o11y_get_apm_environments` call followed by a request for the environment.

The center panel shows the chat query and final response. Open the **Evaluators** tab on the right to inspect groups such as **Agent Quality**. SLM evaluator names include **(SLM)**:

- **Tool Selection Quality (SLM):** whether the model chose appropriate MCP tools
- **Tool Error (SLM):** whether tool calls failed
- **Action Completion (SLM):** whether the agent completed the investigation instead of stopping at a summary or proposed next steps
- **Context Adherence (SLM):** whether claims are grounded in tool output
- **Instruction Adherence (SLM):** whether the agent followed the requirement to use `o11y_`* tools for live data

Open every `tools` span. Inspect MCP inputs, result status, output JSON, and span-level evaluators. Compare those details with the chat response. A detailed answer can still score poorly when the trace shows incomplete investigation or unsupported claims.

{{< diagram src="images/part1-galileo-trace-with-env.png" alt="Splunk Agent Observability Agent Stream showing a Part 1 session with evaluator scores in the Agent Quality panel" caption="Part 1 session after evaluators are applied to existing chats. Low action scores are common when the agent stops at suggested next steps." width="960" >}}

Verify the scored Part 1 session for `paymentservice` in environment `splunk-hipster`:

1. Wait for past-log scoring to finish on the Part 1 session you already ran.
2. Open Splunk Agent Observability **Agent Stream** and select that same session.
3. Expand the session's trace tree and confirm that multiple `tools` spans ran, not only an environment lookup.
4. For each MCP span, verify the input service, environment, and time window; then map chat claims to result JSON.
5. Open the **Evaluators** tab and record scores under **Agent Quality** (and other groups if present).
6. Save the tool sequence, failures, evidence, final conclusion, and scores for Parts 2 and 3.

{{< tabs >}}
{{% tab title="What good looks like" %}}

A strong Part 1 run in a data-rich environment might show:

- **Tool selection quality:** high because tools align with APM errors, traces, or dependencies
- **Tool error:** high because no calls failed
- **Action Completion:** moderate to high because the response reaches a supported root-cause summary
- **Context Adherence:** high because conclusions cite values and service names from MCP JSON
- **Instruction Adherence:** high because the agent used `o11y_`* tools for live data

A shallow run (missing environment) is still useful baseline data:

- One tool call such as `o11y_get_apm_environments`, followed by a request for the environment
- **Action Completion (SLM): 0%** because the scoped investigation never started

A deeper run can still score poorly. The screenshot above shows this pattern:

- The prompt includes the environment, and the agent calls `o11y_get_apm_services` and `o11y_get_apm_service_errors_and_requests`.
- The chat cites real values, such as 68 errors in the last hour.
- **Action Completion (SLM)** remains low, for example **2%**, because the agent stops at a summary and proposes next steps instead of completing the investigation.

Other weak patterns to watch for:

- **Tool selection quality:** low when the model answers without calling appropriate tools
- **Context Adherence:** low when a detailed root cause follows empty or failed tool output
- **Instruction Adherence:** low when the agent skips required `o11y_`* tools or ignores the system prompt

{{% /tab %}}
{{% tab title="When scores are missing" %}}

If evaluator scores do not appear:

1. Confirm you applied evaluators to **existing chats** / **past logs**, not **Not Now**
2. Check **Configure Evaluators** — the evaluator toggle is still on and you clicked **Apply**
3. Verify sampling is **100%** under **Evaluator Sampling** in the same pane
4. Wait a few minutes for past-log scoring to finish, then refresh the session
5. Ask your facilitator to confirm the **LLM integration** is configured in Splunk Agent Observability

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Tip" style="tip" >}}
Part 1 has no playbook, so results vary across runs and participants. A detailed response can still score poorly on **Action Completion** when the trace ends before the investigation reaches a supported conclusion.
{{< /notice >}}

## Exit checks

Before continuing, confirm that:

- The original Part 1 session shows results for the five configured evaluators where each evaluator applies. You do not need a second investigation.
- Tool spans expose the inputs, outputs, failures, and span-level scores needed to explain each evaluation.
- Your notes distinguish tool-selection or execution failures from unsupported final-answer claims.
- You saved the Part 1 scores as the comparison point for Part 2 skills and the Part 3 structured graph.

---

**Next:** [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) — run the skill-injected agent, compare evaluators, and author your own playbook.