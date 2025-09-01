# Encode Base64 Text

> Encodes a given string into Base64 format.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `encode_base64_text_1998` |
| Tier | Free |
| Version | 1.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `text_to_encode` | Text to Encode | `string` | `data.text_asli` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.encoded_text` | `string` | The Base64 encoded result of the input text. |

## API Reference

::: modules.encode_base64_text_1998.processor
