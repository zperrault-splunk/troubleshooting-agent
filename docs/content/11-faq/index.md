---
title: "FAQ"
description: "Forty questions covering the overall workshop plus Parts 1–3 — setup, traces, skills, evaluators, and the four-node workflow."
weight: 11
navTitle: "FAQ"
---

Use these answers to diagnose lab runs. The workshop defaults are service **`paymentservice`** and environment **`splunk-hipster`**. Keep the same [Agent Observability](https://console.multitenant.galileocloud.io) project and agent stream across Parts 1–3.

{{< notice title="How to use this page" style="tip" >}}
Start with [General](#general) for setup and CLI issues. Use the Part 1–3 sections while you are in that exercise. For playbook authoring background, see [AI Skills]({{< relref "2-ai-skills" >}}).
{{< /notice >}}

## General

### 1. What Will I Build in This Workshop?

You will build and compare three troubleshooting-agent implementations: a baseline ReAct agent, the same loop with `SKILL.md` playbooks, and a four-node LangGraph workflow. All three use the `troubleshooting-agent` CLI, integrations in `shared/workshop_shared/`, and the same Observability demo service. That keeps the alert context stable while you compare tool calls, evidence, traces, and evaluator results.

### 2. How Are Parts 1, 2, and 3 Different?

| Part | Agent shape | What is added |
|------|-------------|---------------|
| **[Part 1]({{< relref "6-part1-baseline-agent" >}})** | Single ReAct loop | MCP tools only — no playbooks |
| **[Part 2]({{< relref "8-part2-skill-playbooks" >}})** | Same ReAct loop | Keyword-injected `SKILL.md` playbooks |
| **[Part 3]({{< relref "9-part3-full-workflow" >}})** | Four-node graph | identify → categorize → investigate → report, with skills loaded per node |

### 3. Where Do I Run Commands, and Why Does the Directory Matter?

Run `troubleshooting-agent` from `part1_agent/`, `part2_agent/`, or `part3_agent/`. The current directory selects the agent implementation. If the trace shape or loaded skills do not match the exercise, check `pwd` first.

### 4. I Opened a New SSH Session and `troubleshooting-agent` Is Not Found. What Should I Do?

Activate the virtualenv every time:

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
```

Your prompt should show `(.venv)`. Then `cd` into the part directory. Full setup is in [Configure Environment]({{< relref "5-configure-agent-environment" >}}).

### 5. How Do I Personalize Agent Observability so I Can Find My Traces?

Copy `.env.example` to `.env` and set:

- `ENABLE_GALILEO=true`
- `GALILEO_PROJECT="sre-agent-wkshp"`
- `GALILEO_LOG_STREAM="sre-agent-wkshp-$INSTANCE"` — replace `$INSTANCE` with the value from `echo $INSTANCE` (for example `sre-agent-wkshp-shw-2cb1`)

Use the **same** project and agent stream for Parts 1–3. Do not change `GALILEO_LOG_STREAM` when you switch parts. Your instance name comes from [Connect to EC2]({{< relref "3-connect-ec2" >}}).

### 6. `doctor` or `mcp-doctor` Failed. What Next?

Both must report **Ready** before Part 1:

```bash
cd ~/troubleshooting-agent/part1_agent
troubleshooting-agent doctor
troubleshooting-agent mcp-doctor
```

`doctor` checks the workshop LLM proxy and model. `mcp-doctor` checks Observability MCP; expect about 12 `o11y_*` tools. Do not continue on a partial result. Check `.env`, confirm the current part directory, and re-run once. If either command still fails, give the facilitator the failing check and exact error; common causes are credentials or MCP gateway access.

### 7. Why Do My Prompts Need `paymentservice` and `splunk-hipster`?

Those are the exact workshop APM entity names. Omitting the environment may cause a discovery call followed by a clarification stop. A misspelled service can return an empty or unrelated series. Treat empty data as an input or scope problem until the tool arguments, environment, and time window are verified.

### 8. Where Do I Review a Run After It Finishes?

Correlate the run in three places:

1. **Terminal** — live `[n] MCP o11y_...` lines (`AGENT_LOG_TRACE=true` is the default)
2. **JSONL** — `shared/logs/investigations/<id>.jsonl` (path printed as `Log file:`)
3. **Splunk Agent Observability** — project `sre-agent-wkshp` → Agent Stream → session named like `chat-… | part1_agent`

Terminal IDs use `chat:`; console session names use `chat-`.

### 9. When Do I Enable Evaluators, and Should I Score My First Part 1 Run?

Enable evaluators **after** the first Part 1 investigation, then click **Not Now** when asked to score past logs. That keeps session 1 as a trace-only baseline. Prefer **SLM (Luna)** over full LLM judges. Toggles do nothing until you click **Apply**. If scores stay empty, ask a facilitator to check Integrations.

Details: [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}).

### 10. Can I Use This Agent on Live Incidents After the Workshop?

No. Part 3 demonstrates a real graph, skills, and MCP calls, but it uses CLI mock alerts, per-run MCP sessions, and `.env` credentials on a shared host. It has not established production availability, security, tenancy, or safety. Keep it read-only. Before live use, implement authenticated intake, typed alert payloads, exact time-window handling, bounded retries and timeouts, secret management, evidence checks, tenant isolation, and human authorization for actions.

See [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}).

## Part 1 — Baseline Agent

### 11. What Is the Part 1 Agent Actually Doing?

A LangGraph **ReAct** loop: `agent` (LLM) → `tools` (MCP) → `should_continue` → repeat until it answers. It has **no skills**. The system prompt in `part1_agent/prompt.py` requires `o11y_*` tools for live data; the model still chooses which tools and when.

Full exercise: [Part 1 — Baseline Agent]({{< relref "6-part1-baseline-agent" >}}).

### 12. What Command Should I Run First?

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

You can paste facilitator alert text instead, but always include service and environment.

### 13. Why Do Two People Get Different Part 1 Answers on the Same Prompt?

Part 1 has no playbook, so model sampling can change tool order, depth, and stopping behavior. Compare the actual tool inputs and results; do not assume either answer is better because it is longer. Part 1 is a baseline, not a reference investigation.

### 14. How Do I Tell If the Answer Is Grounded vs. Hallucinated?

Open each MCP span and map the reply's service, time window, metric values, trace IDs, and causal claims to tool results. If a value or cause has no supporting result, mark it unsupported. **Context Adherence** helps identify this after evaluators are enabled, but it does not replace trace inspection.

### 15. Which Tools Should I Expect in Part 1?

Anything from the Observability MCP list (`mcp-doctor`). Common calls include `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`. A baseline run often **skips** traces, logs, and dependency correlation. Missing tools is a finding, not necessarily a setup failure.

### 16. Time Range or Environment Errors on MCP Calls — What Is Wrong?

Inspect the failed tool input. Use exact APM names (`paymentservice`, `splunk-hipster`). Time ranges belong in a `params` object, for example `{"start": "-1h", "stop": "now"}`. A missing `environment_name` or a top-level `start`/`stop` causes validation failure. Correct the input and re-run; **Tool error** evaluators can flag the failure after they are enabled.

### 17. I Cleared the Terminal. How Do I Recover the Trace?

Open the newest JSONL:

```bash
ls -t ~/troubleshooting-agent/shared/logs/investigations/*.jsonl | head -1
```

Or re-run the same chat command. You get a new investigation ID and Agent Observability session; the flow is the same.

### 18. I Cannot Find My Session in Agent Observability. Where Should I Look?

Confirm `GALILEO_LOG_STREAM` matches the Agent Stream name (includes your instance id). Filter sessions by suffix `part1_agent`. Refresh after the run finishes — traces upload at the end. Keep the console tab open for later parts.

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

Record the prompt, session name, tool sequence, each tool's service/environment/time window, empty or failed results, and whether the conclusion is supported by MCP output. Reuse the same alert in Parts 2 and 3 so the comparison is meaningful.

## Part 2 — Skill Playbooks

### 21. Did the Graph Change in Part 2?

No. Part 2 is still a single ReAct loop. Skills are markdown playbooks **injected into the system prompt** before the loop. They are not MCP tools and do not appear under `Agent` → `tools`.

Full exercise: [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}).

### 22. How Does the Agent Pick a Playbook?

A keyword router scores `alert_signals` in each skill’s YAML against your chat/alert text. The winning **domain** skill is injected. `investigation-report` always loads (report format) and is not keyword-matched.

Example: “Investigate **latency** on paymentservice…” → `latency-spike` + `investigation-report`.

### 23. Where Do I Confirm Skills Actually Loaded?

1. **Terminal** — `[N] Skill loaded: latency-spike` (and `investigation-report`)
2. **Agent Observability** — a **`skill_router`** trace that is a **sibling** of `Agent`, not nested inside it; expand `load_skill:…`
3. **Chat JSON** — system message includes `## Active playbook` and `## Reporting requirements`

Do not look for `load_skill` under MCP `tools` spans.

### 24. What Latency Investigation Should I Run First?

```bash
cd ~/troubleshooting-agent/part2_agent
troubleshooting-agent chat "Investigate latency on paymentservice in the splunk-hipster environment"
```

Expect `o11y_search_alerts_or_incidents` followed by `o11y_get_apm_service_latency`. An empty alert search is valid for a CLI run and must not stop the investigation. The latency call still needs the intended service, environment, and time range, and the reply must use `investigation-report` headings.

### 25. What Is Inside a `SKILL.md`?

YAML front matter: `name`, `description`, `alert_signals`, `mcp_tools` (and optional `rule_patterns`). Body: **When to use**, **Tool sequence**, **Interpretation**, **Do not**. Copy `part2_agent/skills/_template/SKILL.md` or follow `skills/latency-spike/SKILL.md`. Tool names must match `mcp-doctor` exactly (`o11y_*`).

### 26. What Do I Need to Finish for the Error-Rate Lab?

Edit `part2_agent/skills/error-rate/SKILL.md`:

- Signals: at least `error`, `errors`, `5xx`
- Tools: `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`
- Sequence: search alerts (continue if empty) → **required** error/request metrics with `service_name`, `environment_name`, and `time_range` in `params`
- At least two interpretation bullets and one **Do not** (for example: no root cause without tool evidence)

Then run:

```bash
troubleshooting-agent chat "Investigate elevated 5xx errors on paymentservice in the splunk-hipster environment"
```

### 27. The Wrong Skill Loaded. How Do I Fix Routing?

The router counts overlapping `alert_signals`. Add clearer keywords (`5xx`, `errors`, `error rate`) to the prompt and check spelling in YAML (lowercase). After saving `SKILL.md`, re-run — skills are read at the start of each investigation.

### 28. Why Must I Keep the Same `GALILEO_LOG_STREAM` in Part 2?

So Part 1 and Part 2 sessions sit in one Agent Stream. Filter by suffix `part2_agent` vs `part1_agent`. Changing the stream splits the comparison the lab is built around.

### 29. Should Evaluator Scores Be Perfect in Part 2?

No. Compare the scores with Part 1 for the same alert. Check Tool selection quality for the required calls, Action Completion for premature stops, Context Adherence for claims supported by MCP results, and Instruction Adherence for the required report format. Inspect the trace behind any score change; a higher aggregate score does not prove a correct investigation.

### 30. What Does Part 2 Deliberately Leave for Part 3?

Still one ReAct loop; one domain skill + report; no mandatory Splunk log search; keyword routing instead of a product categorizer; skills all injected up front in `skill_router`. Part 3 adds the four-node graph, per-step skill load, `splunk_*` log search, and stricter alert anchoring (`detectorId` / rule name).

## Part 3 — Full Workflow

### 31. How Is Part 3 Different from Part 2 If Both Use `SKILL.md`?

Same playbook **file format**, different **orchestration**. Part 2 injects all selected skills before the first LLM turn. Part 3 loads the right skill **when that graph node runs**. You should **not** see a top-level `skill_router` in Part 3.

Full exercise: [Part 3 — Full Workflow]({{< relref "9-part3-full-workflow" >}}).

### 32. What Are the Four Nodes and Which Skills Load?

| Node | Skill(s) | Role |
|------|----------|------|
| **identify** | `get-alerts-or-incidents` | Confirm the alert and capture IDs |
| **categorize** | Routing only (`route_skill:…`) | Python picks APM / IM / RUM / Synthetics — no full playbook |
| **investigate** | Product skill (e.g. `troubleshoot-apm-incidents`) + `search-logs` | O11y steps + mandatory Splunk log search |
| **report** | `troubleshoot-report` | Structured handoff **after** evidence is gathered |

Investigate also injects `search-logs/indexes.md` so the agent does not default to index `main`.

### 33. What Chat Command Should I Use for Part 3?

```bash
cd ~/troubleshooting-agent/part3_agent
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. DetectorId HNcv52_AwAA. Rule: SRE Agent - PaymentService High Error Rate. Find root cause of the high error rate and confirm whether it is resolved."
```

No Slack app is required. The mock prompt mirrors a real alert thread so **identify** can anchor on detector ID and rule name.

### 34. What Should the Agent Observability Tree Look Like?

Session name ends in `part3_agent`. Expand `part3_investigation`:

```text
part3_investigation
├── identify    → load_skill:get-alerts-or-incidents, identify_llm, identify_tools
├── categorize  → route_skill:troubleshoot-apm-incidents
├── investigate → load_skill:troubleshoot-apm-incidents, load_skill:search-logs, … splunk_* / o11y_*
└── report      → load_skill:troubleshoot-report, report_llm
```

Named nodes, not a repeating generic `Agent:agent` loop.

### 35. Why Is `troubleshoot-report` Not Loaded at the Start Like Part 2’s `investigation-report`?

Part 3 loads the report skill only after the investigate node returns MCP evidence. This separates evidence collection from presentation. It is a useful workflow property, not by itself a production control.

### 36. How Does Part 3 Choose the Product Playbook If Not by Keywords?

A **Python categorizer** inspects the alert payload (APM / IM / RUM / Synthetics). For the workshop high-error-rate detector, expect APM → `troubleshoot-apm-incidents`. Categorize shows `route_skill:…` (decision), not prompt injection.

### 37. I Still Do Not See Splunk Log Tools. Is That a Failure?

In Part 3, yes. Investigate should call `splunk_*` tools, typically `splunk_run_query` and sometimes `splunk_get_indexes` or `splunk_get_metadata`. Confirm that you ran from `part3_agent`, then run `mcp-doctor` there; Parts 1 and 2 expose only Observability MCP. If the tool ran but returned no events, verify the index, service fields, and alert-aligned time window. Stale entries in `search-logs/indexes.md` can create false negatives.

### 38. Same Tools as Part 2 — Why Does the Trace Look so Different?

MCP calls can overlap (`o11y_search_alerts_or_incidents`, error metrics). The teaching point is **when** skills enter the prompt and **which node** owns the work. Compare skill timing and graph shape, not only tool names.

### 39. How Should I Compare Evaluator Scores Across Parts?

Use the same alert and Agent Stream, then select sessions ending in `part1_agent`, `part2_agent`, and `part3_agent`. Compare tool inputs, time windows, result status, evidence used in the answer, and failure handling before comparing scores. Part 3 should include a log search and structured report. Do not infer quality from the agent version or score alone.

### 40. What Must I Verify Before Leaving Part 3?

Confirm that the alert was anchored by detector ID and rule, the categorizer selected the expected product playbook, investigate called both O11y and Splunk tools with the intended scope and time window, and every report claim maps to a tool result. Part 2 demonstrates playbook authoring; Part 3 demonstrates when the workflow attaches each playbook. Neither exercise establishes production readiness.

For hardening after the lab, see [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}).
