---
title: "Configure Agent Stream Evaluators"
description: "Enable Action Completion on your agent stream to measure whether each investigation achieved its goal."
weight: 7
navTitle: "Configure Evaluators"
duration: "15 minutes"
---

Use **Action Completion** to compare whether Parts 1, 2, and 3 completed the same investigation goal or stopped at partial findings and suggested next steps.

## What are Evaluators?

Evaluators turn agent traces into measurable quality signals. Each evaluator applies a defined criterion, such as completing the requested action, to recorded evidence from an agent run. This helps you assess behavior consistently instead of relying only on whether a final answer sounds convincing.

### How Evaluators work:

1. **The agent runs:** Splunk Agent Observability records the user's request, model turns, tool calls and results, and final response in a session.
2. **An evaluator reads eligible evidence:** Some evaluators score an individual LLM or tool span. Others evaluate the whole session.
3. **A judge applies one criterion:** The judge compares the recorded behavior with that evaluator's rubric.
4. **The evaluator returns a result:** Review both the score and its explanation. The explanation identifies the behavior that influenced the result and helps you locate supporting or conflicting evidence in the trace.

Evaluator sampling controls how many eligible sessions are scored after an evaluator is enabled. This workshop uses **100%,** so every comparison run receives a result.

### SLM and LLM judges

Splunk Agent Observability can offer evaluator variants backed by a small language model (SLM) or a larger LLM-as-a-judge. Both apply an evaluator-specific rubric, but they differ in model size, latency, and cost.

**Luna** is Splunk's purpose-built SLM for evaluation. Rather than using a larger general-purpose model for every score, Luna models are optimized to evaluate specific quality criteria. This provides practical benefits:

- **Faster feedback:** Lower inference latency helps scores appear sooner while you iterate on an agent.
- **Lower evaluation cost:** Efficient models make it practical to score more sessions, including past-log backfills and 100% workshop sampling.
- **Higher throughput:** More traces can be evaluated in the same period, which is useful for production-scale monitoring and repeated experiments.
- **Focused evaluation:** A model designed for a defined quality signal avoids using a larger general-purpose judge when the task does not require one.

This workshop uses **Action Completion (SLM)** so you can receive fast, economical feedback after each lab. Luna is still model-based evaluation: use the same evaluator variant for each comparison, read its explanation, and validate the result against the trace.

### Why Evaluators matter:

Agent **responses can vary** even when the prompt is **unchanged**. Evaluators provide a repeatable lens for comparing designs, finding incomplete behavior, and measuring whether a playbook or structured workflow changed the result.

A **score** is a diagnostic signal, not ground truth. A high score does not prove that every claim is correct, and a low score does not explain the root cause by itself. Always read the explanation, inspect the trace and tool results, and verify that the final response is supported by evidence.

Splunk Agent Observability offers evaluators for different aspects of agent quality. To keep this workshop focused, you will configure only **Action Completion (SLM)**. It measures whether the session achieved the user's full goal, making it well suited to comparing the same high-error alert across all three parts.

## Workshop evaluator


| Evaluator                                                                                   | Node type | What it tells you                                                                 |
| ------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------- |
| **[Action Completion](https://docs.galileo.ai/concepts/metrics/agentic/action-completion)** | Session   | Whether the agent fully achieved the investigation goal across the entire session |


Action Completion considers the user's goal, the tool-supported investigation, and the final response. A low score can indicate that the agent stopped after describing symptoms, asked the user to approve obvious next steps, contradicted tool output, or failed to address part of the request.

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
5. When Agent Observability asks whether to compute the evaluator on **past logs** or existing chats, apply it to those existing sessions.

## Review scores on your Part 1 session

After you apply Action Completion and confirm scoring of existing chats, wait for its result to appear on the Part 1 session you already ran. Do not re-run the investigation just to get a score.

A strong run reaches a supported conclusion, addresses every part of the alert prompt, and receives a high **Action Completion** result.

A shallow run (missing environment) is still useful baseline data:

- One tool call such as `o11y_get_apm_environments`, followed by a request for the environment
- **Action Completion (SLM): 0%** because the scoped investigation never started

A deeper run can still score poorly. For example:

- The prompt includes the environment, and the agent calls `o11y_get_apm_services` and `o11y_get_apm_service_errors_and_requests`.
- The chat cites real values, such as 68 errors in the last hour.
- **Action Completion (SLM)** remains low, for example **2%**, because the agent stops at a summary and proposes next steps instead of completing the investigation.

If the Action Completion result does not appear:

1. Confirm you applied **Action Completion (SLM)** to **existing chats** / **past logs**, not **Not Now**
2. Check **Configure Evaluators**: the Action Completion toggle is still on and you clicked **Apply**
3. Verify sampling is **100%** under **Evaluator Sampling** in the same pane
4. Wait a few minutes for past-log scoring to finish, then refresh the session
5. Ask your facilitator to confirm the **LLM integration** is configured in Splunk Agent Observability

{{< notice title="Tip" style="tip" >}}
Part 1 has no playbook, so results vary across runs and participants. A detailed response can still score poorly on **Action Completion** when the trace ends before the investigation reaches a supported conclusion.
{{< /notice >}}

## Configure Evaluators Recap

- Configured **Action Completion (SLM)** as the workshop's single evaluator.
- Applied it to the existing Part 1 session.
- Reviewed the score alongside the session trace, tool results, and final response.

---

**Next:** [Part 2: Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) — run the skill-injected agent, compare Action Completion, and author your own playbook.