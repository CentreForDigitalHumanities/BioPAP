# SetChannelTypeAndMontage

::: biopap.modules.set_channel_type_and_montage.SetChannelTypeAndMontage

## Example settings for config file

Example settings in correct format for the config file.

```yaml
SetChannelTypeAndMontage:
    channel_types:
        misc: ['EXG1','EXG2','EXG3','EXG4','EXG5','EXG6','EXG7','EXG8','Erg1','Erg2','Plet']
        gsr: ['GSR1', 'GSR2']
        resp: ['Resp']
        temperature: ['Temp']
    mne_standard_montage: 'biosemi64'
```