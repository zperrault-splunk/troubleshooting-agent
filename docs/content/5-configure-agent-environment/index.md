---
title: "Configure Environment"
description: "Install dependencies and verify everything is ready before Part 1."
weight: 5
navTitle: "Configure Environment"
duration: "10 minutes"
---

Your workshop instance and credentials are already configured. Before Part 1, install the agent dependencies. The agent names your Agent Stream from `$INSTANCE` (for example, `shw-2cb1`) so your traces stay separate from other attendees.

## Install dependencies

From the repository on your instance, create and activate a virtual environment, then install the workshop package:

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-workshop.txt
pip install -e . --no-deps
```

{{% /tab %}}
{{% tab title="Example Output" %}}

```text
Successfully installed langchain-1.3.14 ...
Successfully installed troubleshooting-agent-0.1.0
```

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Tip" style="tip" >}}
Run `source .venv/bin/activate` whenever you open a new SSH session. Your prompt should show `(.venv)` when the environment is active.
{{< /notice >}}

## Verify setup

With the virtual environment active, run both readiness checks:

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
source .venv/bin/activate
cd part1_agent
troubleshooting-agent doctor
troubleshooting-agent mcp-doctor
```

{{% /tab %}}
{{% tab title="Example Output" %}}

```text
Part 1 — minimal MCP-only agent
LLM provider: openai
Base URL: https://lite-llm-proxy.splunko11y.com/v1
Model: gpt-4.1-mini
OpenAI-compatible LLM: OK
Ready.
Part 1 — minimal MCP-only agent
MCP integrations enabled: o11y, cloud
Feature flags: ENABLE_SPLUNK_O11Y=True, ENABLE_SPLUNK_CLOUD_MCP=True, ENABLE_SPLUNK_MCP=False
MCP transport: /usr/bin/npx (mcp-remote)
(Use `node --trace-warnings ...` to show where the warning was created)
splunk_o11y: OK (12 tools)
  - o11y_execute_signalflow_program
  - o11y_get_apm_environments
  - o11y_get_apm_service_errors_and_requests
  - o11y_get_apm_services
  - o11y_search_alerts_or_incidents
  - o11y_get_apm_exemplar_traces
  - o11y_get_apm_service_latency
  - o11y_generate_signalflow_program
  - o11y_get_apm_trace_tool
  - o11y_get_apm_service_dependencies
  - o11y_get_metric_names
  - o11y_get_metric_metadata
splunk_cloud_mcp: OK (9 tools)
  - splunk_get_info
  - splunk_get_indexes
  - splunk_get_index_info
  - splunk_get_user_list
  - splunk_get_user_info
  - splunk_run_query
  - splunk_get_metadata
  - splunk_get_kv_store_collections
  - splunk_get_knowledge_objects
MCP ready.
```

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Important" style="primary" >}}
Continue only when both commands report **Ready**. `doctor` verifies the LLM connection; `mcp-doctor` verifies the Splunk Observability and Splunk Cloud MCP endpoints and lists the available tools. If either check fails, copy the failure output and ask your facilitator for help. {{< /notice >}}

---

**Next:** [Part 1 — Baseline Agent]({{< relref "6-part1-baseline-agent" >}}) — run your first investigation and review traces in the terminal and Splunk Agent Observability.