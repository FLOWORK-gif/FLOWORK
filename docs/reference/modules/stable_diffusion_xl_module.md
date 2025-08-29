# Stable Diffusion XL Image Generator

> Generates images from text prompts using local Stable Diffusion XL models.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `stable_diffusion_xl_module` |
| Tier | Free |
| Version | 1.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `model_folder` | AI Model | `enum` | `` |
| `prompt` | Prompt | `textarea` | `a cinematic photo of a raccoon astronaut, professional photography, 8k` |
| `negative_prompt` | Negative Prompt | `textarea` | `blurry, worst quality, low quality, cartoon, anime` |
| `output_folder` | Output Folder | `string` | `` |
| `output_filename_prefix` | Output Filename Prefix (Optional) | `string` | `` |
| `width` | Width | `integer` | `1024` |
| `height` | Height | `integer` | `1024` |
| `guidance_scale` | Guidance Scale (CFG) | `float` | `7.5` |
| `num_inference_steps` | Inference Steps | `integer` | `30` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.image_path` | `string` | The full local path to the generated image file. |

## API Reference

::: modules.stable_diffusion_xl_module.processor
