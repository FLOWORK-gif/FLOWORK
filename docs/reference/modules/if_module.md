# IF Condition

> Evaluates a condition and directs the workflow to the 'True' or 'False' branch based on the result.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `if_module` |
| Tier | Free |
| Version | 1.1.0 |
| Author | awenk audico |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `variable_to_check` | loc.prop_if_variable_label | `string` | `` |
| `comparison_operator` | loc.prop_if_operator_label | `enum` | `==` |
| `value_to_compare` | loc.prop_if_value_label | `string` | `` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `true` | loc.port_true |
| `false` | loc.port_false |

## API Reference

::: modules.if_module.processor
