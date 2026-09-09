---
session_id: OBS1386
online_guide: https://zperrault-splunk.github.io/troubleshooting-agent/
---

<!-- Workshop exercise text. Word guide: docs/facilitator/conf26 OBS1386 - Lab Guide - 09162026.docx -->

# Exercise 1 – Configure Environment

Your workshop instance and credentials are already configured. Before Part 1, install the agent dependencies and give your Agent Observability agent stream a unique name. That name will let you isolate your traces from other attendees' traces.

## Install dependencies

```bash
cd ~/troubleshooting-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-workshop.txt
pip install -e . --no-deps
```

> Tip: Run `source .venv/bin/activate` whenever you open a new SSH session. Your prompt should show `(.venv)` when the environment is active.

## Personalize your Agent Observability settings

Create `.env`, then enable Agent Observability on the shared workshop project:

```bash
cd ~/troubleshooting-agent
cp .env.example .env
vi .env
```

Add or update these lines. You do not need to set `GALILEO_LOG_STREAM` — the agent builds `sre-agent-wkshp-<instance>` from `$INSTANCE` (see Finding Your Instance Details):

```bash
ENABLE_GALILEO=true
GALILEO_PROJECT="sre-agent-wkshp"
```

For example, if `echo $INSTANCE` prints `shw-2cb1`, your Agent Stream will be `sre-agent-wkshp-shw-2cb1`.

> Tip: Keep `GALILEO_PROJECT` unchanged across Parts 1–3. Do not set `GALILEO_LOG_STREAM` unless your facilitator asks you to. The same Agent Stream will hold every session for side-by-side comparison.

Save and exit: press `Esc`, type `:wq`, then press Enter. Verify that the file contains `ENABLE_GALILEO` and `GALILEO_PROJECT`.

