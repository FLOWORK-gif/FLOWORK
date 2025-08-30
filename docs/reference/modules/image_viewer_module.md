# Image Viewer

> Displays an image in a popup window from a local file path provided by the payload or manual input.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `image_viewer_module` |
| Tier | Free |
| Version | 1.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `path_mode` | loc.prop_image_source_mode_label | `enum` | `dynamic` |
| `image_path_variable` | loc.prop_image_path_variable_label | `string` | `data.image_path` |
| `manual_image_path` | loc.prop_manual_image_path_label | `filepath` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.image_path` | `string` | The path of the image that was displayed. |

## API Reference

::: modules.image_viewer_module.processor
