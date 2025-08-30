# Agentic Web Scraper

> Deploys an autonomous AI agent to navigate websites, interact with elements, and extract information to fulfill a high-level objective.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `intelligent_content_extractor` |
| Tier | Architect |
| Version | 3.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `objective_source_mode` | loc.prop_objective_source_mode_label | `enum` | `manual` |
| `manual_objective` | loc.prop_manual_objective_label | `textarea` | `Find the top 3 latest news about AI technology from detik.com` |
| `objective_source_variable` | loc.prop_objective_source_variable_label | `string` | `data.prompt` |
| `max_steps` | loc.prop_max_steps_label | `integer` | `10` |
| `ai_brain_endpoint` | loc.prop_ai_brain_label | `enum` | `` |
| `headless_mode` | loc.prop_headless_mode_label | `boolean` | `True` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.agent_final_answer` | `string` | The final processed information extracted by the AI agent. |
| `data.interaction_log` | `list` | A step-by-step log of the agent's actions and observations. |

## API Reference

::: modules.intelligent_content_extractor.processor
