# Building the Pipeline

This tutorial explains how to set up and run a preprocessing pipeline for bioelectrical data. It guides you through loading data, configuring modules, and executing a complete pipeline. For details on configuration files, see the [configuration tutorial](configuration.md).

## Overview

A BioPAP pipeline typically follows these steps:

1. Load your data
2. Inspect the data and module outputs individually
3. Configure modules with appropriate parameters
4. Create a pipeline and add processing steps
5. Run the pipeline and access results

## Load the Data

The first step is to load your bioelectrical data into memory. Use the [LoadData()](../api/load_data.md) module, which currently supports BDF (BioSemi Data Format) files.

```python
# Read the data file and load it into memory
load = LoadData(file_path=data_file)
```

Once loaded, inspect the data properties to understand what you're working with:

```python
# Display basic information about the recording
load.raw.info

# Show detailed channel information
load.raw.describe()
```

For a visual inspection of the data, use the [Plot()](../api/plot.md) module. This opens an interactive window where you can navigate through the recording:

```python
# Visualize the raw data in an interactive plot
plt = Plot(raw=load.raw, title="Raw Data Inspection")
```

## Test and Configure Modules

Before adding modules to your pipeline, you can test them individually to ensure the configuration is correct. This allows you to inspect intermediate outputs and verify that each processing step works as expected.

### Running Modules Independently

When running modules individually, always specify the input data using the `raw` parameter:

```python
# Run the Anonymize module and inspect the output
ano = Anonymize(
    raw=load.raw,
    daysback=100,
    experimenter='J. Jansen',
    participant_id='AB00123'
)

# Check the output
ano.processed.info
```

The output of one module can be chained as input to another:

```python
# Run the Rereference module on the output of the Anonymize module
ref = Rereference(raw=ano.processed, ref_channels=['EXG1', 'EXG2'])

# Verify the result
ref.processed.info
```

### Overriding Configuration Parameters

When running modules individually, you can override the default configuration parameters. Any arguments passed to the module will override values from the configuration file:

```python
# Override configuration: custom downsampling rate
ds = Downsample(raw=ref.processed, sfreq=100)
```

For details on which arguments are required or optional for each module, see the [API documentation](../api/).

## Create the Pipeline

Once you've tested your modules and finalized your configurations, create a pipeline by instantiating the `Pipeline` class with your data and configuration file:

```python
# Create a new pipeline
pipe = Pipeline(data=load.raw, config_file=config_file)
```

View the pipeline's configuration settings:

```python
# Print all configuration parameters
from pprint import pprint
pprint(pipe.config)
```

Refer to the [configuration tutorial](configuration.md) for details on modifying these settings.

## Add Processing Steps

Add processing modules to the pipeline in the order you want them to execute. **Important:** Do not specify input data when adding steps to a pipeline—each step automatically receives the output of the previous step.

```python
# Add processing steps in the desired order
pipe.add_step(Anonymize)
pipe.add_step(Downsample)
pipe.add_step(IIRFilter)
pipe.add_step(Rereference)
pipe.add_step(ICA)
```

View all steps and their configurations:

```python
# Display an overview of all pipeline steps with their settings
print(*pipe.steps, sep='\n')
```

## Run the Pipeline

Execute the pipeline using the `run()` method:

```python
# Run the pipeline
pipe.run()
```

The pipeline processes the data sequentially through each step. After execution, access the final processed data via:

```python
# Access the processed output
processed_data = pipe.raw
```

To inspect and visualize the results:

```python
# Check the processed data info
pipe.raw.info

# Visualize the processed data
plot_result = Plot(raw=pipe.raw, title="Processed Data")
```

## Reset the Pipeline

To clear the pipeline and start over (useful for testing different configurations), use the `reset()` method:

```python
# Clear the pipeline
pipe.reset()
```

No arguments are required. This resets all processing steps while keeping the pipeline structure intact.

!!! tip "Tips and Best Practices"

    - **Test incrementally:** Run modules individually before adding them to the pipeline to catch configuration issues early.
    - **Visualize at key steps:** Use the Plot module to verify that each processing step produces expected results.
    - **Save configurations:** Store your final configuration parameters in the configuration file.

