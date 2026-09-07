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

Evaluators turn agent traces into measurable quality signals. Each evaluator applies a defined criterion—such as completing the requested action—to recorded evidence from an agent run. This helps you assess behavior consistently instead of relying only on whether a final answer sounds convincing.

### How evaluation works

1. **The agent runs.** Splunk Agent Observability records the user's request, model turns, tool calls and results, and final response in a session.
2. **An evaluator reads eligible evidence.** Some evaluators score an individual LLM or tool span. Others evaluate the whole session. **Action Completion is session-level**, so it can consider the original goal and the investigation's final outcome together.
3. **A judge applies one criterion.** The judge compares the recorded behavior with that evaluator's rubric.
4. **The evaluator returns a result.** Review both the score and its explanation. The explanation identifies the behavior that influenced the result and helps you locate supporting or conflicting evidence in the trace.

Evaluator sampling controls how many eligible sessions are scored after an evaluator is enabled. This workshop uses **100%** so every comparison run receives a result. Applying the evaluator to **past logs** backfills the Part 1 session that already exists; it does not require another agent run.

### SLM and LLM judges

Splunk Agent Observability can offer evaluator variants backed by a small language model (SLM) or a larger LLM-as-a-judge. Both apply an evaluator-specific rubric, but they differ in model size, latency, and cost.

**Luna** is Galileo's family of purpose-built SLMs for evaluation. Rather than using a larger general-purpose model for every score, Luna models are optimized to evaluate specific quality criteria. This provides practical benefits:

- **Faster feedback:** Lower inference latency helps scores appear sooner while you iterate on an agent.
- **Lower evaluation cost:** Efficient models make it practical to score more sessions, including past-log backfills and 100% workshop sampling.
- **Higher throughput:** More traces can be evaluated in the same period, which is useful for production-scale monitoring and repeated experiments.
- **Focused evaluation:** A model designed for a defined quality signal avoids using a larger general-purpose judge when the task does not require one.

This workshop uses **Action Completion (SLM)** so attendees can receive fast, economical feedback after each lab. Luna is still model-based evaluation: use the same evaluator variant for each comparison, read its explanation, and validate the result against the trace.

### Why evaluators matter

Agent responses can vary even when the prompt is unchanged. Evaluators provide a repeatable lens for comparing designs, finding incomplete behavior, and measuring whether a playbook or structured workflow changed the result. By using the same alert prompt in Parts 1, 2, and 3, you reduce task variation and make the comparison more meaningful.

A score is a diagnostic signal, not ground truth. A high score does not prove that every claim is correct, and a low score does not explain the root cause by itself. Always read the explanation, inspect the trace and tool results, and verify that the final response is supported by evidence.

Splunk Agent Observability offers evaluators for different aspects of agent quality. To keep this workshop focused, you will configure only **Action Completion (SLM)**. It measures whether the session achieved the user's full goal, making it well suited to comparing the same high-error alert across all three parts.

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

## Workshop recap

### What you did

- Configured **Action Completion (SLM)** as the workshop's single evaluator.
- Applied it to the existing Part 1 session instead of running the investigation again.
- Reviewed the score and explanation alongside the session trace, tool results, and final response.
- Saved the Part 1 result as the baseline for the same alert in Parts 2 and 3.

### What you learned

- Evaluators apply defined quality criteria to recorded agent evidence and can operate at span or session scope.
- SLM judges provide lower-latency, lower-cost feedback for repeated workshop runs.
- Action Completion measures whether the entire session achieved the user's goal, not whether the response merely sounded plausible.
- Evaluator results are diagnostic signals that require trace and evidence review rather than standalone proof of quality.

---

**Next:** [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) — run the skill-injected agent, compare Action Completion, and author your own playbook.