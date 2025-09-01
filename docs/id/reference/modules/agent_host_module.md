# Agent Host

> Acts as an autonomous agent on the canvas, using connected nodes as its tools, brain, and prompt to achieve a high-level objective.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `agent_host_module` |
| Tier | Architect |
| Version | 2.2 |
| Author | AWENK AUDICO |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success (Final Answer) |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.agent_final_answer` | `string` | The final answer or result from the agent after completing its objective. |
| `data.agent_interaction_log` | `list` | A step-by-step log of the agent's thoughts, actions, and observations. |

## API Reference

::: modules.agent_host_module.processor
