---
session_id: OBS1386
online_guide: https://zperrault-splunk.github.io/troubleshooting-agent/
---

<!-- Content appended after Exercise 3 "Steps" heading in the Word doc -->

## Run your first investigation

Make sure you completed Exercise 2 — Configure Environment: virtual environment installed, `.env` configured, and both doctor commands passing.

Start with a CLI investigation using the workshop defaults — service `paymentservice`, environment `splunk-hipster`:

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

You can also paste alert text from the facilitator's demo. Always include service (`paymentservice`) and environment (`splunk-hipster`) when asking about a specific service.

## Read the terminal trace

With `AGENT_LOG_TRACE=true` (the default), every run prints a structured trace to the terminal. As you read it, ask:

1. Which MCP tools did the agent call? — Look for `[n] MCP o11y_...` lines.
2. Which tools did it skip? — A baseline agent often skips traces, logs, or infrastructure correlation.
3. Were parameters correct? — Service should be `paymentservice`, environment `splunk-hipster` (exact APM names). Time ranges should use `{"start": "-1h", "stop": "now"}` inside a `params` object.
4. Is the answer grounded? — Does the final response reflect actual JSON from tool results, or does it sound plausible without evidence?

The same events are written to `shared/logs/investigations/<id>.jsonl` for post-workshop review. Each run prints the path at the end (look for `Log file:` in the output).

> Tip: Cleared your terminal before you could review the trace? Open the JSONL log using the `Log file:` path from the end of the run, or list the newest file with `ls -t ~/troubleshooting-agent/shared/logs/investigations/*.jsonl | head -1`. You can also re-run the same chat command — you will get a new trace and Agent Observability session, but the investigation flow is the same.

## Review the run in Splunk Agent Observability

After your chat completes, open the Splunk Agent Observability console and navigate to:

1. Project — the name you set (for example, `sre-agent-wkshp-shw-2cb1`)
2. Agent Stream — your log stream from `.env` (for example, `sre-agent-wkshp`)
3. Sessions — find the most recent session (named `chat-9265e3375c8b | part1_agent`)

Select the session to open the trace view. You should see three areas: the trace tree on the left, the chat in the center (user query and agent response), and detail tabs on the right.

Expand the trace tree. A typical Part 1 run looks like this:

```text
Agent
├── Agent:agent          ← LLM turn
├── should_continue      ← graph routing
├── tools
│   └── o11y_get_apm_service_errors_and_requests   ← MCP tool (names vary by run)
├── Agent:agent          ← next LLM turn
└── should_continue
```

Click `tools` and the nested MCP span to inspect arguments and JSON responses. Compare what Agent Observability captured with what the terminal trace showed — they should tell the same story.

@screenshot: Part 1 in Agent Stream — https://zperrault-splunk.github.io/troubleshooting-agent/6-part1-baseline-agent/

> Tip: Keep the Splunk Agent Observability console open in a browser tab during the workshop. After each investigation, refresh and locate your session — it is the fastest way to compare Part 1, Part 2, and Part 3 on the same alert in one Agent Stream.

## Baseline exercise

Work through this checklist using `paymentservice` in environment `splunk-hipster`:

| Step | Action |
|------|--------|
| 1 | Run `troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"` |
| 2 | Read the terminal trace — list tools called vs. tools skipped |
| 3 | Open Splunk Agent Observability — find your session and expand agent/tool spans |
| 4 | Answer: Did the agent ground its conclusion in MCP data? |
| 5 | Answer: Where might it have hallucinated if MCP had returned empty results? |
| 6 | Save your notes — you will re-run the same scenario in Part 2 and Part 3 |

> Important: Part 1 intentionally has no playbook. Expect variation between runs — that is the baseline you are measuring. Parts 2 and 3 add skills and structure to make investigations repeatable.

# Exercise 4 – Configure Log Stream Evaluators

## Description

You already send agent traces to Splunk Agent Observability from Part 1. In this exercise you turn on log stream evaluators so the platform automatically scores each investigation — not just records it.

Evaluators answer questions that are hard to judge by eye across dozens of runs:

- Did the agent pick the right MCP tools for the alert?
- Did tool calls fail because of bad parameters?
- Is the final answer grounded in tool output, or does it sound plausible without evidence?
- Did the agent complete the investigation goal, or stop early?

Most out-of-the-box evaluators use an SLM (Luna) or LLM-as-a-judge to score traces. Prefer SLM when configuring evaluators. If evaluator scores stay empty after several minutes, ask your facilitator to verify Integrations in the Splunk Agent Observability console.

## Before you start