## Verify setup

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent doctor
troubleshooting-agent mcp-doctor
```

> Important: Continue only when both commands report `Ready`. `doctor` verifies the LLM connection; `mcp-doctor` verifies the Splunk Observability and Splunk Cloud MCP endpoints and lists the available tools. If either check fails, copy the failure output and ask your facilitator for help.

# Exercise 2 – Part 1 — Baseline Agent

## Run your first investigation

Confirm that you completed Exercise 1 — Configure Environment: the virtual environment is active, `.env` identifies your agent stream, and both doctor commands report `Ready`.

Investigate service `paymentservice` in environment `splunk-hipster`:

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

You can also paste alert text from the facilitator's demo. Always include service (`paymentservice`) and environment (`splunk-hipster`) when asking about a specific service.

## Read the terminal trace

With `AGENT_LOG_TRACE=true` (the default), every run prints a structured trace. Verify:

1. Which MCP tools ran. Find each `[n] MCP o11y_...` line.
2. Which relevant signals the agent skipped. A baseline run may omit traces, logs, or infrastructure correlation.
3. Whether each input used the exact APM names: service `paymentservice` and environment `splunk-hipster`.
4. Whether time ranges appear inside `params` as `{"start": "-1h", "stop": "now"}`.
5. Whether claims in the final response map to values in tool-result JSON. Treat a plausible claim without trace evidence as ungrounded.

The same events are written to `shared/logs/investigations/<id>.jsonl` for post-workshop review. Each run prints the path at the end (look for `Log file:` in the output).

> Tip: If the terminal trace is no longer visible, open the JSONL log using the `Log file:` path from the end of the run, or list the newest file with `ls -t ~/troubleshooting-agent/shared/logs/investigations/*.jsonl | head -1`. Re-running the same chat command creates a new terminal trace and Agent Observability session; do not mistake it for the original run.

## Metrics, traces, logs, and events vs Agent streams

Splunk Observability records metrics, traces, logs, and events for `paymentservice`. The agent queries those signals through `o11y_*` tools.

Splunk Agent Observability does not store those application signals. It stores an **Agent stream**, a named collection of sessions for this workshop instance. Each session contains one investigation: the chat, an agent trace, and spans for LLM turns and MCP calls.

> Tip: Same words, two systems. If the agent calls `o11y_get_apm_exemplar_traces`, the returned IDs identify Splunk Observability traces for `paymentservice`. The tree in Agent Stream is the separate agent trace. Nested `o11y_*` spans show which application signals the agent queried.

## Review the run in Splunk Agent Observability

After your chat completes, open the Splunk Agent Observability console and navigate to:

1. Project — the shared workshop project (`sre-agent-wkshp`)
2. Agent Stream — your agent stream from `.env` (for example, `sre-agent-wkshp-shw-2cb1`)
3. Sessions — find the most recent session (named `chat-9265e3375c8b | part1_agent`)

Select the session. Verify three areas are present: the agent trace tree on the left, the chat query and response in the center, and detail tabs on the right. Nested `o11y_*` spans represent queries against Splunk Observability metrics, traces, logs, or events.

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

Open `tools` and each nested MCP span. Check its arguments, result status, and JSON response against the terminal trace. The tool sequence, inputs, results, and final answer should agree across both views.

@screenshot: Part 1 in Agent Stream — https://zperrault-splunk.github.io/troubleshooting-agent/6-part1-baseline-agent/

> Tip: Keep the Splunk Agent Observability console open. After each investigation, refresh the session list and select the latest run. Use the same service, environment, and alert scenario across all three parts, then account for changes in live telemetry when you compare them.

## Baseline exercise

Complete this baseline using `paymentservice` in environment `splunk-hipster`:

| Step | Action |
|------|--------|
| 1 | Run `troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"` |
| 2 | Record the tools called, relevant tools skipped, and each tool's input scope and time window |
| 3 | Open Splunk Agent Observability, find the session, and expand every agent and tool span |
| 4 | Map each conclusion to the MCP result that supports it; mark unsupported claims |
| 5 | Identify claims that would become hallucinations if the corresponding MCP result were empty |
| 6 | Save the tool sequence, evidence, failure modes, and final conclusion for comparison with Parts 2 and 3 |

> Important: Part 1 intentionally has no playbook. Tool choice and investigation depth can vary between runs. Capture that variation; Parts 2 and 3 add controls intended to make the same investigation more repeatable.

# Exercise 3 – Configure Agent Stream Evaluators

## Description

Enable agent stream evaluators, then re-run the Part 1 investigation. Splunk Agent Observability will score the new session while preserving the original trace-only session as your baseline.

Use the scores to verify:

- Whether the selected MCP tools match the alert and available signals
- Whether invalid inputs or execution errors caused tool failures
- Whether the final answer is grounded in tool output
- Whether the agent completed the investigation or stopped early

Most built-in evaluators score traces with an SLM (Luna) or an LLM-as-a-judge. Select SLM when available. If a new session remains unscored after several minutes, ask your facilitator to verify Integrations in the Splunk Agent Observability console.

## Before you start

| Requirement | Why |
|-------------|-----|
| Part 1 investigation completed | Compare before and after enabling evaluators |
| `.env` Agent Observability settings saved | Same `GALILEO_PROJECT` and `GALILEO_LOG_STREAM` you used in Part 1 |
| Splunk Agent Observability console access | Open the shared project `sre-agent-wkshp`, then your instance Agent Stream |

## Steps

### Open your agent stream

1. Sign in to the Splunk Agent Observability console.
2. Open Projects and select the shared project `sre-agent-wkshp`.
3. Select Agent Stream in the sidebar. Open the stream named in your `.env` (for example, `sre-agent-wkshp-shw-2cb1`).
4. Confirm you see at least one session from Part 1 (for example, `chat-9265e3375c8b | part1_agent`).

### Configure evaluators

1. From the agent stream view, click Configure Evaluators.
2. Search or filter the evaluator list.
3. Turn on the evaluators listed in the tables below.
4. When the console offers a choice between LLM and SLM (Luna), select SLM — same scoring intent, with lower latency and cost during the workshop.
5. Click Apply to save your evaluator selections. Toggles alone do not take effect until you apply.
6. When Agent Observability asks whether to compute evaluators on past logs, click Not Now. Your Part 1 session stays as the without evaluators baseline; you will run a fresh investigation next so you can compare both traces side by side.

> Tip: Keep the first Part 1 session unscored. After you re-run the same command, the agent stream will contain one trace-only session and one session with trace data and evaluator scores.

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

1. Project — the shared workshop project (`sre-agent-wkshp`)
2. Agent Stream — your stream from `.env` (for example, `sre-agent-wkshp-shw-2cb1`)
3. Sessions — use the session picker (for example, Session 2 of 2) to find your two Part 1 runs: the original (trace only) and the newest (with evaluator scores)

Select the newest session. On the right, open the Evaluators tab to see scores grouped under headings such as Agent Quality. SLM evaluators are labeled with (SLM).

@screenshot: Part 1 re-run with evaluator scores — https://zperrault-splunk.github.io/troubleshooting-agent/7-galileo-logstream-evaluators/

Work through this checklist using `paymentservice` in environment `splunk-hipster`:

| Step | Action |
|------|--------|
| 1 | Run the same chat command as Part 1 |
| 2 | Open Agent Stream — find both sessions using the session picker |
| 3 | Expand the newest session's trace tree and confirm that multiple `tools` spans ran |
| 4 | For each MCP span, verify the input service, environment, and time window; then map chat claims to result JSON |
| 5 | Open the Evaluators tab and record scores under Agent Quality |
| 6 | Compare the Part 1 trace-only baseline with this trace-and-scores run |
| 7 | Save the tool sequence, failures, evidence, final conclusion, and scores for Parts 2 and 3 |

> Tip: Part 1 has no playbook, so results vary across runs. A detailed response can still score poorly on Action Completion when the trace ends before the investigation reaches a supported conclusion.

# Exercise 4 – Part 2 Skill Playbooks

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

Make sure Exercise 2 (Part 1) and Exercise 3 (Configure Evaluators) are done — you will compare against those sessions.

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
| Action Completion | Did it get further than Part 1's "please provide environment" or "here are next steps" stops? |
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

# Exercise 5 – Part 3 Full Workflow

## Description

Part 3 replaces the single ReAct loop with a four-node LangGraph workflow: identify → categorize → investigate → report. The same `SKILL.md` playbook format from Part 2 applies — but when and where skills load in Splunk Agent Observability looks different on purpose.

Complete Exercise 4 (Part 2 Skill Playbooks) first so you have a baseline for keyword injection and the upfront `skill_router` trace.

### Part 2 vs Part 3 — how skills load

| | Part 2 | Part 3 |
|---|--------|--------|
| Orchestration | Single ReAct loop (same as Part 1) | Four-node graph — each step has its own prompt |
| Skill selection | Keyword router on your chat/alert text | Python categorizer on the alert payload (APM / IM / RUM / Synthetics) |
| When skills load | All at once, before the agent's first LLM turn | One step at a time, when that graph node runs |
| Agent Observability trace shape | Separate `skill_router` trace, then Agent | `load_skill:*` spans inside each node (`identify`, `investigate`, `report`) |
| Skills per run | One domain skill + always-on `investigation-report` | Different skills per phase |

> Important: Part 3 has no top-level `skill_router` block. Each skill appears under the node that loads it. If `skill_router` appears, verify that you ran the command from `part3_agent`.

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
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. DetectorId HO6Pg5tAwAM. Rule: sre agent - High Error rate. Find root cause of the high error rate and confirm whether it is resolved."
```

> Tip: The workshop prompt mirrors a Slack alert: service (`paymentservice`), environment (`splunk-hipster`), detector ID, and rule name. Part 3 uses these to fetch the alert payload, categorize as APM, run troubleshoot-apm-incidents + search-logs, then format troubleshoot-report.

Agent Observability sessions are named `chat-… | part3_agent`. Expect `part3_investigation` with nodes identify → categorize → investigate → report — not a single ReAct Agent trace.

### Review Part 3 in Splunk Agent Observability

1. Open Agent Stream and find a session ending in `part3_agent`.
2. Expand `part3_investigation` — confirm named nodes (`identify`, `categorize`, `investigate`, `report`), not repeated generic Agent:Agent spans.
3. Expand `load_skill:*` under `identify`, `investigate`, and `report`. Record which skill entered the prompt before each node's MCP calls.
4. Inspect `identify_tools` for alert resolution. Inspect `investigate_tools` for APM evidence and at least one `splunk_*` log search. Treat an empty result as an observation, not proof that no events exist. First confirm that the query succeeded and used the intended service, environment, index, and alert time window.
5. In the final report, trace every metric and root-cause statement back to a tool result. Treat unsupported causality or a resolution claim without post-alert evidence as a failure.
6. Compare with the Part 2 session for the same alert. Tool names may overlap; node ownership and skill timing must differ.

> Tip: Side-by-side comparison: Part 2 loads investigation-report at the start with the domain skill. Part 3 loads troubleshoot-report only in the report node — after investigate has gathered evidence.

### Comparison checklist

| Step | Action |
|------|--------|
| 1 | Confirm no top-level `skill_router` trace in Part 3 |
| 2 | Expand `load_skill:*` under identify, investigate, and report nodes |
| 3 | Confirm Splunk log search (`splunk_*` tools) ran in the investigate node |
| 4 | Trace every report claim to a tool result; treat unsupported resolution claims as a failure |
| 5 | Compare evaluator scores to Part 1 and Part 2 on a similar alert |
| 6 | Save notes — Part 2 = keyword router + upfront skills; Part 3 = graph nodes + per-step skills |

# Wrap-up – Production-Ready Agent (optional reading)

## Description

The Part 3 implementation is suitable for learning and controlled evaluation. It is not production-ready. The four-node graph, playbooks, MCP calls, and Splunk Agent Observability traces demonstrate the workflow, but they do not provide the availability, security, tenancy, change-control, or safety controls required for live incident operations.

This section summarizes practical next steps. It is optional reading — no lab steps required.

Full detail: https://zperrault-splunk.github.io/troubleshooting-agent/10-production-ready-agent/

### Alert intake and context

- Structured alert ingestion — Replace the mock CLI prompt with a durable, authenticated trigger (Slack Events API, webhook, or queue consumer) and normalize every alert into a typed payload before the graph starts.
- Anchor IDs early — Resolve the O11y alert record in deterministic code before spending LLM or MCP tool budget.
- Resolution / dedup — Use `event_id` as the idempotency key. Deduplicate retries and define when a cleared alert should receive a shortened verification run.

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

> Tip: Start with one alert type, such as APM error rate. Add authenticated Slack or webhook intake, deterministic alert normalization, bounded tool calls, and an Agent Observability evaluator for `troubleshoot-report` completeness. Run in shadow mode: the agent reports and humans investigate and act. Promote only against explicit accuracy, completeness, latency, failure-rate, and safety criteria; stable evaluator scores alone are insufficient.
