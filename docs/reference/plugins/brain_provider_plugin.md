# AI Brain Provider

> A universal AI Brain for agents. Select any configured AI provider (local model or API) to act as the agent's decision-making core.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `brain_provider_plugin` |
| Tier | Pro |
| Version | 1.2.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `selected_ai_provider` | loc.brain_provider_select_label | `enum` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `brain_output` | Brain |

## API Reference

::: plugins.brain_provider_plugin.processor
