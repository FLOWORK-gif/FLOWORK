# Set Variables / START

> Sets initial values or modifies multiple variables in a single step. Often used as the starting point of a workflow.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `set_variable_module` |
| Tier | Free |
| Version | 1.1.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `variables` | loc.prop_variables_label | `list` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `[dynamic]` | `any` | Output variables are generated dynamically based on the configuration in the properties. |

## API Reference

::: modules.set_variable_module.processor
