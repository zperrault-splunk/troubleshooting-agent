---
title: "Production-Ready Agent"
description: "Harden the Part 3 troubleshooting workflow for live incidents — alert intake, orchestration, MCP reliability, and operational guardrails."
weight: 10
navTitle: "Production-Ready Agent"
duration: "10 minutes"
---

The Part 3 implementation is suitable for learning and controlled evaluation. It is not production-ready. The four-node graph, playbooks, MCP calls, and Splunk Agent Observability traces demonstrate the workflow, but they do not provide the availability, security, tenancy, change-control, or safety controls required for live incident operations.

Use this page as a hardening checklist after [Part 3 — Full Workflow]({{< relref "9-part3-full-workflow" >}}). There are no lab steps.

## Workshop architecture and production controls

The workshop uses a CLI mock alert, `.env` credentials on one host, per-investigation MCP stdio sessions, prompt-driven node behavior, and human review of traces. A production service must define and test controls around those components. Retaining the four-node graph is an implementation choice, not evidence that the system is safe or reliable at scale.

## Alert intake and context

- Replace the mock CLI prompt with a durable, authenticated trigger such as the Slack Events API, a webhook, or a queue consumer.
- Normalize input before the graph starts. Require a typed payload containing `event_id`, `detector_id`, `service`, `environment`, `rule`, and alert timestamps; reject or quarantine malformed events.
- Resolve the O11y alert record in deterministic code, as `fetch_alert_payload` does, before spending LLM or MCP tool budget.
- Derive investigation windows from alert start, last-triggered, and clear timestamps. Record the exact window passed to every metric, trace, and log tool so results can be reproduced.
- Use `event_id` as the idempotency key. Deduplicate retries and concurrent deliveries, and define when a cleared alert should receive a shortened verification run instead of a full investigation.

## Orchestration and skills

- Define a schema for each node's inputs, outputs, evidence references, and failure state. Enforce required fields and maximum tool calls instead of relying on prompt text alone.
- Keep deterministic routing for known APM, IM, RUM, and Synthetics payloads. If an LLM handles `unknown`, log the ambiguity and require an explicit confidence threshold or human review.
- Carry tool name, normalized input, time window, result status, and evidence identifiers between nodes. A report should distinguish empty data from tool failure, timeout, authorization failure, and invalid input.
- Version `SKILL.md` files with the application. Require review, product-specific regression cases, and evaluators for report structure, tool-use completeness, and unsupported claims. See [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}).

## MCP, Splunk, and reliability

- Replace per-investigation MCP stdio setup with a supported connection lifecycle. Set connection, call, and overall investigation timeouts; bound retries with backoff and jitter; and apply per-tenant concurrency and rate limits.
- Validate tool inputs against schemas before dispatch. Preserve the exact normalized input and result status in the trace, with secrets and sensitive fields redacted.
- Maintain `search-logs/indexes.md`, or replace it with an authoritative configuration service. Test index mappings during deployment. A stale index can produce a credible but false “no logs found” conclusion.
- Define partial-result behavior. If Splunk MCP is unavailable, return the O11y evidence with **Logs: unavailable** and the tool failure reason. Do not represent unavailable logs as an empty search result.
- Require trace evidence before claiming a causal service or operation. Require a post-alert comparison window before claiming recovery; current status alone does not establish when or why the signal cleared.

## Safety, trust, and operations

- Keep investigation and reporting read-only until action authorization is designed. Posting messages, opening tickets, or executing remediation requires scoped identities, policy checks, a preview, explicit confirmation, an audit record, and a rollback path where possible.
- Store API tokens in a vault or KMS-backed secret service, not `.env` on shared hosts. Scope MCP credentials by tenant and environment. Enforce tenant isolation in state, caches, traces, and tool authorization.
- Redact tokens and PII before logs or Agent Observability traces leave the process. Set retention and access policies for prompts, tool inputs, results, and reports.
- Monitor session volume, queue delay, node latency, tool error and timeout rates, retry volume, evaluator regressions, and incomplete reports. Alert on service-level objectives defined for the agent.
- Set recursion, token, wall-clock, and parallel-call budgets per investigation. Track spend and latency by node; the Part 3 investigate node is the likely cost driver, but measure it in your environment.
- Test malformed alerts, duplicate delivery, empty metric series, missing traces, stale indexes, MCP outages, rate limits, model refusal, and partial node completion before shadow traffic.

{{< notice title="Workshop → production path" style="tip" >}}
Start with one alert type, such as APM error rate. Add authenticated Slack or webhook intake, deterministic alert normalization, bounded tool calls, and an Agent Observability evaluator for **`troubleshoot-report`** completeness. Run in shadow mode: the agent reports and humans investigate and act. Promote only against explicit accuracy, completeness, latency, failure-rate, and safety criteria; stable evaluator scores alone are insufficient.
{{< /notice >}}

## Related reading

- [Part 3 — Full Workflow]({{< relref "9-part3-full-workflow" >}}) — graph nodes and Agent Observability trace shape
- [AI Skills]({{< relref "2-ai-skills" >}}) — authoring and testing playbooks
- [Configure Evaluators]({{< relref "7-galileo-logstream-evaluators" >}}) — quality gates for agent outputs
- [FAQ]({{< relref "11-faq" >}}) — setup, Parts 1–3, evaluators, and common lab issues

**Next:** [FAQ]({{< relref "11-faq" >}}) — forty questions covering the overall workshop and each part.
