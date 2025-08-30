# Advanced Web Scraper (Selenium)

> Extracts data from modern websites that use JavaScript, by controlling a real browser. Now with caching.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `advanced_web_scraper_module_1a2b` |
| Tier | Basic |
| Version | 1.2 |
| Author | AWENK AUDICO |

## Configuration Properties

| ID (`config`) | Label | Type | Default Value |
| --- | --- | --- | --- |
| `url_source_mode` | loc.prop_url_source_mode_label | `enum` | `manual` |
| `target_url` | loc.prop_target_url_label | `string` | `https://` |
| `url_source_variable` | loc.prop_url_source_variable_label | `string` | `data.url` |
| `extraction_rules` | loc.prop_extraction_rules_label | `textarea` | `judul_artikel: article.detail h1.detail__title [text]<br>isi_artikel: article.detail .detail__body-text [text]` |
| `exclude_selectors` | loc.prop_exclude_selectors_label | `textarea` | `.lihatjg<br>.para_caption` |
| `wait_time` | loc.prop_wait_time_label | `integer` | `5` |
| `headless_mode` | loc.prop_headless_mode_label | `boolean` | `True` |
| `use_cache` | loc.prop_use_cache_label | `boolean` | `True` |

## Output Ports

| Port Name | Display Name |
| --- | --- |
| `success` | Success |
| `error` | Error |

## API Reference

::: modules.advanced_web_scraper_module_1a2b.processor
