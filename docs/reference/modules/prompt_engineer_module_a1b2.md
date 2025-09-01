# Prompt Engineer

> Selects a pre-saved prompt template from the Prompt Manager and outputs its content. (Refactored to align with architecture)

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `prompt_engineer_module_a1b2` |
| Tier | Free |
| Version | 2.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `selected_prompt_id` | loc.prop_prompt_template_select_label | `enum` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | success |
| `error` | error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.prompt_template` | `string` | The full text content of the selected prompt template. |

## API Reference

::: modules.prompt_engineer_module_a1b2.processor
