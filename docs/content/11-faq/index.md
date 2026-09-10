---
title: "FAQ"
description: "Forty questions covering the overall workshop plus Parts 1–3 — setup, traces, skills, evaluators, and the four-node workflow."
weight: 11
navTitle: "FAQ"
---

Use these answers to diagnose lab runs. The workshop defaults are service `paymentservice` and environment `splunk-hipster`. Keep the same [Agent Observability](https://console.multitenant.galileocloud.io) project and agent stream across Parts 1–3.

{{< notice title="How to use this page" style="tip" >}}
Start with [General](#general) for setup and CLI issues. Use the Part 1–3 sections while you are in that exercise. For playbook authoring background, see [AI Skills]({{< relref "2-ai-skills" >}}).
{{< /notice >}}

## General

### 1. What Will I Build in This Workshop?

You will build and compare three troubleshooting-agent implementations: a baseline ReAct agent, the same loop with `SKILL.md` playbooks, and a four-node LangGraph workflow. All three use the `troubleshooting-agent` CLI, integrations in `shared/workshop_shared/`, and the same Observability demo service. That keeps the alert context stable while you compare tool calls, evidence, traces, and evaluator results.

### 2. How Are Parts 1, 2, and 3 Different?


| Part                                                   | Agent shape       | What is added                                                             |
| ------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------- |
| **[Part 1]({{< relref "6-part1-baseline-agent" >}})**  | Single ReAct loop | MCP tools only: no playbooks                                              |
| **[Part 2]({{< relref "8-part2-skill-playbooks" >}})** | Same ReAct loop   | Keyword-injected `SKILL.md` playbooks                                     |
| **[Part 3]({{< relref "9-part3-full-workflow" >}})**   | Four-node graph   | identify → categorize → investigate → report, with skills loaded per node |




### 3. Where Do I Run Commands, and Why Does the Directory Matter?

Run `troubleshooting-agent` from `part1_agent/`, `part2_agent/`, or `part3_agent/`. The current directory selects the agent implementation. If the trace shape or loaded skills do not match the exercise, check `pwd` first.

### 4. I Opened a New SSH Session and `troubleshooting-agent` Is Not Found. What Should I Do?

Activate the virtualenv every time:

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
```

Your prompt should show `(.venv)`. Then `cd` into the part directory. Full setup is in [Configure Environment]({{< relref "5-configure-agent-environment" >}}).

If `.venv` does not exist or activation does not restore the command, this instance has not completed its first-time setup. Return to Configure Environment and run the dependency installation before continuing.

### 5. How Do I Personalize Agent Observability so I Can Find My Traces?

Run `cp .env.example .env` during [Configure Environment]({{< relref "5-configure-agent-environment" >}}). The example file already enables Galileo and selects the shared project `sre-agent-wkshp`; credentials remain in the workshop instance's environment and should not be copied into `.env`.

The agent derives `GALILEO_LOG_STREAM` from `$INSTANCE` (for example, `shw-2cb1`). Do not add or override that setting unless your facilitator asks. Keeping the same stream across Parts 1–3 places all of your sessions together for comparison.

### 6. `doctor` or `mcp-doctor` Failed. What Next?

Both must report **Ready** before Part 1:

```bash
cd ~/troubleshooting-agent/part1_agent
troubleshooting-agent doctor
troubleshooting-agent mcp-doctor
```

`doctor` checks the workshop LLM proxy and model. `mcp-doctor` checks both MCP integrations; expect about 12 `o11y_*` tools and 9 `splunk_*` tools. Do not continue on a partial result. Check `.env`, confirm the current part directory, and re-run once. If either command still fails, give the facilitator the failing check and exact error; common causes are credentials or MCP gateway access.

### 7. Why Do My Prompts Need `paymentservice` and `splunk-hipster`?

The supplied workshop prompts already include these exact APM entity names. When writing a custom prompt, keep the same spelling and include both values. A missing environment may cause a discovery call followed by a clarification stop, while a misspelled service can return an empty or unrelated series. Treat empty data as an input or scope problem until the tool arguments, environment, and time window are verified.

### 8. Where Do I Review a Run After It Finishes?

Correlate the run in three places:

1. **Terminal**: live `[n] MCP ...` lines for `o11y_`* and, in Part 3, `splunk_*` calls (`AGENT_LOG_TRACE=true` is the default)
2. **JSONL**:  `shared/logs/investigations/<id>.jsonl` (path printed as `Log file:`)
3. **Splunk Agent Observability**: project `sre-agent-wkshp` → Agent Stream → session named like `chat-… | part1_agent`

Terminal IDs use `chat:`; console session names use `chat-`.

### 9. When Do I Enable Evaluators, and Should I Score My First Part 1 Run?

After the first Part 1 investigation, enable only **Action Completion (SLM)** and apply it to **existing chats** / **past logs**. Do not click **Not Now**, and do not re-run Part 1 just to get a score. The toggle does nothing until you click **Apply**.

If the result stays empty, confirm the evaluator is still enabled, **Apply** was clicked, and **Evaluator Sampling** is 100%. Wait a few minutes for past-log scoring, then refresh the session. If it is still missing, ask a facilitator to confirm the **LLM integration** in Splunk Agent Observability.

Details: [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}).

### 10. Can I Use This Agent on Live Incidents After the Workshop?

No. Part 3 demonstrates a real graph, skills, and MCP calls, but it uses CLI mock alerts, per-run MCP sessions, and workshop credentials exposed to the process on a shared host. It has not established production availability, security, tenancy, or safety. Keep it read-only. Before live use, implement authenticated intake, typed alert payloads, exact time-window handling, bounded retries and timeouts, secret management, evidence checks, tenant isolation, and human authorization for actions.

See [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}).

## Part 1: Baseline Agent



### 11. What Is the Part 1 Agent Actually Doing?

A LangGraph **ReAct** loop: `agent` (LLM) → `tools` (MCP) → `should_continue` → repeat until it answers. It has **no skills**. The system prompt in `part1_agent/prompt.py` requires `o11y_`* tools for live data; the model still chooses which tools and when.

Full exercise: [Part 1: Baseline Agent]({{< relref "6-part1-baseline-agent" >}}).

### 12. What Command Should I Run First?

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

Reuse this short prompt in Part 2 for a direct Action Completion comparison. Part 3 uses a mock-alert version with additional rule context for its structured workflow.

### 13. Why Do Two People Get Different Part 1 Answers on the Same Prompt?

Part 1 has no playbook, so model sampling can change tool order, depth, and stopping behavior. Compare the actual tool inputs and results; do not assume either answer is better because it is longer. Part 1 is a baseline, not a reference investigation.

### 14. How Do I Tell If the Answer Is Grounded vs. Hallucinated?

Open each MCP span and map the reply's service, time window, metric values, trace IDs, and causal claims to tool results. If a value or cause has no supporting result, mark it unsupported. Action Completion does not replace manual evidence inspection.

### 15. Which Tools Should I Expect in Part 1?

Anything from the Observability MCP list (`mcp-doctor`). Common calls include `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`. A baseline run often **skips** traces, logs, and dependency correlation. Missing tools is a finding, not necessarily a setup failure.

### 16. Time Range or Environment Errors on MCP Calls — What Is Wrong?

Inspect the failed tool input. Use exact APM names (`paymentservice`, `splunk-hipster`). For time windows, `params.time_range` must be an object such as `{"start": "-1h", "stop": "now"}`—not a bare string and not top-level `start` / `stop` fields. A missing `environment_name` also causes validation failure. Correct the input and rerun.

### 17. I Cleared the Terminal. How Do I Recover the Trace?

Open the newest JSONL:

```bash
ls -t ~/troubleshooting-agent/shared/logs/investigations/*.jsonl | head -1
```

You can also reopen the existing `part1_agent` session in Splunk Agent Observability. Do not rerun the investigation only to recover its trace; a rerun creates a different investigation and session.

### 18. I Cannot Find My Session in Agent Observability. Where Should I Look?

Confirm the Agent Stream name is your instance id (`echo $INSTANCE`, for example `shw-2cb1`). Filter sessions by suffix `part1_agent`. Refresh after the run finishes — traces upload at the end. Keep the console tab open for later parts.

### 19. What Does a Typical Part 1 Agent Observability Tree Look Like?

A repeating ReAct shape, not named workflow stages:

```text
Agent
├── Agent:agent
├── should_continue
├── tools → o11y_…
├── Agent:agent
└── should_continue
```

Click `tools` to inspect arguments and JSON. Evaluators are empty until [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}).

### 20. What Notes Should I Save Before Leaving Part 1?

Record the prompt, session name, tool sequence, each tool's service/environment/time window, empty or failed results, and whether the conclusion is supported by MCP output. Reuse the same short prompt in Part 2. Part 3 keeps the high-error scenario but adds mock-alert rule context for the structured workflow.

## Part 2: Skill Playbooks



### 21. Did the Graph Change in Part 2?

No. Part 2 is still a single ReAct loop. Skills are markdown playbooks **injected into the system prompt** before the loop. They are not MCP tools and do not appear under `Agent` → `tools`.

Full exercise: [Part 2: Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}).

### 22. How Does the Agent Pick a Playbook?

A keyword router scores `alert_signals` in each skill’s YAML against your chat/alert text. The winning **domain** skill is injected. `investigation-report` always loads (report format) and is not keyword-matched.

Examples: the shared high-error alert → supplied `error-rate` + `investigation-report`; the separate latency lab prompt → attendee-built `latency-spike` + `investigation-report`.

### 23. Where Do I Confirm Skills Actually Loaded?

1. **Terminal**: `[N] Skill loaded: error-rate` for the shared comparison, or `latency-spike` for the separate lab (plus `investigation-report`)
2. **Agent Observability**: a `skill_router` trace that is a **sibling** of `Agent`, not nested inside it; expand `load_skill:…`
3. **Chat JSON**:  system message includes `## Active playbook` and `## Reporting requirements`

Do not look for `load_skill` under MCP `tools` spans.

### 24. What Investigation Should I Run First in Part 2?

```bash
cd ~/troubleshooting-agent/part2_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

This is the same prompt used in Part 1. Expect the supplied `error-rate` skill and this tool order:

1. `o11y_search_alerts_or_incidents`
2. `o11y_get_apm_service_errors_and_requests`

An empty alert list is not a stopping condition. The agent should still retrieve error/request metrics and format the final reply with `investigation-report` headings. Stopping after alert search or asking whether to pull metrics is an incomplete run.

### 25. What Is Inside a `SKILL.md`?

YAML front matter: `name`, `description`, `alert_signals`, `mcp_tools` (and optional `rule_patterns`). Body: **When to use**, **Tool sequence**, **Interpretation**, **Do not**. Copy `part2_agent/skills/_template/SKILL.md` or follow the supplied `skills/error-rate/SKILL.md`. Tool names must match `mcp-doctor` exactly (`o11y_`*).

### 26. What Do I Need to Finish for the Latency Lab?

Edit `part2_agent/skills/latency-spike/SKILL.md`:

- Signals: `latency`, `duration`, `p99`, and `slow`
- Tools: `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_latency`
- Sequence: search alerts (continue if empty) → **required** latency metrics with `service_name`, `environment_name`, and `time_range` in `params`
- At least two interpretation bullets and one **Do not** rule

Then run:

```bash
troubleshooting-agent chat "Investigate high p99 latency on paymentservice in the splunk-hipster environment"
```

This separate run validates your authored skill; it is not the Parts 1–3 Action Completion comparison.

### 27. The Wrong Skill Loaded. How Do I Fix Routing?

The router counts overlapping `alert_signals`. For the latency lab, add clearer keywords (`latency`, `p99`, `slow`) and check spelling in YAML (lowercase). After saving `SKILL.md`, re-run — skills are read at the start of each investigation.

### 28. Why Must I Keep the Same `GALILEO_LOG_STREAM` in Part 2?

The agent derives the stream from `$INSTANCE`. Leave it unset (or unchanged) so Part 1 and Part 2 sessions sit in one Agent Stream. Filter by suffix `part2_agent` vs `part1_agent`. Setting a different stream splits the comparison the lab is built around.

### 29. Should Evaluator Scores Be Perfect in Part 2?

No. Compare **Action Completion (SLM)** and its explanation with Part 1 for the same high-error alert. Inspect the trace behind any change; a higher score does not prove that the investigation or conclusion is correct.

### 30. What Does Part 2 Deliberately Leave for Part 3?

Still one ReAct loop; one domain skill + report; no mandatory Splunk log search; keyword routing instead of a product categorizer; skills all injected up front in `skill_router`. Part 3 adds the four-node graph, per-step skill loading, a required `splunk_*` log search, and mock-alert context containing the service, environment, and rule name.

## Part 3: Full Workflow



### 31. How Is Part 3 Different from Part 2 If Both Use `SKILL.md`?

Same playbook **file format**, different **orchestration**. Part 2 injects all selected skills before the first LLM turn. Part 3 loads the right skill **when that graph node runs**. You should **not** see a top-level `skill_router` in Part 3.

Full exercise: [Part 3: Full Workflow]({{< relref "9-part3-full-workflow" >}}).

### 32. What Are the Four Nodes and Which Skills Load?


| Node            | Skill(s)                                                          | Role                                                        |
| --------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| **identify**    | `get-alerts-or-incidents`                                         | Confirm the alert and capture IDs                           |
| **categorize**  | Routing only (`route_skill:…`)                                    | Python picks APM / IM / RUM / Synthetics — no full playbook |
| **investigate** | Product skill (e.g. `troubleshoot-apm-incidents`) + `search-logs` | O11y steps + mandatory Splunk log search                    |
| **report**      | `troubleshoot-report`                                             | Structured handoff **after** evidence is gathered           |


Investigate also injects `search-logs/indexes.md` so the agent does not default to index `main`.

### 33. What Chat Command Should I Use for Part 3?

```bash
cd ~/troubleshooting-agent/part3_agent
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. Rule: obs1386 | sre agent | high error rate. Find root cause of the high error rate."
```

No Slack app is required. The mock prompt mirrors a real alert thread and gives **identify** the service, environment, and rule name.

### 34. What Should the Agent Observability Tree Look Like?

Session name ends in `part3_agent`. Expand `part3_investigation`:

```text
Session: chat-… | part3_agent
└── part3_investigation
    ├── identify
    │   ├── load_skill:get-alerts-or-incidents
    │   ├── identify_llm
    │   └── identify_tools → o11y_…
    ├── categorize
    │   └── route_skill:troubleshoot-apm-incidents
    ├── investigate
    │   ├── load_skill:troubleshoot-apm-incidents
    │   ├── load_skill:search-logs
    │   ├── investigate_llm
    │   └── investigate_tools → o11y_… / splunk_…
    └── report
        ├── load_skill:troubleshoot-report
        └── report_llm
```

Part 3 has no top-level `skill_router`. Named nodes should own the work; a `skill_router` or repeated generic `Agent:Agent` spans indicates that you ran the wrong agent.

### 35. Why Is `troubleshoot-report` Not Loaded at the Start Like Part 2’s `investigation-report`?

Part 3 loads the report skill only after the investigate node returns MCP evidence. This separates evidence collection from presentation. It is a useful workflow property, not by itself a production control.

### 36. How Does Part 3 Choose the Product Playbook If Not by Keywords?

A **Python categorizer** inspects the resolved alert payload (APM / IM / RUM / Synthetics). For rule `obs1386 | sre agent | high error rate`, expect APM → `troubleshoot-apm-incidents`. Categorize shows `route_skill:…` (decision), not prompt injection.

### 37. I Still Do Not See Splunk Log Tools. Is That a Failure?

Part 3's investigate node requires at least one `splunk_*` log search, typically `splunk_run_query` and sometimes `splunk_get_indexes` or `splunk_get_metadata`. `mcp-doctor` lists both the Observability and Splunk Cloud MCP integrations, but Parts 1 and 2 investigations focus on `o11y_*` tools.

If no `splunk_*` call appears, confirm that you ran from `part3_agent`. If the call succeeded but returned no events, verify the index, service fields, alert-aligned time window, authorization, ingestion delay, and result limits. An empty result is an observation, not proof that no logs exist; stale entries in `search-logs/indexes.md` can also create false negatives.

### 38. Same Tools as Part 2. Why Does the Trace Look so Different?

MCP calls can overlap (`o11y_search_alerts_or_incidents`, error metrics). The teaching point is **when** skills enter the prompt and **which node** owns the work. Compare skill timing and graph shape, not only tool names.

### 39. How Should I Compare Evaluator Scores Across Parts?

Use one Agent Stream and select sessions ending in `part1_agent`, `part2_agent`, and `part3_agent`. Parts 1 and 2 use the same short error prompt, so they provide the direct same-prompt comparison. Part 3 investigates the same high-error scenario with additional service, environment, and rule context for the structured workflow.

Compare **Action Completion (SLM)** and its explanation, then inspect tool inputs, results, evidence, skill timing, and failure handling. Part 3 should include a log search and a report produced after evidence collection. Because its prompt contains richer alert context, do not attribute every score difference only to the graph design.

### 40. What Must I Verify Before Leaving Part 3?

Confirm that:

- `part3_investigation` contains the four named nodes rather than a generic ReAct loop.
- The alert was anchored by service, environment, and rule, and the categorizer selected `troubleshoot-apm-incidents`.
- `investigate_tools` contains both O11y evidence and at least one Splunk log search with the intended scope and time window.
- Every causal claim maps to a tool result.
- Any claim that the incident is resolved uses post-alert evidence; an empty current-alert result is not enough.
- Skill loading occurs under the node that consumes each playbook.

Part 2 demonstrates playbook authoring; Part 3 demonstrates structured orchestration. Neither exercise establishes production readiness.

For hardening after the lab, see [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}).