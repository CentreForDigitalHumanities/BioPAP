# BioPAP module development guide

A BioPAP analysis pipeline consists of preprocessing modules. Each module performs a single processing step, which at its heart calls one (incidentally more) function of the [MNE package](https://mne.tools/). In the pipeline, each module is applied sequentially to EEG data. The output of one module becomes the input for the next module. If required, a module can contain additional logic, as long as the paradigm:

_Module A.processed output &rarr; Module B.raw input_

remains intact, so it can be used in a BioPAP pipeline. Beyond that, basically anything is allowed if it fits the module design outlined below. In theory a module could also use a different library for its processing, but all current modules wrap functions from MNE.


## Module outline

A BioPAP module is a Python class wrapping an [MNE](https://mne.tools/stable/index.html)-function. It is designed to have a standardized interface, which makes it possible to chain multiple modules together in a pipeline. 

### Input and output data

Generally speaking, a BioPAP module loads data, which is assigned to the class attribute `raw`, performs some form of processing, and makes the processed data available as the attribute `processed`. When chained together in a pipeline, the output data of one module becomes the input data of the next one. This means that each module requires input data when its class is instantiated (each class' `__init()__` function accepts a mandatory `raw` parameter), and requires to assign its output to the `processed` attribute.

The exception to this is the [LoadData](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/load_data.py) module, which has no input, and therefore no `raw` attribute. There are other modules that don't do any actual processing, such as [SaveOutput](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/save_output.py), [Metadata](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/metadata.py) and [Plot](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/plot.py), but in order to be able to make them part of a pipeline, in which each next module expects to read its data from the previous one through the `processed` attribute, these classes simply copy `raw` to `processed` without any processing.

### MNE-functions

BioPAP modules are wrappers around MNE functions. Usually, a single module applies a single MNE function to its input data. For instance, the [BaselineCorrection](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/baseline_correction.py) module calls [mne.Epochs.apply_baseline](https://mne.tools/stable/generated/mne.Epochs.html#mne.Epochs.apply_baseline).

Occasionally, a module calls more than one MNE function. For instance, the [BIDSConversion module](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/bids.py), which first calls [mne_bids.BIDSPath](https://mne.tools/mne-bids/stable/generated/mne_bids.BIDSPath.html#mne_bids.BIDSPath) to create the path of the BIDS file, followed by [mne_bids.write_raw_bids](https://mne.tools/mne-bids/stable/generated/mne_bids.write_raw_bids.html#mne_bids.write_raw_bids) to write the actual BIDS-file. 

In other cases, a single module calls a different MNE-function, depending on the value of a parameter or some variable. For instance, based on the file extension of the file to be loaded, [LoadData](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/load_data.py) calls either [read_raw_bdf](https://mne.tools/stable/generated/mne.io.read_raw_bdf.html), [read_raw_edf](https://mne.tools/stable/generated/mne.io.read_raw_edf.html), or [read_raw_fif](https://mne.tools/stable/generated/mne.io.read_raw_fif.html). Furthermore, in the case of .FIF files, which can hold either raw or epoched data, the module first tries calling [read_epochs](https://mne.tools/stable/generated/mne.read_epochs.html) on the file, only to falls back to read_raw_fif when that fails.


### Parameters

Each BioPAP module accepts a set of standard parameters to be passed on to the underlying MNE-function. However, nearly all MNE functions accept more parameters (sometimes many more) than declared in the BioPAP module's `__init()__` method. For clarity, only the most important parameters have been included as standard parameters; however, additional parameters can always be passed on to the underlying MNE-function through the `**kwargs` parameter.

Values for parameters are passed on to the module at run time:

```python
load = LoadData(file_path='/data/my_eeg_data.bdf')

ref = Rereference(
    raw=load.processed,
    ref_channels=['EXG1', 'EXG2'],
    ch_type='eeg')
```

Note that `ch_type` is not part of [Rereference](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/rereference.py)'s initial parameters, and will be passed on to the [set_eeg_reference](https://mne.tools/stable/generated/mne.set_eeg_reference.html#mne.set_eeg_reference). This happens  _as is_, and it is left to the MNE-function to validate the parameter and its value. If you pass on something that is not recognized or has an invalid value, it will trigger an error from the MNE-function.

When one BioPAP module wraps multiple MNE-functions, it looks for specific keys in `**kwargs`, corresponding to specific MNE-functions. The actual variables to be passed on should be provided as a dictionary holding the keys and values. For instance, the [Segmentation](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/segmentation.py) module uses MNE's [find_events](https://mne.tools/stable/generated/mne.find_events.html) and [pick_events](https://mne.tools/stable/generated/mne.pick_events.html) functions, both of which accept additional parameters. In order to pass extra parameters for either one, or both, the module looks in the `**kwargs` for the keys `find_events` and `Epochs`:

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
Subsequently, `{'consecutive': true}` will be passed on as extra parameter to `find_events()`, and `{'preload': true}` to `pick_events()`. The manual [modules section of the manual](https://centrefordigitalhumanities.github.io/BioPAP/api/) lists the correct keys for passing on extra parameters.


## Module classes

### BaseClass

Each BioPAP module is a Pythin class derived from the [BaseClass](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/base_class.py). BaseClass handles saving a module's configuration to file, and exposes the `raw` and `processed` attributes. 

BaseClass contains a number of constants that can be overridden in inherited classes:

**log_config**  (default True): whether the class should produce log output. Should be set to False if sensitive information might be logged. Be aware that the logger not just records what is explicitly logged (through `logger.info()` etc.), but also, if `silent` is False (which is the default), records any output written by NME-functions to stdout. The [Anonymize](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/anonymize.py) module, for instance, sets `log_config` to False.

**halt_on_exceptions** (default True): whether a module should cause a pipeline it is part of to stop processing when an exception occurs in the module. This usually makes sense, because an exception probably means something went wrong during processing, making it pointless to continue with the next module. An exception is the [Plot](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/plot.py) module, which does not do perform any processing.

**alters_data** (default True): indicates whether a module is designed to alter the raw data it is handed (*not* whether it has actually done so at run time). Used by [Pipeline](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/pipeline.py) when checking a pipeline's integrity.

**standalone_module** (default True): indicates if a class is an actual BioPAP module. Required to separate modules from helper classes that reside in the same folder (such as [PipelineStep](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/src/biopap/modules/pipeline_step.py)).



## TBD

+ make a complete template for an empty module
+ "copy one and modify"
+ naming conventions
+ include ref to a new class in:
    + Git module folder
    + Pipeline class
    + update_config.py
+ __init__
    + CONFIG_MODULE_CLASS_KEY = '_biopap_module'
    + CONFIG_MODULE_ORDER_KEY = '_order'
    + TPL_SUBJECT_ID = '{subject_id}'
    + TPL_FILENAME = '{filename}'
+ how does config work, and what is altered by Pipeline and why
+ documentation
    + how does it work
    + doc string & relation with documentation
    + what to include manually
+ what goes into helpers
+ Git locations
+ A word about pseudocodes
+ A word about paralllism: embarrasingly
    + if paths need to change, run_pipeline.py has to change
+ A word about interactivity
+ PR's
+ tests...
+ what to do when updating an existing class?
    + think about versioning (and make an issue out of it)
    + for now, just call it ClassName2?