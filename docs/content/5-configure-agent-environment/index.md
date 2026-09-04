---
title: "Configure Environment"
description: "Install dependencies, personalize your Agent Observability settings, and verify everything is ready before Part 1."
weight: 5
navTitle: "Configure Environment"
duration: "10 minutes"
---

Your workshop instance and credentials are already configured. Before Part 1, install the agent dependencies and give your Agent Observability agent stream a unique name. That name will let you isolate your traces from other attendees' traces.

## Install dependencies

From the repository on your instance, create and activate a virtual environment, then install the workshop package:

{{< tabs >}}
{{% tab title="Script" open="true" %}}

```bash
cd ~/troubleshooting-agent
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

## Personalize your Agent Observability settings

Create `.env`, then set an Agent Observability stream name that is unique to your instance:

```bash
cd ~/troubleshooting-agent
cp .env.example .env
vi .env
```

Add or update these lines. Use the value printed by `echo $INSTANCE` (see [Connect to EC2]({{< relref "3-connect-ec2" >}})). Replace `$INSTANCE` with that value; do not leave the dollar sign in `.env`:

```bash
ENABLE_GALILEO=true
GALILEO_PROJECT="sre-agent-wkshp"
GALILEO_LOG_STREAM="sre-agent-wkshp-$INSTANCE"
```

For example, if `echo $INSTANCE` prints `shw-2cb1`:

```bash
GALILEO_PROJECT="sre-agent-wkshp"
GALILEO_LOG_STREAM="sre-agent-wkshp-shw-2cb1"
```

{{< notice title="Tip" style="tip" >}}
Keep **`GALILEO_PROJECT`** and **`GALILEO_LOG_STREAM`** unchanged across Parts 1–3. When you switch to `part2_agent` or `part3_agent`, the same **Agent Stream** will hold every session for side-by-side comparison.
{{< /notice >}}

Save and exit: press `Esc`, type `:wq`, then press Enter. Verify that the file resembles this example and contains your instance name:

{{< diagram src="images/env-example.png" alt="Example .env file with Agent Observability enabled and a personalized agent stream name" >}}

## Verify setup

With the virtual environment active and `.env` saved, run both readiness checks:

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
(.venv) splunk@ip-172-31-19-27:~/troubleshooting-agent/part1_agent$ troubleshooting-agent doctor
Part 1 — minimal MCP-only agent
LLM provider: openai
Base URL: https://lite-llm-proxy.splunko11y.com/v1
Model: gpt-4.1-mini
OpenAI-compatible LLM: OK
Ready.
(.venv) splunk@ip-172-31-19-27:~/troubleshooting-agent/part1_agent$ troubleshooting-agent mcp-doctor
Part 1 — minimal MCP-only agent
splunk_o11y: OK (12 tools)
  - o11y_get_metric_names
  - o11y_get_apm_trace_tool
  - o11y_get_apm_exemplar_traces
  - o11y_generate_signalflow_program
  - o11y_get_apm_service_errors_and_requests
  - o11y_get_apm_service_latency
  - o11y_get_apm_services
  - o11y_search_alerts_or_incidents
  - o11y_execute_signalflow_program
  - o11y_get_apm_service_dependencies
  - o11y_get_apm_environments
  - o11y_get_metric_metadata
MCP ready.
```

{{% /tab %}}
{{< /tabs >}}

{{< notice title="Important" style="primary" >}}
Continue only when both commands report **Ready**. `doctor` verifies the LLM connection; `mcp-doctor` verifies the Splunk Observability MCP endpoint and lists the available tools. If either check fails, copy the failure output and ask your facilitator for help.
{{< /notice >}}

---

**Next:** [Part 1 — Baseline Agent]({{< relref "6-part1-baseline-agent" >}}) — run your first investigation and review traces in the terminal and Splunk Agent Observability.
