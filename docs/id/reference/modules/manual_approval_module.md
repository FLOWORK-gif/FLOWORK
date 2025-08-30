# Manual Approval

> Pauses the workflow and displays a popup message for user interaction.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `manual_approval_module` |
| Tier | Free |
| Version | 1.0 |
| Author | Flowork Contributor |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `approval_message` | Approval Message | `string` | `Are you sure you want to continue with this process?` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `APPROVED` | APPROVED |
| `REJECTED` | REJECTED |

## API Reference

::: modules.manual_approval_module.processor
