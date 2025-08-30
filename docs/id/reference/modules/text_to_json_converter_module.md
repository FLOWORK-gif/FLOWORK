# Text to JSON Converter

> Converts a plain text string into a structured list of JSON objects based on user-defined delimiters and keys.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `text_to_json_converter_module` |
| Tier | Free |
| Version | 1.0.0 |
| Author | AWENK AUDICO & Gemini |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `source_text_variable` | loc.prop_source_text_label | `string` | `data.raw_text` |
| `line_delimiter` | loc.prop_line_delimiter_label | `string` | `\n` |
| `value_delimiter` | loc.prop_value_delimiter_label | `string` | `,` |
| `key_names` | loc.prop_key_names_label | `string` | `column1,column2,column3` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.json_data` | `list` | The resulting list of JSON objects after conversion. |

## API Reference

::: modules.text_to_json_converter_module.processor
