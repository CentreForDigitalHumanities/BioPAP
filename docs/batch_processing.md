# Batch processing

`run_pipeline.py` allows you to run multiple pipelines in parallel. The program will divide 
files in an input folder among the available workers (cores) and process them in parallel. The 
process also takes care of the pseudonomisation of the output files.

## Usage

```bash
usage: run_pipeline.py [-h] -c CONFIG_FILE -i INPUT_DIR
                       [--extensions EXTENSIONS [EXTENSIONS ...]] [-o OUTPUT_DIR]
                       --do_not_share_dir DO_NOT_SHARE_DIR
                       [--pseudocode_file PSEUDOCODE_FILE]
                       [--max_workers MAX_WORKERS] [--mp_start_method {spawn,fork}]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Path to YAML file containing pipeline configuration (default:
                        None)
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Folder with input files to process (default: None)
  --extensions EXTENSIONS [EXTENSIONS ...]
                        Valid extensions for input files (default: ['.bdf', '.edf',
                        '.fif'])
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Optional folder to write results to (overrides output paths
                        of Plot, BIDS and SaveOutput modules in config file)
                        (default: None)
  --do_not_share_dir DO_NOT_SHARE_DIR
                        Folder to save pseudocode lookup file in (default: ./)
  --pseudocode_file PSEUDOCODE_FILE
                        Path to file containing pseudocodes and output from previous
                        run (default: None)
  --max_workers MAX_WORKERS
                        Maximun number of workers. Defaults to maximum available
                        number. Set to 1 for no parallelization (default: None)
  --mp_start_method {spawn,fork}
                        Multiprocessing start method (default: spawn)


```

For relevant modules, a save path is included in their configuration, listed in the config file.
When running the pipeline in parallel, you can override the save paths by setting `output_dir`,
allowing you to easily manage the general output location without having to edit the configuration.
For instance, when you run a multi-part pipeline, the `output_dir` set in the run for the first part
can then become the `input_dir` of the second part, without having to manually move files around.

Before running the actual pipeline, a four-letter pseudocode is created for each input file. The
anonymization module uses the pseudocode to overwrite the user ID in the 'subject_info' field of
the input's metadata. The pseudocode is also prepended to the file names of all files the pipeline
outputs (save, plot and BIDS modules). A file listing input files and corresponding pseudocodes
and output files is written to the `do_not_share_dir` folder. As the name implies, the contents
in this folder should never be shared when sharing the pipeline's output.

When you run a multi-part pipeline - for instance when the complete process includes a module that
requires user interaction - the pipeline can re-use the generated pseudocodes from the first step
by adding the generated file with pseudocodes as values for the `pseudocode_file` parameter for the
next step (the full path of the pseudocode file is printed to the screen at the end of each run).

If you want to run your pipeline over each file sequentially, rather than in parallel,
simply call `run_pipeline.py` with `max_workers` set to 1.


## Process flow

In a single process, the program:
 
+ Reads in a list of files in `INPUT_DIR` matching `EXTENSIONS`
+ Reads config from `CONFIG_FILE`
+ If user specified `OUTPUT_DIR`, program overrides relevant paths in the configuration with `OUTPUT_DIR`:
    + `Plot`-module: `save_folder` is set to `OUTPUT_DIR`
    + `SaveOutput`-module: folder part of `output_file` is set to `OUTPUT_DIR`
    + `BIDSConversion`-module: `bids_root` is set to  `OUTPUT_DIR / 'bids'`
+ Tests, if `Segmentation` or `BIDSConversion` are present in the pipeline and contain an eventsfile in the config,
  whether the specified file actually exists (halts if not)
+ Tests if the config is valid (halts if not)
+ Creates a pseudocode per input file (string of four random uppercase characters). <u>Pseudocodes are unique within one run, but not across runs</u>.
+ Saves input file/pseudocode relations to `DO_NOT_SHARE_DIR / 'pseudocodes_<timestamp>.txt'`

The program then launches a pool of `MAX_WORKERS` workers, dividing the input files among them. Each process:

+ Where relevant, overrides config settings with the pseudocode:
    + `Anonymize`-module: `participant_id`
    + `BIDSConversion`-module: `subject`
    + `SaveOutput`-module: `output_file` (if the config value contains the substring `{subject_id}`, that is replaced with the pseudocode; if not, the pseudocode is appended to the filename)
+ Creates a pipeline from the configuration and runs it.


## Log settings

Log level can be set to DEBUG (default is INFO) through the environment variable `BIOPAP_DEBUG`.
By default, the program only logs to the terminal. In order to save log information, a logfile
can be set through the environment variable `BIOPAP_LOGFILE`:

```bash
export BIOPAP_DEBUG=1
export BIOPAP_LOGFILE=/biopap/logs/my_logfile.txt

# or when executing:

$ BIOPAP_LOGFILE=/log/biopap.log BIOPAP_DEBUG=1 python parallel_runner.py \
    -i /biopap/data \
    -o /biopap/out \
    -c '/biopap/config/my_config.yaml' \
    --max_workers 4
```

Please be aware that when running in parallel, error messages can remain invisible, causing the program to fail without apparent reason. If this happens, run the same command with a single worker (`--max_workers 1`) to catch the error.