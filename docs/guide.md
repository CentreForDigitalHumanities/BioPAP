# User Guide

This guide is a general explanation on how the EEG preprocessing pipeline is structured and how it is typically used.

The pipeline provides a modular framework for processing EEG data. The preprocessing is constructed by combining individual processing steps, called modules, into a sequential pipeline.

It is recommended to develop and test pipelines interactively, and then run them in batch mode to process multiple datafiles.

## Pipeline Concept

The analysis pipeline consists of sequential **modules** applied to EEG data.

Each module performs a single processing step such as:

- filtering
- artifact rejection
- ICA decomposition
- epoching
- plotting

Modules are executed in the order they are added to the pipeline. The output of one module becomes the input for the next module.

A simple pipeline might look like:
```
Load Data
↓
Anonymize
↓
Filter
↓
ICA
↓
Epoching
```

This modular design makes it easy to:  
- experiment with different analysis strategies  
- modify processing steps  
- reuse pipelines across datasets  

---

## Pipeline Components

A pipeline consists of three main components.

**Modules**  
: Modules define the processing steps of the analysis pipeline. Each module performs a specific operation on the EEG data.

: Examples include filtering, artifact rejection, or epoch creation.

: The order in which modules are added determines the execution order of the pipeline.

**Configuration**  
: Every module has specific settings defined in a configuration file.

: Example configuration file:
    ```
    examples/data/pipeline.yaml.example
    ```

: Using configuration files allows pipelines to be easily reproduced and reused.

**Execution environment**  
: The pipeline can be executed in two different environments:

: - **Interactive mode** using a Jupyter notebook (`pipeline.ipynb`)
: - **Batch mode** using a Python script (`pipeline.py`)

: Both modes use the same modules and configuration files but serve different purposes during the analysis workflow.

---

## Interactive Mode (pipeline.ipynb)

Interactive mode is used when **developing or exploring a pipeline.**

In this mode, the pipeline is executed step by step and intermediate results can be inspected visually. Module settings from the configuration file can be overridden easily in the notebook to try different settings. 

Typical use cases:

- exploring available modules
- testing different configurations
- visually inspecting intermediate results 
- processing small datasets

Interactive execution makes it easy to quickly iterate on the settings and verify that each processing step behaves as expected.

For this reason, interactive mode is typically used during **pipeline development.**

---

## Batch Mode (pipeline.py)

Batch mode is designed for **automated processing of multiple EEG datafiles.**

The pipeline is executed without user interaction and all outputs are saved automatically.

Typical use cases:

- processing many participants
- running preprocessing pipeline on servers

Batch mode ensures that the same preprocessing pipeline is applied consistently across all datasets.

---

## Batch Mode with Visual Inspection (ICA)

Some modules require **manual inspection or adjustment.**

A common example is the **ICA module**, where users may need to manually identify and remove artifact-related components.

To support this, the pipeline can be executed in two stages.

**Step 1 – Run pipeline until ICA**

The pipeline processes the data up to the ICA step and saves the intermediate results to disk.

**Step 2 – Inspect ICA**

The user loads the saved data and inspects the ICA components to identify artifacts.

**Step 3 – Continue pipeline**

After the ICA components have been cleaned, the remaining pipeline steps can be executed in batch mode.

This approach allows pipelines to remain largely automated while still supporting necessary manual inspection steps.

---

## Pipeline Development Process

A typical process would look something like:

**1. Develop the pipeline in a notebook**

Use (a subset of) a single participant dataset, and:  
- explore modules  
- test configurations  
- interactively inspect outcomes of the steps  

**2. Finalize configuration**

Once the pipeline works, finalize:  
- define module execution order  
- add configuration parameters in the config file

**3. Create batch pipeline**

The finalized pipeline is defined in pipeline.py by adding the modules in the correct order.

This script will later be used to run the analysis on the full dataset.

**4. Run on full dataset**

Finally, the pipeline is executed in batch mode to process all participants.

The pipeline runs automatically and stores the resulting outputs for further analysis.