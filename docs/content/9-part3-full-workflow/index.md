---
title: "Part 3: Full Workflow"
description: "Run the four-node LangGraph agent, compare how skills load per workflow step in Splunk Agent Observability, and contrast with Part 2's upfront keyword router."
weight: 9
navTitle: "Part 3: Full Workflow"
duration: "30 minutes"
---

Run the alert through a four-node LangGraph workflow: **identify → categorize → investigate → report**. Part 3 keeps the `SKILL.md` format from Part 2 but loads each playbook only in the node that needs it.

Complete [Part 2: Skill Playbooks]({{< relref "8-part2-skill-playbooks" >}}) first. Its keyword injection and `skill_router` trace provide the comparison baseline.

## Part 2 vs Part 3: How skills load in Splunk Agent Observability

Both parts inject playbooks into the system prompt; neither exposes skills as MCP tools. Compare their timing and orchestration:


|                                     | Part 2                                              | Part 3                                                                          |
| ----------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Orchestration**                   | Single ReAct loop (same as Part 1)                  | Four-node graph: each step has its own prompt                                   |
| **Skill selection**                 | Keyword router on your chat/alert text              | Python categorizer on the alert payload (APM / IM / RUM / Synthetics)           |
| **When skills load**                | **All at once**, before the agent's first LLM turn  | **One step at a time**, when that graph node runs                               |
| **Agent Observability trace shape** | Separate `skill_router` trace, then `Agent`         | `load_skill:`* spans **inside** each node (`identify`, `investigate`, `report`) |
| **Skills per run**                  | One domain skill + always-on `investigation-report` | Different skills per phase                                                      |


{{< notice title="Don't expect skill_router in Part 3" style="primary" >}}
Part 3 has no top-level `skill_router` block. Each skill appears under the node that loads it. If `skill_router` appears, verify that you ran the command from `part3_agent`.
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

Skills load **when each node runs**. Look for `load_skill:`* spans nested under named workflow nodes:

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


| Node            | Skill(s) loaded                                                   | Why here                                                 |
| --------------- | ----------------------------------------------------------------- | -------------------------------------------------------- |
| **identify**    | `get-alerts-or-incidents`                                         | Confirm the alert and capture IDs before investigating   |
| **categorize**  | *(routing only)*                                                  | Code picks product type                                  |
| **investigate** | Product skill (e.g. `troubleshoot-apm-incidents`) + `search-logs` | Product-specific MCP steps + mandatory Splunk log search |
| **report**      | `troubleshoot-report`                                             | Structured handoff only after evidence is gathered       |

## Run Part 3

Run Part 3 from the CLI with a mock Observability alert. The prompt provides the service, environment, and rule name. The **identify** node uses those fields to resolve alert context before investigation.

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part3_agent
troubleshooting-agent chat "Troubleshoot the Splunk Observability alert: paymentservice in splunk-hipster environment. Rule: obs1386 | sre agent | high error rate. Find root cause of the high error rate."
```

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Mock alert fields" style="tip" >}}
The prompt carries fields expected from an alert integration: **service** (`paymentservice`), **environment** (`splunk-hipster`), and **rule name (**obs1386 | sre agent | high error rate**)**. Part 3 uses them to resolve alert context, categorize it as APM, run `troubleshoot-apm-incidents` plus `search-logs`, and then apply `troubleshoot-report`.
{{< /notice >}}

Agent Observability sessions are named `chat-… | part3_agent`. Expect `part3_investigation` with `identify` **→** `categorize` **→** `investigate` **→** `report`, not a single ReAct `Agent` trace.

## Review Part 3 in Splunk Agent Observability

1. Open **Agent Stream** in the [Splunk Agent Observability console](https://console.multitenant.galileocloud.io) and select a session ending in `part3_agent`.
2. Expand `part3_investigation`. Confirm the named nodes `identify`, `categorize`, `investigate`, and `report`; repeated generic `Agent:Agent` spans indicate the wrong agent.
3. Expand `load_skill:*` under `identify`, `investigate`, and `report`. Record which skill entered the prompt before each node's MCP calls.
4. Inspect `identify_tools` for alert resolution. Inspect `investigate_tools` for APM evidence and at least one `splunk_*` log search. Treat an empty result as an observation, not proof that no events exist. First confirm that the query succeeded and used the intended service, environment, index, and alert time window; also consider authorization, ingestion delay, and result limits.
5. In the final report, trace every metric and root-cause statement back to a tool result. Treat unsupported causality or a resolution claim without post-alert evidence as a failure.
6. Compare with the Part 2 session for the same alert. Tool names may overlap; node ownership and skill timing must differ.
7. Compare **Action Completion (SLM)** and its explanation across the Part 1, Part 2, and Part 3 sessions. All three use the same alert prompt.

{{< notice title="Tip" style="tip" >}}
Side-by-side comparison: Part 2 loads `investigation-report` at the start with the domain skill. Part 3 loads `troubleshoot-report` only in the **report** node after investigate has gathered evidence. {{< /notice >}}

## Part 3 Recap
- Ran the same high-error alert through the four-node **identify → categorize → investigate → report** workflow.
- Inspected `load_skill:*` spans to see each playbook enter the prompt only when its graph node needed it.
- Followed alert context, APM evidence, and Splunk log evidence from separate tool calls into one structured report.
- Compared Action Completion and trace evidence across the Part 1 baseline, Part 2 playbook injection, and Part 3 structured workflow.
- Part 2 and Part 3 share the `SKILL.md` format but differ in orchestration and skill-loading time.
- Named graph nodes make routing, evidence collection, and reporting responsibilities visible in the trace.
- Combining Observability and Splunk evidence produces a stronger investigation than relying on one signal source.
- A resolution claim requires supporting evidence after the alert window; an empty current-alert result is not enough.

This graph is a workshop implementation, not a production architecture guarantee. The production controls still required are covered in the next chapter. For skill authoring details and the full Part 3 skill library, see [AI Skills]({{< relref "2-ai-skills" >}}).

**Next:** [Production-Ready Agent]({{< relref "10-production-ready-agent" >}}): what to harden after the workshop before running on live incidents.