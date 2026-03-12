# Building the pipeline

This tutorial explains how to set up a pipeline, it is based on parts of the jupyter notebook. 

## Load the data

Define the path to the data in my_config.ipynb. A detailed description on how to add and change the configurations can be found [here](configuration.md).

The data can be loaded with a module called [LoadData()](../api/load_data.md), which takes the path to the data file as input. It is currently designed to only read bdf files. 


```python
# Read the data file and load it into memory.
load = LoadData(file_path=data_file)
```

You can check the descriptives of the loaded data with the codes below.

```python
# Display basic info
load.raw.info

# Show channel info
load.raw.describe()
```

Maybe you also want to visually inspect the data. We use the [Plot()](../api/plot.md) module for this. An interactive window will open.

```python
# use the Plot-module to inspect the data
plt = Plot(raw=load.raw, title="Initial state")
```

## Inspect modules and tweek configurations

The notebook allows you to run modules separately and check the output (with .info or the Plot module). 

When running the modules outside of the pipeline you should always define the input data (raw=). So, in case you want to build onto the output of the previous step you have to define it.

```python
# run anoymize module and check the output 
ano = Anonymize(raw=load.raw, daysback=100, experimenter='J. Jansen', participant_id='AB00123')
ano.processed.info
```

In this example the output `ano.processed` of the Anonymized module can be the input of a different module. It is also possible to run the modules on load.raw. 

```python
# run rereference module on output of previous step
ref = Rereference(raw=ano.processed, ref_channels=['EXG1', 'EXG2'])
ref.processed.info
```

In the examples above you see multiple arguments given to the module. These are configurations of the modules, and specifying it like above means that you will overwrite the ones specified in the configuration file. The [configuration tutorial](configuration.md) will explain more about defining and using configurations. 

In the documentation about the modules you can see which arguments are required and which are optional.


## Create the pipeline

Once you know which modules and configurations you need for your preprocessing pipeline. You can create the pipeline. First, you need to set up a new pipeline, where you load in the data and the configurations for the config file. Go to the [tutorial about configurations](configuration.md) if you want to know how to adjust it. But for now you can continu with the default configuration.  

```python
# Create a new pipeline, loading the raw data and the configuration file.
pipe = Pipeline(data=load.raw, config_file=config_file)
```

The can see the default configurations with the code below.

```python
# Print the pipeline's config attribute to see the settings you loaded.
pprint(pipe.config)
```

## Add steps

Once you've created an empty pipeline, you can now add steps to the pipeline in the order that you want to run them. **Note** that you don't need to specify the input data, the output of the previous step will automatically be the input to the next. 

```python
# Add processing steps in the order they should be run.
pipe.add_step(Anonymize)
pipe.add_step(Downsample)
pipe.add_step(IIRFilter)
pipe.add_step(Plot)
```

You can show an overview of all the steps added to the pipeline with their configurations.

```python
# print pipeline overview, including each step's configuration settings
print(*pipe.steps, sep='\n')
```

## Run or reset

You can clear the pipeline with the reset() method. 

```python
# Call reset to clear the entire pipeline.
pipe.reset()
```

And run the pipeline with the run() method.

```python
# Call reset to clear the entire pipeline.
pipe.reset()
```

## Plotting

Do we explain something about plotting here? Interactive vs save? Or in the configuration tutorial?
