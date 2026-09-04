---
title: "Part 1 — Baseline Agent"
description: "Run the minimal MCP-only ReAct agent, interpret terminal and Agent Observability traces, and establish a baseline investigation for comparison with Parts 2 and 3."
weight: 6
navTitle: "Part 1 — Baseline Agent"
duration: "20 minutes"
---

Run the minimal troubleshooting agent and capture its investigation path. This baseline has no skills and no multi-step workflow. A single LangGraph ReAct loop lets the LLM reason, call Splunk Observability MCP tools, inspect results, and repeat until it answers.

Record what the agent does without a playbook. You will compare its tool selection, evidence, and investigation depth with Part 2 (skills) and Part 3 (structured graph).

## Baseline Agent


| Component         | Description                                             |
| ----------------- | ------------------------------------------------------- |
| **Agent loop**    | LangGraph ReAct: `agent` (LLM) → `tools` (MCP) → repeat |
| **Tools**         | Splunk Observability MCP only (`o11y_`* prefix)         |
| **Skills**        | None; the model decides the investigation path          |
| **Observability** | Terminal trace, JSONL logs, Agent Observability session |


If you want to skim the code before running:


| File                    | Purpose                                              |
| ----------------------- | ---------------------------------------------------- |
| `part1_agent/agent.py`  | ReAct graph, MCP wiring, observability callbacks     |
| `part1_agent/prompt.py` | System prompt requiring `o11y_*` calls for live data |




## Run your first investigation

Confirm that you completed [Configure Environment]({{< relref "5-configure-agent-environment" >}}): the virtual environment is active, `.env` identifies your agent stream, and both doctor commands report `Ready`.

