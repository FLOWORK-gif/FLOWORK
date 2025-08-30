# Prompt Receiver

> Receives a prompt from a UI widget via an event and passes it to the next node.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `prompt_receiver_module` |
| Tier | Free |
| Version | 1.0 |
| Author | AWENK AUDICO |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `output` | Output |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.prompt` | `string` | The text prompt received from the sender widget. |

## API Reference

::: modules.prompt_receiver_module.processor
