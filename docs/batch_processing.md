# Batch processing

`parallel_runner.py` allows you to run multiple pipelines in parallel. The program will divide 
files in an input folder among the available workers (cores) and process them in parallel.

## Usage

```bash
usage: parallel_runner.py [-h] -i INPUT_DIR
                          [--extensions EXTENSIONS [EXTENSIONS ...]]
                          [-o OUTPUT_DIR] --do_not_share_dir
                          DO_NOT_SHARE_DIR -c CONFIG_FILE
                          [--max_workers MAX_WORKERS]
                          [--mp_start_method {spawn,fork}]

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        folder with input files to process
                        (default: None)
  --extensions EXTENSIONS [EXTENSIONS ...]
                        valid extensions for input files (default:
                        ['.bdf', '.edf'])
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Optional folder to write results to
                        (overrides Plot, BIDS and SaveOutput
                        settings in config file) (default: None)
  --do_not_share_dir DO_NOT_SHARE_DIR
                        Folder to save pseudocode lookup file in
                        (default: ./)
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        path to YAML file containing pipeline
                        configuration (default: None)
  --max_workers MAX_WORKERS
                        defaults to max available workers; set to
                        1 for no parallelization (default: None)
  --mp_start_method {spawn,fork}
                        multiprocessing start method (default:
                        spawn)


```

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