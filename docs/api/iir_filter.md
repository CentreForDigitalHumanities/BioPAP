# IIRFilter

::: biopap.modules.iir_filter.IIRFilter

## Example settings for config file

Example settings in correct format for the config file.

```yaml
IIRFilter:
  _biopap_module: <class 'biopap.modules.iir_filter.IIRFilter'>
  l_freq: 0.1
  h_freq: 35
  order: 4
  ftype: 'butter'
  method: 'fir'
```

Please note that by setting method to either 'iir' or 'fir,
this module can apply either an IIR-filter, or an FIR-filter.