# Segmentation

::: biopap.modules.segmentation.Segmentation

## Example settings for config file

Example settings in correct format for the config file.

```yaml
Segmentation:
  _biopap_module: <class 'biopap.modules.segmentation.Segmentation'>
  stim_channel: 'Status'
  start: -0.2
  end: 1
  baseline: None
  reference_markers:
    list:
    - '100'
    - '101'
    - '120'
    range: 10-69
  eventsfile: /path/to/your/events_metadata.csv
```