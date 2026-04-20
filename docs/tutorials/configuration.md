# Configuration

BioPAP uses configuration files to manage data paths and module parameters. This tutorial explains how to set up and customize these configurations.

## Configuration Files

You'll work with two main configuration files:

### 1. `my_config.ipynb` (Notebook Configuration)

This is a personal configuration notebook that stores paths to your data and configuration file. Start with the provided template `example.my_config.ipynb` and create your own `my_config.ipynb` file. This keeps your local settings separate from the repository to avoid conflicts with GitHub updates.

### 2. `pipeline.yaml` (Module Configuration)

This YAML file contains the parameters for all preprocessing modules. Start with the template `pipeline.yaml.example` and create your own `pipeline.yaml` to store the settings for the modules you'll use in your pipeline.

## Loading Configuration Files

The notebook uses the following code to load both configuration files:

```python
from pathlib import Path

config_notebook = './my_config.ipynb'

if Path(config_notebook).exists():
    %run {config_notebook}
else:
    data_file = '/biopap/data/example.bdf'
    config_file = './data/pipeline.yaml'

if not Path(config_file).exists():
    print(f"Config file {config_file} does not exist.")

if not Path(data_file).exists():
    print(f"Data file {data_file} does not exist.")
```

!!! info "Note"

    This code is already included in the Jupyter notebook. It automatically loads your custom configurations if they exist, or falls back to defaults.

## Configuration Parameters

Module settings are defined in `pipeline.yaml` using YAML format. Each module has its own section with specific parameters. Some parameters accept simple values (strings, numbers), while others expect dictionaries or lists. Always consult the Module documentation.

### Example Configuration File

```yaml
Anonymize:
    daysback: 100
    experimenter: 'J. Jansen'
    participant_id: 'AB00123'

Rereference:
    ref_channels: ['EXG1', 'EXG2']

EOGChannels:
    ref_channels: ['hEOG', 'vEOG']
    anode_channels: ['EXG3', 'EXG5']
    cathode_channels: ['EXG4', 'EXG6']

IIRFilter:
    l_freq: 0.1
    h_freq: 35

Downsample:
    sfreq: 250

SaveOutput:
    export_formats: ['fif', 'csv']
    output_file: './output/preprocessed_data'
    overwrite: True
```

## Overriding Configuration Parameters

While your `pipeline.yaml` file defines default settings, you can temporarily override these values when running modules. This is useful for testing different parameter combinations without modifying your configuration file.

### Override When Running Modules Independently

When running a module outside the pipeline, pass parameter values directly to the constructor:

```python
# Override default IIRFilter settings (assuming defaults: l_freq=0.1, h_freq=35)
flt = IIRFilter(
    raw=load.raw,
    l_freq=0.2,
    h_freq=50
)
```

### Override When Adding Steps to a Pipeline

When adding a module to a pipeline using `pipe.add_step()`, use the `cfg` parameter to override settings:

```python
# Override IIRFilter settings in the pipeline
pipe.add_step(IIRFilter, cfg={'l_freq': 0.2, 'h_freq': 50})
```

## Advanced: Passing Additional MNE Parameters

BioPAP modules use the MNE library internally. You can pass additional parameters to specific MNE functions by organizing them under the function name. Each module uses different MNE functions, so consult the module's documentation to see which functions are used.

### In Configuration File

Parameters are organized by the name of the MNE function they apply to. For example, the Segmentation module uses `find_events` and `Epochs`:

```yaml
Segmentation:
    stim_channel: 'Status'
    start: -0.2
    end: 1
    find_events:
        consecutive: true
    Epochs:
        detrend: 0
```

### Or in a Module

Pass function-specific parameters as separate kwargs:

```python
seg = Segmentation(
    raw=load.raw,
    stim_channel='STI 014',
    start=-0.2,
    end=0.5,
    find_events={'consecutive': true},
    Epochs={'preload': true}
)
```

Refer to each module's documentation to see which MNE functions it uses. For the complete list of available parameters for each MNE function, consult the [MNE documentation](https://mne.tools/stable/index.html), as BioPAP documentation does not show all possible MNE parameters.

!!! tip "Tips for Managing Configurations"

    - **Start with templates:** Use the provided example files as starting points rather than creating configurations from scratch.
    - **Copy from module documentation:** Each module's documentation includes an example YAML format with all possible settings. Copy this example and adjust the values to avoid syntax errors.
    - **Test before pipelines:** Run modules individually with your desired settings before adding them to a full pipeline.
