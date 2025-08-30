# Email Reader (IMAP)

> Connects to an IMAP email server to find and read emails, and extract specific information like verification links or codes.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `email_reader_module` |
| Tier | Pro |
| Version | 1.1 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `search_from` | loc.prop_email_reader_from_label | `string` | `` |
| `search_subject` | loc.prop_email_reader_subject_label | `string` | `` |
| `mark_as_read` | loc.prop_email_reader_mark_read_label | `boolean` | `True` |
| `delete_after_read` | loc.prop_email_reader_delete_label | `boolean` | `False` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `not_found` | Email Not Found |
| `error` | Error |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.email_body` | `string` | The entire plain text content of the found email. |

## API Reference

::: modules.email_reader_module.processor