| Requirement | Why |
|-------------|-----|
| Part 1 investigation completed | Compare before and after enabling evaluators |
| `.env` Agent Observability settings saved | Same `GALILEO_PROJECT` and `GALILEO_LOG_STREAM` you used in Part 1 |
| Splunk Agent Observability console access | Open the project your facilitator shared (or the one you created with `GALILEO_PROJECT`) |

## Steps

### Open your log stream

1. Sign in to the Splunk Agent Observability console.
2. Open Projects and select your project (for example, `sre-agent-wkshp-shw-2cb1`).
3. Select Agent Stream in the sidebar — this is the log stream named in your `.env` (for example, `sre-agent-wkshp`).
4. Confirm you see at least one session from Part 1 (for example, `chat-9265e3375c8b | part1_agent`).

### Configure evaluators

1. From the log stream view, click Configure Evaluators.
2. Search or filter the evaluator list.
3. Turn on the evaluators listed in the tables below.
4. When the console offers a choice between LLM and SLM (Luna), select SLM — same scoring intent, with lower latency and cost during the workshop.
5. Click Apply to save your evaluator selections. Toggles alone do not take effect until you apply.
6. When Agent Observability asks whether to compute evaluators on past logs, click Not Now. Your Part 1 session stays as the without evaluators baseline; you will run a fresh investigation next so you can compare both traces side by side.

> Tip: Keep your first Part 1 session un-scored on purpose. After you re-run the same chat command, you will have two sessions in the same log stream: one trace only (Part 1) and one trace + evaluator scores (this exercise). That makes the before/after difference easy to see.

> Tip: Many built-in evaluators have an SLM variant powered by Luna models. Use SLM for workshop runs unless your facilitator asks you to compare against the full LLM judge. If you do not see an SLM option for an evaluator, the LLM variant is fine.

#### Agent behavior — minimum set for Part 1

| Evaluator | Node type | Workshop focus |
|-----------|-----------|----------------|
| Tool selection quality | LLM span | Did it call `o11y_get_apm_service_errors_and_requests` vs. skipping straight to a vague answer? |
| Tool error | Tool span | Catches MCP validation errors (for example, missing `environment_name`) |
| Action completion | Session | Did it actually investigate errors, or only ask clarifying questions? |

#### Response quality — minimum set for hallucination checks

| Evaluator | Node type | Workshop focus |
|-----------|-----------|----------------|
| Context adherence | LLM span | Scores low when the model invents service names, error rates, or root causes not present in MCP JSON |
| Instruction adherence | LLM span | Part 1's prompt requires using `o11y_*` tools for live data |

> Tip: Context adherence is the primary hallucination signal for this workshop: it checks whether claims appear in the context Agent Observability sees (tool outputs attached to the trace). Correctness is broader factuality and is most useful when you have a known-good answer or rich tool results to compare against.

@screenshot: Configure Evaluators pane — https://zperrault-splunk.github.io/troubleshooting-agent/7-galileo-logstream-evaluators/

### Re-run Part 1 investigation

Re-run the same Part 1 investigation. Use the workshop defaults — service `paymentservice`, environment `splunk-hipster`:

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

### Review evaluator scores in Splunk Agent Observability

After your chat completes, open the Splunk Agent Observability console and navigate to:

1. Project — the name you set (for example, `sre-agent-wkshp-shw-2cb1`)
2. Agent Stream — your log stream from `.env` (for example, `sre-agent-wkshp`)
3. Sessions — use the session picker (for example, Session 2 of 2) to find your two Part 1 runs: the original (trace only) and the newest (with evaluator scores)

Select the newest session. On the right, open the Evaluators tab to see scores grouped under headings such as Agent Quality. SLM evaluators are labeled with (SLM).

@screenshot: Part 1 re-run with evaluator scores — https://zperrault-splunk.github.io/troubleshooting-agent/7-galileo-logstream-evaluators/

Work through this checklist using `paymentservice` in environment `splunk-hipster`:

| Step | Action |
|------|--------|
| 1 | Run the same chat command as Part 1 |
| 2 | Open Agent Stream — find both sessions using the session picker |
| 3 | On the newest session, expand the trace tree — confirm multiple tools spans ran |
| 4 | Click each MCP span — do the numbers and facts in the chat response match the tool JSON? |
| 5 | Open the Evaluators tab and record scores under Agent Quality |
| 6 | Compare your sessions — Part 1 baseline (trace only) vs. this run (trace + evaluator scores) |
| 7 | Save your notes and scores — you will re-run the same scenario in Part 2 and Part 3 |

