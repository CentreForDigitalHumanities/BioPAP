# Batch processing

`run_pipeline.py` allows you to run multiple pipelines in parallel. The program will divide 
files in an input folder among the available workers (cores) and process them in parallel. The 
process also takes care of the pseudonomisation of the output files.

## Usage

```bash
usage: run_pipeline.py [-h] -c CONFIG_FILE -i INPUT
                       [--extensions EXTENSIONS [EXTENSIONS ...]] -o OUTPUT_DIR
                       [--do_not_share_dir DO_NOT_SHARE_DIR] [--no_pseudo]
                       [--max_workers MAX_WORKERS] [--mp_start_method {spawn,fork}]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Path to YAML file containing pipeline configuration (default: None)
  -i INPUT, --input INPUT
                        Path to file or folder with files to process (default: None)
  --extensions EXTENSIONS [EXTENSIONS ...]
                        Valid extensions for input files (default: ['.bdf', '.edf',
                        '.fif'])
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Folder to write results to (overrides output paths of Plot, BIDS
                        and SaveOutput modules in config file) (default: None)
  --do_not_share_dir DO_NOT_SHARE_DIR
                        Folder to save pseudocode lookup file in (cannot be combined with
                        --no_pseudo) (default: None)
  --no_pseudo           Do not create and apply pseudocodes (cannot be combined with
                        --do_not_share_dir) (default: False)
  --max_workers MAX_WORKERS
                        Maximun number of workers. Defaults to maximum available number.
                        Set to 1 for no parallelization (default: None)
  --mp_start_method {spawn,fork}
                        Multiprocessing start method (default: spawn)

```

For relevant modules, a save path is included in their configuration, listed in the config file.
When running the pipeline in parallel, you can override the folder of these save paths by
setting `output_dir`, allowing you to easily manage the general output location without having to
edit the configuration. For instance, when you run a multi-part pipeline, the `output_dir` set in
the run for the first part can then become the `input_dir` of the second part, without having to
manually move files around.

Before running the actual pipeline, a four-letter pseudocode is created for each input file. The
anonymization module uses the pseudocode to overwrite the user ID in the 'subject_info' field of
the input's metadata. The pseudocode is also prepended to the file names of all files the pipeline
outputs (save, plot and BIDS modules). A file listing input files and corresponding pseudocodes
and output files is written to the `do_not_share_dir` folder. As the name implies, the contents
in this folder should never be shared when sharing the pipeline's output.

When you run a multi-part pipeline - for instance when the complete process includes a module that
requires user interaction - the pipeline automatically re-uses the generated pseudocodes from the
first step by re-using the first four characters from the input filenames as pseudocodes for the
next step (provided they match the pseudocode pattern, i.e. four capital letters followed by an
underscores)

If you do not need pseudonymization, start the program with the argument `--no_pseudo`.

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
  whether the specified events file actually exists (halts if not)
+ Tests if the config is valid (halts if not)
+ When pseudonymizing
    + Assigns a pseudocode to each input file:
        + If the last section of the stem of an input file's  name matches the right pattern (underscore plus four uppercase letters) it re-uses that pseudocode (`input_file_ABCD.bdf` &rarr;  pseudocode `ABCD`).
        + If not, a new pseudocode is created, and appended to all output files.
    + Saves input file/pseudocode relations to `DO_NOT_SHARE_DIR / 'pseudocodes_<timestamp>.txt'`

The program then launches a pool of `MAX_WORKERS` workers, dividing the input files among them. Each process:

+ Where relevant, overrides config settings:
    + `Anonymize`-module: `participant_id` replaced by pseudocode.
    + `BIDSConversion`-module: `subject` replaced by pseudocode.
    + `SaveOutput`-module, setting `output_file`:
        + if the value contains the substring `{subject_id}`, it is replaced with the pseudocode; if not, the pseudocode is appended to the filename.
        + if it contains the substring `{filename}`, it will be replaced with the name of the input file.
+ Creates a pipeline from the configuration and runs it.


