# AI Center

> An intelligent router to delegate prompts to the appropriate AI Provider or local model based on the task type.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `ai_center_module` |
| Tier | Pro |
| Version | 1.1 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `prompt_source_variable` | Prompt Source Variable | `string` | `data.prompt` |
| `provider_mapping` | Provider Mapping | `dictionary` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `text_output` | Text |
| `image_output` | Image |
| `audio_output` | Audio |
| `video_output` | Video |
| `code_output` | Code |
| `data_output` | Data/Analysis |
| `default_output` | Default / Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.ai_result_text` | `string` | The text result from the AI. |
| `data.ai_result_image_url` | `string` | The image URL result from the AI. |
| `data.ai_result_audio_file` | `string` | The audio file path result from the AI. |
| `data.ai_result_video_url` | `string` | The video URL result from the AI. |
| `data.ai_result_code` | `string` | The code snippet result from the AI. |
| `data.ai_result_json` | `object` | The JSON data/analysis result from the AI. |

## API Reference

::: modules.ai_center_module.processor