> Tip: Part 1 intentionally has no playbook, so results can range from weak to strong across runs. A response can sound detailed in the chat panel but still score poorly on Action Completion — evaluators help you see that gap without reading every tool JSON by hand.

# Exercise 5 – Part 2 Skill Playbooks

## Description

Part 2 uses the same ReAct loop as Part 1, but adds playbooks — markdown skills that tell the agent which MCP tools to call, in what order, and how to format the answer. You will run the Part 2 agent, see what changes in Splunk Agent Observability, then complete your own error-rate skill and run the agent again.

For background on why skills matter, see the AI Skills chapter in the online guide.

### Part 1 vs Part 2 — agent differences

| Component | Part 1 | Part 2 |
|-----------|--------|--------|
| Agent loop | LangGraph ReAct | Same ReAct loop |
| Playbooks | None | One domain skill + always-on `investigation-report` |
| Routing | — | Keyword match on your chat/alert text (`alert_signals` in SKILL.md YAML) |
| Agent Observability session | `chat-… \| part1_agent` | `chat-… \| part2_agent` |
| Extra Agent Observability trace | — | `skill_router` — all skills injected before the ReAct loop |

Your message → keyword router → SKILL.md → system prompt → ReAct loop (LLM + MCP tools)

## Steps

### Run Part 2 agent

Make sure Exercise 3 (Part 1) and Exercise 4 (Configure Evaluators) are done — you will compare against those sessions.

From `part2_agent`, run a latency investigation. Use the workshop defaults — service `paymentservice`, environment `splunk-hipster`:

> Tip: Do not change `GALILEO_LOG_STREAM` in `.env` when you switch to `part2_agent`. Part 2 sessions appear in the same Agent Stream as Part 1 — look for the `part2_agent` suffix in the session name.

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part2_agent
troubleshooting-agent chat "Investigate latency on paymentservice in the splunk-hipster environment"
```

The keyword router should select `latency-spike` because the message contains signals like `latency`. The agent should also load `investigation-report` on every Part 2 run (report formatting — not matched by keywords).

> Tip: Use `paymentservice` and `splunk-hipster` for all Part 2 chat commands unless your facilitator says otherwise — same service and environment as Part 1.

### Review Part 2 in Splunk Agent Observability

Open Agent Stream and find the newest session named `chat-… | part2_agent`.

> Important: Playbooks are appended to the system prompt before the ReAct loop runs. You will not see `load_skill:investigation-report` or `load_skill:latency-spike` under Agent → tools — those spans only show MCP calls like `o11y_search_alerts_or_incidents`.

To confirm skills loaded, check:

1. Terminal — lines like `[N] Skill loaded: latency-spike` and `[N] Skill loaded: investigation-report`
2. Splunk Agent Observability — a separate `skill_router` trace in the same session (sibling to Agent, not nested inside it)
3. Chat JSON — the system message includes `## Active playbook` and `## Reporting requirements`

@screenshot: Part 1 vs Part 2 Agent Stream comparison — https://zperrault-splunk.github.io/troubleshooting-agent/8-part2-skill-playbooks/

On the Part 2 session:

- Select `skill_router` first — it is a sibling of Agent, not nested inside it
- Expand `load_skill:latency-spike` and `load_skill:investigation-report` to see characters injected into the system prompt
- Expand Agent → tools for MCP calls (`o11y_search_alerts_or_incidents`, `o11y_get_apm_service_latency`)
- Open the Evaluators tab — compare scores to your Part 1 baseline on a similar alert

The ReAct trace looks like Part 1 (`Agent:agent`, `tools`, `should_continue`), but tool order should follow the active playbook — for `latency-spike`, expect:

1. `o11y_search_alerts_or_incidents`
2. `o11y_get_apm_service_latency`

Compare evaluators to Part 1:

| Evaluator | What to look for |
|-----------|------------------|
| Tool selection quality | Did the agent call the tools the playbook names? |
| Action advancement / completion | Did it get further than Part 1's "please provide environment" or "here are next steps" stops? |
| Context adherence | Are cited metrics present in MCP tool output? |
| Instruction adherence | Did it follow the report skill (no raw JSON dumps)? |

> Tip: Filter Agent Stream by session name suffix `part2_agent`, or use the session picker to compare `part1_agent` vs `part2_agent` runs side by side.

### Author the error-rate skill

Your task: finish the starter stub at `part2_agent/skills/error-rate/SKILL.md` so the router picks `error-rate` when the user mentions errors or 5xx.

Work from `latency-spike/SKILL.md` — same structure, different tools and signals.

