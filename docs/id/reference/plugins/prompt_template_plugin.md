# Prompt Template

> Selects a pre-saved prompt template from the Prompt Manager and outputs its content.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `prompt_template_plugin` |
| Tier | Free |
| Version | 2.1.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `selected_prompt_id` | loc.prop_prompt_template_select_label | `enum` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.prompt_template` | `string` | The full text content of the selected prompt template. |

## API Reference

::: plugins.prompt_template_plugin.processor
