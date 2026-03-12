# Configuration

## Configuration files

There are two configuration files:


#### example.my_config.ipynb

: This file serves as a template. To avoid issues with local settings and GitHub updates, create a small notebook called `my_config.ipynb` and update the paths to the data file and module configuration file. 

#### pipeline.yaml.example

: This file also serves as a template with some example module settings. Please create a file called `pipeline.yaml`, and use the newly created file to store the settings for the modules that you'll use in your pipeline. 

Configuration files that you just created will be loaded into the notebook with the following code.

```python
config_notebook = './my_config.ipynb'

if Path(config_notebook).exists():
    %run {config_notebook}
else:
    data_file = '/biopap/data/example.bdf'
    config_file = './data/pipeline.yaml'

if not Path(config_file).exists:
    print(f"Config file {config_file} does not exist.")

if not Path(data_file).exists:
    print(f"Data file {data_file} does not exist.")
```
!!! info 

    This code is already in the notebook.

## Overwrite configs

The initial configurations for the modules are defined in the modules configuration file (pipeline.yaml), also mentioned as the configuration file. 

If you're just trying out the modules with different settings and you don't want to update the configuration file everytime. You can overwrite the configurations.

One way of overwriting - when running modules separately - can be done like this. 

```python
# Settings from the config file can be overridden (defaults; l_freq=0.1 and h_freq=35)
# run IIRFilter with l_freq=0.2 and h_freq=50
flt = IIRFilter(
    raw=load.raw,
    l_freq=0.2,
    h_freq=50)
```

When you have the modules in a pipeline already and you use pipe.add_step(_module_). The configuration from the config file can be overridden by changing the configs when adding the step to the pipeline, like this.

```python
pipe.add_step(IIRFilter, cfg={'l_freq': 0.2, 'h_freq': 50})
```

## Configurations of the modules

Can be found in the modules. The file is in yaml format. Some module settings expect a dictionary or a list. All of this information can be found in the documentation of the module. You can also see an example of the setting which you can copy paste and adjust. This is to make sure the correct layout will be added to the yaml, in order for the module to run.

```yaml
# Example config file
Anonymize:
    daysback: 100
    experimenter: 'J. Jansen'
    participant_id: 'AB00123'

Rereference:
    ref_channels: ['EXG1', 'EXG2']

EOGChannels:
    ref_channels: ['hEOG', 'vEOG']
    anode_channels: ['EXG3','EXG5']
    cathode_channels: ['EXG4','EXG6']

IIRFilter:
    l_freq: 0.1
    h_freq: 35

```

## Add additional configs from MNE functions

Explain **kwargs here. 

```yaml
Show example how it is used in yaml file
```