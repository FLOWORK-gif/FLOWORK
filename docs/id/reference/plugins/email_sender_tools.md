# Email Sender Tools

> Sends an email. 'data' must contain 'recipient_to', 'subject', 'body'. For attachments, provide an 'attachments' list. RULE: For existing files (like images), provide the path as a STRING. To create a file from text (like an article), provide an object {'filename': 'file.txt', 'content': 'your text...'}. PRO TIP: For content, you can also use a payload variable like {{data.article_text}} to avoid sending large texts to the AI.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `email_sender_tools` |
| Tier | Basic |
| Version | 1.3.0 |
| Author | awenk audico |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `recipient_to` | loc.prop_recipient_manual_label | `string` | `` |
| `subject` | loc.prop_subject_manual_label | `string` | `` |
| `body` | loc.prop_body_manual_label | `textarea` | `` |
| `attachment_path_variable` | loc.prop_attachment_path_label | `string` | `data.image_path` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.email_status` | `string` | The status of the email sending operation (e.g., 'Sent successfully'). |

## API Reference

::: plugins.email_sender_tools.processor
