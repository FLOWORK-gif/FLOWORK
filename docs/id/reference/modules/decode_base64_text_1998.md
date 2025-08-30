# Decode Base64 Text

> Decodes a Base64 string back into plain text.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `decode_base64_text_1998` |
| Tier | Free |
| Version | 1.0 |
| Author | Flowork Contributor |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `base64_to_decode` | Base64 Text to Decode | `string` | `data.encoded_text` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.decoded_text` | `string` | The plain text result from the decoded Base64 string. |

## API Reference

::: modules.decode_base64_text_1998.processor
