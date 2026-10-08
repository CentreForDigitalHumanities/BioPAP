# Plot

::: biopap.modules.plot.Plot

Wrapper around several plot-functions:

+ [Plot raw data](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.plot) (`PLOT`)
+ [Plot sensors positions](https://mne.tools/stable/generated/mne.viz.plot_sensors.html) (`SENSORS`)
+ [Plot power or amplitude spectra](https://mne.tools/stable/generated/mne.time_frequency.Spectrum.html#mne.time_frequency.Spectrum.plot) (`SPECTRUM_PLOT`)
+ [Plot power spectral density, separately for each channel](https://mne.tools/stable/generated/mne.time_frequency.Spectrum.html#mne.time_frequency.Spectrum.plot_topo) (`SPECTRUM_TOPO`)
+ [Plot scalp topography of PSD for chosen frequency bands](https://mne.tools/stable/generated/mne.time_frequency.Spectrum.html#mne.time_frequency.Spectrum.plot_topomap) (`SPECTRUM_TOPO_MAP`)

## Example settings for config file

Example settings in correct format for the config file.

```yaml
Plot:
    plot_types: 8
    save_folder: './examples/data/plots'
    save_postfix: 'participant1'
    save_overwrite: False
```

The value of `plot_types` translates to actual types thus:

+ `PLOT` = 1
+ `SENSORS` = 2
+ `SPECTRUM_PLOT` = 4
+ `SPECTRUM_TOPO` = 8
+ `SPECTRUM_TOPO_MAP` = 16

To generate different types at the same time, you can add the values. For instance, `plot_types: 11`
translates to `PLOT`, `SENSORS`, and `SPECTRUM_TOPO`, because 11 equals 1 + 2 + 8.
