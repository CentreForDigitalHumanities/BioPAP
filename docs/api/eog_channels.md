# EOGChannels

::: biopap.modules.eog_channels.EOGChannels

## Example settings for config file

Example settings in correct format for the config file.

```yaml
EOGChannels:
  _biopap_module: <class 'biopap.modules.eog_channels.EOGChannels'>
  anode_channels:
  - EXG3
  - EXG5
  cathode_channels:
  - EXG4
  - EXG6
  ref_channels:
  - hEOG
  - vEOG
  drop_refs: false
  copy: false
```