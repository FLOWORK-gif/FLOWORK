# Image Generator Tools

> A tool for AI agents to generate images from a text prompt using the globally configured AI model for image tasks.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `image_generator_tools` |
| Tier | Pro |
| Version | 1.1.0 |
| Author | AWENK AUDICO & Gemini |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `prompt_source_variable` | loc.prop_image_gen_prompt_source_label | `string` | `data.prompt_gambar` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.generated_image_path` | `string` | The full local path to the generated image file. |

## API Reference

::: plugins.image_generator_tools.processor