1. Open `skills/error-rate/SKILL.md` in your editor.
2. SKILL.md YAML — replace the TODO entries:
   - description — one line: investigate error-rate / 5xx alerts using APM error metrics
   - alert_signals — include `error`, `errors`, and `5xx` (add others if useful)
   - mcp_tools — list `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests`
3. When to use — when the alert or user message mentions elevated errors or error rate.
4. Tool sequence — two steps: search alerts/incidents (capture `eventId` when present; if empty, continue to step 2); get APM service errors and requests (required; `service_name`, `environment_name`, `time_range` in `params`).
5. Interpretation — at least two bullets (for example: error count vs request volume; errors spiking with traffic vs independently).
6. Do not — at least one rule (for example: do not state root cause without metric evidence from tools).
7. Save the file.

> Important: Tool names must match `mcp-doctor` exactly (`o11y_*` prefix). Time ranges belong inside a `params` object: `{"start": "-1h", "stop": "now"}`.

> Tip: The router counts how many alert_signals appear in your message. A prompt with `5xx` or `errors` should score `error-rate` higher than `latency-spike`.

### Run Part 2 with your error-rate skill

After saving `error-rate/SKILL.md`, run an error-focused investigation:

```bash
cd ~/troubleshooting-agent/part2_agent
troubleshooting-agent chat "Investigate elevated 5xx errors on paymentservice in the splunk-hipster environment"
```

Confirm in Splunk Agent Observability:

1. Open the new `part2_agent` session in Agent Stream.
2. Expand `skill_router` — expect `load_skill:error-rate` and `load_skill:investigation-report`.
3. Expand the main trace — expect at least `o11y_search_alerts_or_incidents` and `o11y_get_apm_service_errors_and_requests` under tools spans.
4. Open Evaluators — compare scores to your Part 1 and latency-demo Part 2 sessions.

@screenshot: Part 2 error-rate session — https://zperrault-splunk.github.io/troubleshooting-agent/8-part2-skill-playbooks/

| Step | Action |
|------|--------|
| 1 | `skill_router` shows `error-rate` as the domain skill |
| 2 | The trace includes two or more MCP tool calls aligned with your playbook |
| 3 | The chat response cites interpreted numbers from tool output (not generic advice) |
| 4 | The reply uses `investigation-report` headings — no raw JSON blocks |
| 5 | Evaluator scores are recorded — note which improved vs Part 1 |

> Tip: If the wrong skill loads, check alert_signals spelling and re-run with clearer keywords (`5xx`, `errors`, `error rate`) in the prompt.

# Exercise 6 – Part 3 Full Workflow

## Description

Part 3 replaces the single ReAct loop with a four-node LangGraph workflow: identify → categorize → investigate → report. The same `SKILL.md` playbook format from Part 2 applies — but when and where skills load in Splunk Agent Observability looks different on purpose.

Complete Exercise 5 (Part 2 Skill Playbooks) first so you have a baseline for keyword injection and the upfront `skill_router` trace.

### Part 2 vs Part 3 — how skills load

| | Part 2 | Part 3 |
|---|--------|--------|
| Orchestration | Single ReAct loop (same as Part 1) | Four-node graph — each step has its own prompt |
| Skill selection | Keyword router on your chat/alert text | Python categorizer on the alert payload (APM / IM / RUM / Synthetics) |
| When skills load | All at once, before the agent's first LLM turn | One step at a time, when that graph node runs |
| Agent Observability trace shape | Separate `skill_router` trace, then Agent | `load_skill:*` spans inside each node (`identify`, `investigate`, `report`) |
| Skills per run | One domain skill + always-on `investigation-report` | Different skills per phase |

> Important: If you just finished Part 2, you may look for a top-level `skill_router` block with every playbook listed upfront. Part 3 does not use that pattern. Skills appear under the node that needs them — that is the production-style workflow the workshop is teaching.

Part 3 trace shape (what to look for):

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

| Node | Skill(s) loaded | Why here |
|------|-----------------|----------|
| identify | get-alerts-or-incidents | Confirm the alert and capture IDs before investigating |
| categorize | (routing only) | Code picks product type — no full playbook yet |
| investigate | Product skill + search-logs | Product-specific MCP steps + mandatory Splunk log search |
| report | troubleshoot-report | Structured handoff — only after evidence is gathered |

## Steps

### Run Part 3 agent

Participants run Part 3 from the CLI with a mock Observability alert — no Slack integration required. The prompt includes service, environment, detectorId, and rule name so the identify node can anchor the investigation like a real alert thread.

