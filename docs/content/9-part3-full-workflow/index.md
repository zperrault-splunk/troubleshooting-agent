---
title: "Part 3 — Full Workflow"
description: "Run the four-node LangGraph agent, compare how skills load per workflow step in Splunk Agent Observability, and contrast with Part 2's upfront keyword router."
weight: 9
navTitle: "Part 3 — Full Workflow"
duration: "30 minutes"
---

Run the alert through a four-node LangGraph workflow: **identify → categorize → investigate → report**. Part 3 keeps the `SKILL.md` format from Part 2 but loads each playbook only in the node that needs it.

Complete [Part 2 — Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) first. Its keyword injection and **`skill_router`** trace provide the comparison baseline.

## Part 2 vs Part 3 — how skills load in Splunk Agent Observability

Both parts inject playbooks into the system prompt; neither exposes skills as MCP tools. Compare their timing and orchestration:

| | Part 2 | Part 3 |
|---|--------|--------|
| **Orchestration** | Single ReAct loop (same as Part 1) | Four-node graph — each step has its own prompt |
| **Skill selection** | Keyword router on your chat/alert text | Python categorizer on the alert payload (APM / IM / RUM / Synthetics) |
| **When skills load** | **All at once**, before the agent's first LLM turn | **One step at a time**, when that graph node runs |
| **Agent Observability trace shape** | Separate **`skill_router`** trace, then **`Agent`** | **`load_skill:*`** spans **inside** each node (`identify`, `investigate`, `report`) |
| **Skills per run** | One domain skill + always-on `investigation-report` | Different skills per phase — see table below |

{{< notice title="Don't expect skill_router in Part 3" style="primary" >}}
Part 3 has no top-level **`skill_router`** block. Each skill appears under the node that loads it. If `skill_router` appears, verify that you ran the command from `part3_agent`.
{{< /notice >}}

### Part 2 trace (what you saw in Part 2)

Skills load **before** the ReAct loop starts. Splunk Agent Observability shows a sibling trace:

```text
Session: chat-… | part2_agent
├── skill_router                         ← all playbooks injected here
│   ├── load_skill:latency-spike
│   └── load_skill:investigation-report
└── Agent                                ← MCP tools only appear here
    ├── Agent::Agent
    ├── tools → o11y_search_alerts_or_incidents
    └── …
```

### Part 3 trace (what to look for instead)

Skills load **when each node runs**. Look for **`load_skill:*`** spans nested under named workflow nodes:

```text
Session: chat-… | part3_agent
└── part3_investigation
    ├── identify
    │   ├── load_skill:get-alerts-or-incidents   ← step 1 playbook
    │   ├── identify_llm
    │   └── identify_tools → o11y_…
    ├── categorize
    │   └── route_skill:troubleshoot-apm-incidents   ← routing decision (no prompt injection)
    ├── investigate
    │   ├── load_skill:troubleshoot-apm-incidents   ← product playbook injected here
    │   ├── load_skill:search-logs                  ← mandatory log search
    │   ├── investigate_llm
    │   └── investigate_tools → o11y_… / splunk_…
    └── report
        ├── load_skill:troubleshoot-report          ← final report format
        └── report_llm
```

The files remain `SKILL.md`; the orchestration changes:

- Part 2 selects a domain playbook with a keyword router and injects the report format up front.
- Part 3 loads the alert, product, log-search, and report playbooks at their respective workflow nodes.

## Skills loaded at each node

| Node | Skill(s) loaded | Why here |
|------|-----------------|----------|
| **identify** | `get-alerts-or-incidents` | Confirm the alert and capture IDs before investigating |
| **categorize** | *(routing only)* | Code picks product type — no full playbook yet |
| **investigate** | Product skill (e.g. `troubleshoot-apm-incidents`) + **`search-logs`** | Product-specific MCP steps + mandatory Splunk log search |
| **report** | `troubleshoot-report` | Structured handoff — only after evidence is gathered |

The investigate node also injects **`search-logs/indexes.md`**, the workshop tenant's Splunk index catalog. Confirm that log queries use a listed index rather than defaulting to `main`.

## Run Part 3

Run Part 3 from the CLI with the supplied mock Observability alert; Slack is not required. The prompt provides the service, environment, **`detectorId`**, and rule name. The **identify** node uses those fields to resolve the alert before investigation.

From `part3_agent`:

{{< notice title="Same agent stream" style="tip" >}}
Do **not** change `GALILEO_LOG_STREAM` in `.env` when you switch to `part3_agent`. Part 3 sessions appear in the same Agent Stream as Parts 1 and 2 — look for the `part3_agent` suffix in the session name.
{{< /notice >}}

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part3_agent
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. DetectorId HNcv52_AwAA. Rule: SRE Agent - PaymentService High Error Rate. Find root cause of the high error rate and confirm whether it is resolved."
```

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Mock alert fields" style="tip" >}}
The prompt carries the fields expected from an alert integration: **service** (`paymentservice`), **environment** (`splunk-hipster`), **detector ID**, and **rule name**. Part 3 uses them to fetch the alert payload, categorize it as APM, run **`troubleshoot-apm-incidents`** plus **`search-logs`**, and then apply **`troubleshoot-report`**.
{{< /notice >}}

Agent Observability sessions are named `chat-… | part3_agent`. Expect **`part3_investigation`** with **`identify` → `categorize` → `investigate` → `report`**, not a single ReAct **`Agent`** trace.

## Review Part 3 in Splunk Agent Observability

1. Open **Agent Stream** in the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io) and select a session ending in **`part3_agent`**.
2. Expand **`part3_investigation`**. Confirm the named nodes `identify`, `categorize`, `investigate`, and `report`; repeated generic `Agent:Agent` spans indicate the wrong agent.
3. Expand **`load_skill:*`** under **`identify`**, **`investigate`**, and **`report`**. Record which skill entered the prompt before each node's MCP calls.
4. Inspect `identify_tools` for alert resolution. Inspect `investigate_tools` for APM evidence and at least one `splunk_*` log search. Treat an empty result as an observation, not proof that no events exist. First confirm that the query succeeded and used the intended service, environment, index, and alert time window; also consider authorization, ingestion delay, and result limits.
5. In the final report, trace every metric and root-cause statement back to a tool result. Treat unsupported causality or a resolution claim without post-alert evidence as a failure.
6. Compare with the Part 2 session for the same alert. Tool names may overlap; node ownership and skill timing must differ.

{{< notice title="Tip" style="tip" >}}
Side-by-side comparison: Part 2 loads **`investigation-report`** at the start with the domain skill. Part 3 loads **`troubleshoot-report`** only in the **report** node — after investigate has gathered evidence.
{{< /notice >}}

## Exit checks

Before leaving Part 3, confirm:

- Part 2 and Part 3 use the same `SKILL.md` format.
- Part 2 loads selected skills up front in **`skill_router`**.
- Part 3 shows **`load_skill:*`** under the node that consumes each playbook.
- Alert identity, APM metrics or traces, and Splunk logs are separated in the trace and reconciled in the report.
- Any claim that the incident is resolved uses evidence after the alert window, not only a current empty-alert response.

This graph is a workshop implementation, not a production architecture guarantee. The production controls still required are covered in the next chapter.

For skill authoring details and the full Part 3 skill library, see [AI Skills]({{< relref "2-ai-skills" >}}).

**Next:** [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}) — what to harden after the workshop before running on live incidents.