Investigate service `paymentservice` in environment `splunk-hipster`:

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
```

{{% /tab %}}
{{% tab title="Example Output" %}}

```text
(.venv) splunk@ip-172-31-19-27:~/troubleshooting-agent/part1_agent$ troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"
INFO Splunk OTel initialized service=troubleshooting-agent
INFO HTTP Request: POST https://lite-llm-proxy.splunko11y.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO [inv=chat:5a4dffc6d704] Log file: /home/splunk/troubleshooting-agent/shared/logs/investigations/chat-5a4dffc6d704.jsonl
INFO [inv=chat:5a4dffc6d704] 
INFO [inv=chat:5a4dffc6d704] ══════════════════════════════════════════════════════════════
INFO [inv=chat:5a4dffc6d704]  Investigation  chat:5a4dffc6d704  |  part1_agent  |  cli
INFO [inv=chat:5a4dffc6d704] ──────────────────────────────────────────────────────────────
INFO [inv=chat:5a4dffc6d704]  Query: Why does paymentservice have errors in the splunk-hipster environment?
INFO [inv=chat:5a4dffc6d704]  LLM: openai  |  MCP tools available: 12
INFO [inv=chat:5a4dffc6d704] ══════════════════════════════════════════════════════════════
INFO HTTP Request: GET https://api.multitenant.galileocloud.io/healthcheck "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/login/api_key "HTTP/1.1 200 OK"
INFO HTTP Request: GET https://api.multitenant.galileocloud.io/current_user "HTTP/1.1 200 OK"
INFO HTTP Request: GET https://api.multitenant.galileocloud.io/projects?project_name=sre-agent-wkshp&type=gen_ai "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/projects "HTTP/1.1 200 OK"
INFO HTTP Request: GET https://api.multitenant.galileocloud.io/projects/26a65ecc-5b04-43b8-adf0-4aabf5af4b94/log_streams/paginated?include_counts=false&starting_token=0&limit=500 "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/projects/26a65ecc-5b04-43b8-adf0-4aabf5af4b94/log_streams "HTTP/1.1 200 OK"
INFO HTTP Request: GET https://api.multitenant.galileocloud.io/ingest/healthz "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/v2/projects/26a65ecc-5b04-43b8-adf0-4aabf5af4b94/sessions/search "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/v2/projects/26a65ecc-5b04-43b8-adf0-4aabf5af4b94/sessions "HTTP/1.1 200 OK"
INFO Galileo session=chat-5a4dffc6d704 | part1_agent project=sre-agent-wkshp stream=sre-agent-wkshp-shw-2cb1 console=https://console.multitenant.galileocloud.io
INFO HTTP Request: POST https://lite-llm-proxy.splunko11y.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO [inv=chat:5a4dffc6d704]  trace_id=963b3abe6a9c149c418f84c5fea67a82 [1] LLM turn 1 — calling tools: o11y_search_alerts_or_incidents
INFO [inv=chat:5a4dffc6d704]  trace_id=963b3abe6a9c149c418f84c5fea67a82 [2] MCP o11y_search_alerts_or_incidents — OK
INFO HTTP Request: POST https://lite-llm-proxy.splunko11y.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO [inv=chat:5a4dffc6d704]  trace_id=963b3abe6a9c149c418f84c5fea67a82 [2] LLM turn 2 — calling tools: o11y_get_apm_service_errors_and_requests
INFO [inv=chat:5a4dffc6d704]  trace_id=963b3abe6a9c149c418f84c5fea67a82 [3] MCP o11y_get_apm_service_errors_and_requests — OK
INFO HTTP Request: POST https://lite-llm-proxy.splunko11y.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO [inv=chat:5a4dffc6d704]  trace_id=963b3abe6a9c149c418f84c5fea67a82 [3] LLM turn 3 — composing final response
INFO HTTP Request: POST https://api.multitenant.galileocloud.io/ingest/traces/26a65ecc-5b04-43b8-adf0-4aabf5af4b94 "HTTP/1.1 200 OK"
INFO [inv=chat:5a4dffc6d704] ──────────────────────────────────────────────────────────────
INFO [inv=chat:5a4dffc6d704]  Done — 3 LLM turns | 2 tool calls | 18.2s
INFO [inv=chat:5a4dffc6d704]  Log file: /home/splunk/troubleshooting-agent/shared/logs/investigations/chat-5a4dffc6d704.jsonl
INFO [inv=chat:5a4dffc6d704] ══════════════════════════════════════════════════════════════
INFO [inv=chat:5a4dffc6d704] 
INFO [inv=chat:5a4dffc6d704] ──────────────────────────────────────────────────────────────
INFO [inv=chat:5a4dffc6d704]  Agent response
INFO [inv=chat:5a4dffc6d704] ──────────────────────────────────────────────────────────────
INFO [inv=chat:5a4dffc6d704] paymentservice in splunk-hipster shows elevated errors in the last hour. I found … (summary from MCP tool JSON — your run may differ)
INFO [inv=chat:5a4dffc6d704] ══════════════════════════════════════════════════════════════
```

{{% /tab %}}  
{{< /tabs >}}

## Read the terminal trace

With `AGENT_LOG_TRACE=true` (the default), every run prints a structured trace. Verify:

1. Which MCP tools ran. Find each `[n] MCP o11y_...` line.
2. Which relevant signals the agent skipped. A baseline run may omit traces, logs, or infrastructure correlation.
3. Whether each input used the exact APM names: service `paymentservice` and environment `splunk-hipster`.
4. Whether time ranges appear inside `params` as `{"start": "-1h", "stop": "now"}`.
5. Whether claims in the final response map to values in tool-result JSON. Treat a plausible claim without trace evidence as ungrounded.

The same events are written to `shared/logs/investigations/<id>.jsonl` for post-workshop review. Each run prints the path at the end (look for `Log file:` in the output).

{{< notice title="Tip" style="tip" >}}
If the terminal trace is no longer visible, recover the evidence in either of these ways:

- Open the JSONL log. Use the `Log file:` path printed at the end of the run, or list the newest file:
  ```bash
  ls -t ~/troubleshooting-agent/shared/logs/investigations/*.jsonl | head -1
  ```
- Re-run `troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"`. This creates a new terminal trace and Agent Observability session; do not mistake it for the original run.
{{< /notice >}}



## Splunk Agent Observability

**Splunk Agent Observability** captures each investigation as a browser-accessible agent trace:

- Each LLM turn and the model's next action
- Each MCP tool call, including inputs and outputs
- Input, output, and total token usage for the session


| Signal                           | Where                              | Best for                        |
| -------------------------------- | ---------------------------------- | ------------------------------- |
| **Terminal trace**               | CLI output during a run            | Live narration                  |
| **JSONL files**                  | `shared/logs/investigations/`      | Review after a run              |
| **Agent Observability sessions** | Splunk Agent Observability console | Comparing runs across Parts 1–3 |


Each investigation creates a **session** named like `chat-abc123 | part1_agent` in your Agent Observability project (terminal IDs use `chat:`; session names in the console use `chat-`).

### Metrics, traces, logs, and events vs Agent streams

**Splunk Observability** records metrics, traces, logs, and events for `paymentservice`. The agent queries those signals through `o11y_`* tools.

**Splunk Agent Observability** does not store those application signals. It stores an **Agent stream**, a named collection of sessions for this workshop instance. Each session contains one investigation: the chat, an agent trace, and spans for LLM turns and MCP calls.


| Splunk Observability | What it tells you (the app)                                        | In an Agent stream                               | Difference                                           |
| -------------------- | ------------------------------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------- |
| **Metrics**          | Time series: error rate, latency, request volume                   | Token counts, later **evaluators**               | App RED vs agent quality/cost — not the same numbers |
| **Traces**           | One user request across services (`paymentservice` → dependencies) | One agent interaction (reason → tools → answer)  | App request vs investigation workflow                |
| **Logs**             | Application log lines                                              | Span input/output and the workshop JSONL file    | Syslog/events from the service vs LLM/tool payloads  |
| **Events**           | Detector firings, alert/incident activity                          | A **session** (one `troubleshooting-agent chat`) | An incident on the app vs a recorded agent run       |


**Chat** is the session's query-and-answer view, not a fifth Observability signal.

{{< notice title="Same words, two systems" style="tip" >}}
If the agent calls `o11y_get_apm_exemplar_traces`, the returned IDs identify **Splunk Observability traces** for `paymentservice`. The tree in **Agent Stream** is the separate **agent trace**. Nested `o11y_`* spans show which application signals the agent queried.
{{< /notice >}}

## Review the run in Splunk Agent Observability

After your chat completes, open the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io) and navigate to:

1. **Project** — the shared workshop project (`sre-agent-wkshp`)
2. **Agent Stream** — your agent stream from `.env` (for example, `sre-agent-wkshp-shw-2cb1`)
3. **Sessions** — find the most recent session (named `chat-9265e3375c8b | part1_agent`)

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

{{< diagram src="images/part1-galileo-trace.png" alt="Splunk Agent Observability Agent Stream showing a Part 1 session with trace tree, chat, and empty Evaluators tab" caption="Part 1 in Agent Stream. Evaluators are empty until the next section." width="960" >}}

{{< notice title="Tip" style="tip" >}}
Keep the Splunk Agent Observability console open. After each investigation, refresh the session list and select the latest run. Use the same service, environment, and alert scenario across all three parts, then account for changes in live telemetry when you compare them.
{{< /notice >}}

## Baseline exercise

Complete this baseline using `paymentservice` in environment `splunk-hipster`:


| Step | Action                                                                                                                                 |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Run `troubleshooting-agent chat "Why does paymentservice have errors in the splunk-hipster environment?"`                              |
| 2    | Record the tools called, relevant tools skipped, and each tool's input scope and time window                                           |
| 3    | Open [Splunk Agent Observability](https://console.multitenant.galileocloud.io), find the session, and expand every agent and tool span |
| 4    | Map each conclusion to the MCP result that supports it; mark unsupported claims                                                        |
| 5    | Identify claims that would become hallucinations if the corresponding MCP result were empty                                            |
| 6    | Save the tool sequence, evidence, failure modes, and final conclusion for comparison with Parts 2 and 3                                |


{{< notice title="Important" style="primary" >}}
Part 1 intentionally has no playbook. Tool choice and investigation depth can vary between runs. Capture that variation; Parts 2 and 3 add controls intended to make the same investigation more repeatable.
{{< /notice >}}

## Exit checks

Before continuing, confirm that you have:

- A terminal trace and matching Agent Observability session for the run
- The exact tool sequence, tool inputs, result status, and one-hour query window
- Evidence linking each final-answer claim to MCP result JSON
- A list of relevant signals the agent did not inspect
- Notes on empty results, failed tool calls, or unsupported conclusions
- A saved baseline suitable for comparing tool selection, depth, and grounding in Parts 2 and 3

---

**Next:** [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}) — enable agent stream evaluators before comparing Parts 2 and 3.