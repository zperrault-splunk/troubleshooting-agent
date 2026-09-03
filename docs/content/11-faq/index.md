---
title: "FAQ"
description: "Forty questions covering the overall workshop plus Parts 1–3 — setup, traces, skills, evaluators, and the four-node workflow."
weight: 11
navTitle: "FAQ"
---

Quick answers for the hands-on lab. Workshop defaults: service **`paymentservice`**, environment **`splunk-hipster`**. Use the same [Agent Observability](https://console.multitenant.galileocloud.io) project and agent stream across Parts 1–3.

{{< notice title="How to use this page" style="tip" >}}
Start with [General](#general) for setup and CLI issues. Use the Part 1–3 sections while you are in that exercise. For playbook authoring background, see [AI Skills]({{< relref "2-ai-skills" >}}).
{{< /notice >}}

## General

### 1. What Will I Build in This Workshop?

A troubleshooting agent that investigates observability alerts using an LLM plus structured MCP tools. You progress through three implementations that share the same CLI (`troubleshooting-agent`) and integrations in `shared/workshop_shared/`: a baseline ReAct agent, the same loop with skill playbooks, and a four-node LangGraph workflow.

The three parts share one CLI and the same Observability demo service so you can compare traces side by side.

### 2. How Are Parts 1, 2, and 3 Different?

| Part | Agent shape | What is added |
|------|-------------|---------------|
| **[Part 1]({{< relref "6-part1-baseline-agent" >}})** | Single ReAct loop | MCP tools only — no playbooks |
| **[Part 2]({{< relref "8-part2-skill-playbooks" >}})** | Same ReAct loop | Keyword-injected `SKILL.md` playbooks |
| **[Part 3]({{< relref "9-part3-full-workflow" >}})** | Four-node graph | identify → categorize → investigate → report, with skills loaded per node |

### 3. Where Do I Run Commands, and Why Does the Directory Matter?

Always `cd` into the part directory (`part1_agent/`, `part2_agent/`, or `part3_agent/`) before running `troubleshooting-agent`. The CLI loads the agent for **that directory**. Running from the repo root (or the wrong part folder) uses the wrong graph and skills.

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

`doctor` checks the LLM (workshop proxy / model). `mcp-doctor` checks Observability MCP (expect about 12 `o11y_*` tools). If either fails, ask a facilitator — most issues are credentials, `.env`, or the MCP gateway.

### 7. Why Do My Prompts Need `paymentservice` and `splunk-hipster`?

Those are the workshop APM names. If you omit the environment, the agent may call `o11y_get_apm_environments` and stop to ask you for it. If you misspell the service, MCP returns empty or unrelated data and the answer looks like a hallucination even when the model is trying.

### 8. Where Do I Review a Run After It Finishes?

Three places, same story:

1. **Terminal** — live `[n] MCP o11y_...` lines (`AGENT_LOG_TRACE=true` is the default)
2. **JSONL** — `shared/logs/investigations/<id>.jsonl` (path printed as `Log file:`)
3. **Splunk Agent Observability** — project `sre-agent-wkshp` → Agent Stream → session named like `chat-… | part1_agent`

Terminal IDs use `chat:`; console session names use `chat-`.

### 9. When Do I Enable Evaluators, and Should I Score My First Part 1 Run?

Enable evaluators **after** the first Part 1 investigation, then click **Not Now** when asked to score past logs. That keeps session 1 as a trace-only baseline. Prefer **SLM (Luna)** over full LLM judges. Toggles do nothing until you click **Apply**. If scores stay empty, ask a facilitator to check Integrations.

Details: [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}).

### 10. Can I Use This Agent on Live Incidents After the Workshop?

Part 3 is a teaching workflow: real graph, skills, and MCP, but workshop shortcuts remain (CLI mock alerts, per-run MCP sessions, `.env` on a shared host). Harden intake, timeouts, secrets, report completeness evaluators, and human-in-the-loop before production. The agent is **read-only** (investigate + report) — do not add remediations without a confirm step.

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

That is expected. With no playbook, tool order, depth, and whether the agent stops at “next steps” all vary. Part 1 is a **baseline**, not a gold-standard investigation.

### 14. How Do I Tell If the Answer Is Grounded vs. Hallucinated?

In the terminal or Agent Observability, open each MCP span and compare JSON to the chat reply. Claims about error rates, services, or root cause should appear in tool output. **Context Adherence** (after evaluators are on) is the primary hallucination signal for this lab.

### 15. Which Tools Should I Expect in Part 1?

Anything from the Observability MCP list (`mcp-doctor`). Common calls include `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`. A baseline run often **skips** traces, logs, and dependency correlation. Missing tools is a finding, not necessarily a setup failure.

### 16. Time Range or Environment Errors on MCP Calls — What Is Wrong?

Use exact APM names (`paymentservice`, `splunk-hipster`). Time ranges belong in a `params` object, for example `{"start": "-1h", "stop": "now"}`. Missing `environment_name` is a typical validation error; **Tool error** evaluators catch this after you enable them.

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

Tools called vs skipped; whether the conclusion matched MCP JSON; where the agent might have invented a cause if tools were empty. You will re-run the **same alert** in Parts 2 and 3 and compare traces and evaluator scores.

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

Expect tools in playbook order: `o11y_search_alerts_or_incidents`, then `o11y_get_apm_service_latency`. Empty alert search is normal for CLI runs — the agent must still call step 2 and format the reply with `investigation-report` headings.

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

No. Watch **direction**: Tool selection quality (playbook tools called), Action Completion (fewer “please specify environment” / “next steps” stops), Context Adherence (metrics from MCP JSON), Instruction Adherence (report headings, no raw JSON dumps). Scores can still be low; that is useful data.

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

Part 3 loads the report skill only in the **report** node, after investigate has MCP evidence. That is the production-style pattern: do not format the handoff until the work is done.

### 36. How Does Part 3 Choose the Product Playbook If Not by Keywords?

A **Python categorizer** inspects the alert payload (APM / IM / RUM / Synthetics). For the workshop high-error-rate detector, expect APM → `troubleshoot-apm-incidents`. Categorize shows `route_skill:…` (decision), not prompt injection.

### 37. I Still Do Not See Splunk Log Tools. Is That a Failure?

Investigate should call `splunk_*` tools (typically `splunk_run_query`, sometimes `splunk_get_indexes` / `splunk_get_metadata`). If they are missing, confirm you ran from `part3_agent` (Parts 1 and 2 expose Observability MCP only) and check `mcp-doctor` from that directory. Stale names in `search-logs/indexes.md` can also yield “no logs found.”

### 38. Same Tools as Part 2 — Why Does the Trace Look so Different?

MCP calls can overlap (`o11y_search_alerts_or_incidents`, error metrics). The teaching point is **when** skills enter the prompt and **which node** owns the work. Compare skill timing and graph shape, not only tool names.

### 39. How Should I Compare Evaluator Scores Across Parts?

Same alert, same Agent Stream, three suffixes: `part1_agent`, `part2_agent`, `part3_agent`. Look at Tool selection quality, Action Completion, Context Adherence, and Instruction Adherence. Part 3 should show log search and a structured report; Part 1 often stops early; Part 2 sits in between.

### 40. What Is the One-Line Takeaway of Part 3?

**Author** playbooks in Part 2 (keywords + `SKILL.md`). **Orchestrate** them in Part 3 (workflow engine decides *when* each runbook attaches). Production troubleshooting agents usually look more like Part 3 than a single ReAct loop.

For hardening after the lab, see [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}).
