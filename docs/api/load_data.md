# LoadData

::: biopap.modules.load_data.LoadData

## Example settings for config file

Example settings in correct format for the config file.

```yaml
LoadData:
    preload: True
```

If you need to pass extra arguments (**kwargs) to any of the underlying functions,
use `load_bdf`, `load_edf`, `load_fif`, or `load_epochs` as key, depending on what
type of file you are loading. These will be passed on as kwargs to `mne.io.read_raw_bdf`,
`mne.io.read_raw_edf`, `mne.io.read_raw_fif` and `mne.read_epochs`, respectively.

When you run a pipeline using the Pipeline-class, LoadData should be omitted from
your pipeline-configuration, as it is called automatically when the pipeline is
created. If you need to pass extra arguments to any of the underlying functions
while running a pipeline, either add them to your configuration-file in a section
labeled `Pipeline` (see example below), or pass them directly as **kwargs when
creating a new Pipeline.

```yaml
Pipeline:
    load_bdf:
        encoding: 'latin-1'
        exclude_after_unique: true
    load_epochs:
        proj: 'delayed'
```