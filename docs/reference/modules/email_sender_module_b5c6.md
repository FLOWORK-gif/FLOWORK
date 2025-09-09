# Email Sender

> Sends an email via an SMTP server. The recipient, subject, and body can be configured or taken dynamically from the payload.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `email_sender_module_b5c6` |
| Tier | Basic |
| Version | 1.0.0 |
| Author | awenk audico |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `smtp_server` | loc.prop_smtp_server_label | `string` | `` |
| `smtp_port` | loc.prop_smtp_port_label | `integer` | `587` |
| `smtp_username` | loc.prop_smtp_username_label | `string` | `` |
| `smtp_password` | loc.prop_smtp_password_label | `password` | `` |
| `recipient_mode` | loc.prop_recipient_mode_label | `enum` | `` |
| `recipient` | loc.prop_recipient_manual_label | `string` | `` |
| `recipient_variable` | loc.prop_recipient_variable_label | `string` | `` |
| `subject_mode` | loc.prop_subject_mode_label | `enum` | `` |
| `subject` | loc.prop_subject_manual_label | `string` | `` |
| `subject_variable` | loc.prop_subject_variable_label | `string` | `` |
| `body_mode` | loc.prop_body_mode_label | `enum` | `` |
| `body` | loc.prop_body_manual_label | `textarea` | `` |
| `body_variable` | loc.prop_body_variable_label | `string` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | loc.port_success |
| `error` | loc.port_on_failure |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.email_status` | `string` | The status of the email sending operation, e.g., 'Sent successfully'. |
| `data.recipient` | `string` | The email address the email was sent to. |

## API Reference

::: modules.email_sender_module_b5c6.processor