> Tip: Do not change `GALILEO_LOG_STREAM` in `.env` when you switch to `part3_agent`. Part 3 sessions appear in the same Agent Stream as Parts 1 and 2 — look for the `part3_agent` suffix in the session name.

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part3_agent
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. DetectorId HNcv52_AwAA. Rule: SRE Agent - PaymentService High Error Rate. Find root cause of the high error rate and confirm whether it is resolved."
```

> Tip: The workshop prompt mirrors a Slack alert: service (`paymentservice`), environment (`splunk-hipster`), detector ID, and rule name. Part 3 uses these to fetch the alert payload, categorize as APM, run troubleshoot-apm-incidents + search-logs, then format troubleshoot-report.

Agent Observability sessions are named `chat-… | part3_agent`. Expect `part3_investigation` with nodes identify → categorize → investigate → report — not a single ReAct Agent trace.

### Review Part 3 in Splunk Agent Observability

1. Open Agent Stream and find a session ending in `part3_agent`.
2. Expand `part3_investigation` — confirm named nodes (`identify`, `categorize`, `investigate`, `report`), not repeated generic Agent:Agent spans.
3. Under `identify`, `investigate`, and `report`, expand `load_skill:*` spans — note when each playbook enters the prompt relative to MCP tool calls.
4. Compare to your Part 2 session on a similar alert — same tools may run, but the trace shape and skill timing should differ.

> Tip: Side-by-side comparison: Part 2 loads investigation-report at the start with the domain skill. Part 3 loads troubleshoot-report only in the report node — after investigate has gathered evidence.

### Comparison checklist

| Step | Action |
|------|--------|
| 1 | Confirm no top-level `skill_router` trace in Part 3 |
| 2 | Expand `load_skill:*` under identify, investigate, and report nodes |
| 3 | Confirm Splunk log search (`splunk_*` tools) ran in the investigate node |
| 4 | Compare evaluator scores to Part 1 and Part 2 on a similar alert |
| 5 | Save notes — Part 2 = keyword router + upfront skills; Part 3 = graph nodes + per-step skills |

# Wrap-up – Production-Ready Agent (optional reading)

## Description

After Part 3, you have a working four-node agent with skills, MCP tools, and Splunk Agent Observability tracing. Part 3 is a teaching workflow — the graph, skills, and MCP wiring are real, but several workshop shortcuts would need hardening before you run this on live incidents at scale.

This section summarizes practical next steps. It is optional reading — no lab steps required.

Full detail: https://zperrault-splunk.github.io/troubleshooting-agent/10-production-ready-agent/

### Alert intake and context

- Structured alert ingestion — Replace mock CLI prompts with a durable trigger (Slack Events API, webhook, or queue consumer) and normalize every alert into a typed payload before the graph starts.
- Anchor IDs early — Production runs should resolve the O11y alert record in code before the identify ReAct loop, so a bad LLM turn cannot burn tool budget searching for context.
- Resolution / dedup — Skip or shorten investigations when the alert is already cleared, or when the same event_id was handled recently.

### Orchestration and skills

- Keep the graph; tighten the nodes — The identify → categorize → investigate → report shape scales well. Production gains come from stricter node contracts and clearer handoff state between steps.
- Hybrid routing — The Python categorizer is fast and deterministic; add LLM fallback only for unknown product types.
- Version and test playbooks — Treat SKILL.md files like code: PR review, golden-path tests, and Agent Observability evaluators on report structure and tool-use completeness.

### MCP, Splunk, and reliability

- Session pooling and limits — Workshop runs open MCP stdio sessions per investigation; production needs connection reuse, per-tenant rate limits, and timeouts.
- Catalog maintenance — Keep search-logs/indexes.md aligned with your Splunk tenant; stale index names cause "no logs found" false negatives.
- Graceful degradation — When Splunk MCP is down, return a partial report with O11y evidence and an explicit Logs: unavailable section instead of failing the run.

### Safety, trust, and operations

- Human-in-the-loop for actions — This agent is read-only (investigate + report). Any production extension that posts to Slack, opens tickets, or runs remediations should use a two-step confirm flow.
- Secrets and tenancy — API tokens via vault/KMS, not `.env` on shared hosts; scope MCP credentials per environment; redact tokens and PII in logs and Agent Observability traces.
- Observability of the agent itself — Session IDs, node timings, tool failure rates, and evaluator scores should feed dashboards and alerts.
- Cost and latency budgets — Set recursion limits, cap parallel MCP calls, and track LLM token usage per investigation.

> Tip: A practical next step after the workshop: pick one alert type (e.g. APM error rate), wire real Slack or webhook intake, add one Agent Observability evaluator for troubleshoot-report completeness, and run shadow mode (agent reports, humans act) until scores stabilize.