## Running a multi-part pipeline: example

Suppose you have a pipeline in three parts, because there are intermediate steps between part one and two, and again
between part two and three, that are interactive. First, create separate configuration-files for each part of the pipeline.
Make sure each part ends with a SaveModule. If you have previously designed you pipeline as one complete configuration-file,
you can just split that file into three separate files, and add a SaveModule as extra step to the first and second part.
In the examples below, the configuration files are named `/pipeline/cfg/part1.yaml` and `.../part2.yaml`, respectively.

Next, make sure you collect the input files into one folder (you can also start `run_pipeline.py` with the path of a
single file as input, but this example assumes you are preparing to process an entire batch). In the example below, this
is the folder `/pipeline/input`. Next, specify a general output folder (`/pipeline/output_1`) for the pipeline to write its
output to. This path takes precedent over any output folders configured for individual modules in your configuration-files,
and makes it easier to pass along the output of the first part of the pipeline as input to the next part. Finally, create a 
folder to save the pseudocode-file to `/pipeline/do_not_share/`, and run the first part of the pipeline thus:


```bash
python ./run_pipeline.py \
    -c '/pipeline/cfg/part1.yaml'  \
    -i '/pipeline/input' \
    -o '/pipeline/output_1' \
    --do_not_share_dir '/pipeline/do_not_share/'
```

Once done, the (partially) processed files are in the output folder, and there is a file with filepaths and corresponding
pseudocodes in the `do_not_share_dir` folder. The file's complete path is printed to the terminal as the very last log line.
The file is named using the datetimestamp of the moment of its creation, plus the filename of the config-file used for
running the pipeline: `pseudocodes_<date YYYYMMDD>-<time HHMMSS>--<config file's name>.tsv'`.

The contents of the file look something like this:

```csv
input_file                        pseudocode  saved_files                         exit_code
/pipeline/input/CBN1BD071212.bdf  XKVG        /pipeline/output_1/XKVG_part1.fif   0;success
/pipeline/input/CBN1BD023561.bdf  NHSE        /pipeline/output_1/NHSE_part1.fif   0;success

```

After having done any intermediate processing, either return the files to the `/pipeline/output_1` folder for the next part, or
create a new folder and put them there - as long as the pseudocodes at the start of the filenames remain unchanged (`XKVG_`,
`NHSE_`). In the next step, rather than creating  new pseudocodes, the pipeline will deduce the previously generated pseudocodes
from input files' names.

For example, the next step below uses `/pipeline/output_1` as its new input folder, and `/pipeline/output_2` as new output folder.
The program will read all the files in the folder `/pipeline/output_1`, and try to deduce the pseudocodes from the filenames. For
instance, if it finds the file `NHSE_part1.fif` in the new input folder, it will (again) use `NHSE` as the pseudocode for the
second pipeline.

```bash
python ./run_pipeline.py \
    -c '/pipeline/cfg/part2.yaml'  \
    -i '/pipeline/output_1' \
    -o '/pipeline/output_2' \
    --do_not_share_dir '/pipeline/do_not_share/'
```

This step will write its output to `/pipeline/output_2`, and once it's done, will write its own pseudocode-file
to `do_not_share_dir`.


## Log settings

Log level can be set to DEBUG (default is INFO) through the environment variable `BIOPAP_DEBUG`.
By default, the program only logs to the terminal. In order to save log information, a logfile
can be set through the environment variable `BIOPAP_LOGFILE`:

```bash
export BIOPAP_DEBUG=1
export BIOPAP_LOGFILE=/biopap/logs/my_logfile.txt

# or when executing:

$ BIOPAP_LOGFILE=/log/biopap.log BIOPAP_DEBUG=1 python run_pipeline.py \
    -i /biopap/data \
    -o /biopap/out \
    -c '/biopap/config/my_config.yaml' \
    --max_workers 4
```

Please be aware that when running in parallel, error messages can remain invisible, causing the program to fail without apparent reason. If this happens, run the same command with a single worker (`--max_workers 1`) to catch the error.