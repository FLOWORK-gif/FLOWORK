# Spreadsheet (Excel) Manager

> Reads rows from or writes new rows to an Excel file (.xlsx, .xls). Supports sheet, row, and column selection.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `excel_manager_module` |
| Tier | Basic |
| Version | 1.0.0 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `operation` | loc.prop_operation_label | `enum` | `read` |
| `path_mode` | loc.prop_path_source_title | `enum` | `manual` |
| `manual_path` | loc.prop_manual_path_label | `filepath` | `` |
| `path_input_key` | loc.prop_path_input_key_label | `string` | `` |
| `sheet_name` | loc.prop_sheet_name_label | `string` | `Sheet1` |
| `data_to_write_key` | loc.prop_data_to_write_label | `string` | `data.new_rows` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | loc.port_success |
| `error` | loc.port_on_failure |

## Output Data Schema

This module adds the following keys to `payload['data']`:

| Payload Path (`data.key`) | Data Type | Description |
| --- | --- | --- |
| `data.excel_rows` | `list` | A list of dictionaries representing the rows read from the Excel file. |
| `data.file_path` | `string` | The full path of the Excel file that was processed. |

## API Reference

::: modules.excel_manager_module.processor
