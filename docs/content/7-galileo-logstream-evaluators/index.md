---
title: "Configure Agent Stream Evaluators"
description: "Enable Action Completion on your agent stream to measure whether each investigation achieved its goal."
weight: 7
navTitle: "Configure Evaluators"
duration: "15 minutes"
---

Enable Action Completion, then apply it to the Part 1 session already in your stream. Splunk Agent Observability will score that existing investigation. **You do not need to re-run Part 1**.

Use **Action Completion** to compare whether Parts 1, 2, and 3 completed the same investigation goal or stopped at partial findings and suggested next steps.

## What are evaluators?

Evaluators are automated checks that score recorded agent sessions against a specific quality criterion. They review the session's prompt, tool-assisted investigation, and final response so you can assess agent behavior consistently instead of relying only on whether an answer sounds convincing.

Evaluators are important because agent responses can vary between runs. A repeatable score makes it easier to compare designs, identify incomplete behavior, and measure whether a playbook or structured workflow improved the result. A score is a diagnostic signal, not proof that an answer is correct. Always read its explanation and compare it with the trace, tool results, and final response.

Splunk Agent Observability offers evaluators for different aspects of agent quality. To keep this workshop focused, you will use only **Action Completion (SLM)**. It measures whether the session achieved the user's full goal, making it well suited to comparing the same high-error alert across Parts 1, 2, and 3.

## Before you start


| Requirement                                                               | Why                                                                        |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [Part 1 investigation completed]({{< relref "6-part1-baseline-agent" >}}) | Provides the session that Action Completion will score                     |
| `.env` Agent Observability settings saved                                 | Same `GALILEO_PROJECT` and `GALILEO_LOG_STREAM` you used in Part 1         |
| Splunk Agent Observability console access                                 | Open the shared project `sre-agent-wkshp`, then your instance Agent Stream |


Action Completion is available with an **SLM** (Luna) or an **LLM-as-a-judge**. This workshop uses **Action Completion (SLM)** for lower latency and cost. Your workshop instance should already have the required integration. If a session remains unscored after several minutes, ask your facilitator to verify **Integrations** in the Splunk Agent Observability console.

## Open your agent stream

1. Sign in to the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io).
2. Open **Projects** and select the shared project `sre-agent-wkshp`.
3. Select **Agent Stream** in the sidebar. Open the stream named after your instance (for example, `shw-2cb1` from `echo $INSTANCE`).
4. Confirm you see at least one session from Part 1 (for example, `chat-9265e3375c8b | part1_agent`).



## Configure Action Completion

1. From the agent stream view, click **Configure Evaluators**.
2. Search for **Action Completion**.
3. Turn on **Action Completion (SLM)**. Leave the other evaluators off for this workshop.
4. Click **Apply** to save your evaluator selection. The toggle does not take effect until you apply.
5. When Agent Observability asks whether to compute the evaluator on **past logs** or existing chats, apply it to those existing sessions. Your Part 1 investigation receives a score; do not click **Not Now**.

## Workshop evaluator

| Evaluator                                                                                   | Node type | What it tells you                                                                 |
| ------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------- |
| **[Action Completion](https://docs.galileo.ai/concepts/metrics/agentic/action-completion)** | Session   | Whether the agent fully achieved the investigation goal across the entire session |

Action Completion considers the user's goal, the tool-supported investigation, and the final response. A low score can indicate that the agent stopped after describing symptoms, asked the user to approve obvious next steps, contradicted tool output, or failed to address part of the request.

## Review scores on your Part 1 session

After you apply Action Completion and confirm scoring of existing chats, wait for its result to appear on the Part 1 session you already ran. Do not re-run the investigation just to get a score.

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

The center panel shows the chat query and final response. Open the **Evaluators** tab on the right and find **Action Completion (SLM)**. Review both its score and explanation.

Then open every `tools` span. Inspect MCP inputs, result status, and output JSON. Compare that evidence with the chat response to understand why the session did or did not complete the requested investigation. A detailed answer can still score poorly when the trace shows that the agent stopped before reaching a supported conclusion.

Verify the scored Part 1 session:

1. Wait for past-log scoring to finish on the Part 1 session you already ran.
2. Open Splunk Agent Observability **Agent Stream** and select that same session.
3. Expand the session's trace tree and inspect the tool sequence, inputs, results, and final answer.
4. Open the **Evaluators** tab and record the **Action Completion (SLM)** score and explanation.
5. Save the trace evidence, final conclusion, and Action Completion result for comparison with Parts 2 and 3.

{{< tabs >}}
{{% tab title="What good looks like" %}}

A strong run reaches a supported conclusion, addresses every part of the alert prompt, and receives a high **Action Completion** result.

A shallow run (missing environment) is still useful baseline data:

- One tool call such as `o11y_get_apm_environments`, followed by a request for the environment
- **Action Completion (SLM): 0%** because the scoped investigation never started

A deeper run can still score poorly. For example:

- The prompt includes the environment, and the agent calls `o11y_get_apm_services` and `o11y_get_apm_service_errors_and_requests`.
- The chat cites real values, such as 68 errors in the last hour.
- **Action Completion (SLM)** remains low, for example **2%**, because the agent stops at a summary and proposes next steps instead of completing the investigation.

{{% /tab %}}
{{% tab title="When scores are missing" %}}

If the Action Completion result does not appear:

1. Confirm you applied **Action Completion (SLM)** to **existing chats** / **past logs**, not **Not Now**
2. Check **Configure Evaluators** — the Action Completion toggle is still on and you clicked **Apply**
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

- The original Part 1 session shows an **Action Completion (SLM)** result. You do not need a second investigation.
- The result includes an explanation you can compare with the trace and final response.
- You saved the Part 1 result as the comparison point for Part 2 skills and the Part 3 structured graph.

---

**Next:** [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) — run the skill-injected agent, compare Action Completion, and author your own playbook.