import argparse
import glob
from datetime import datetime
from pathlib import Path
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_SUBJECT_ID)
from biopap.modules.helpers import (get_pseudocoded_file_list,
                                    get_logger, read_config_file)
from biopap.modules.bids import BIDSConversion
from biopap.modules.plot import Plot
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.parallel_runner import ParallelRunner
from biopap.pipeline import Pipeline


logger = get_logger()

argp = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
argp.add_argument(
    "-i", "--input_dir", 
    type=Path,
    required=True,
    help="folder with input files to process",
)
argp.add_argument(
    "--extensions", 
    nargs="+",
    help="valid extensions for input files",
    default=[".bdf", ".edf", ".fif"]
)
argp.add_argument(
    "-o", "--output_dir",
    type=Path,
    required=False,
    help="Optional folder to write results to (overrides Plot, BIDS and SaveOutput settings in config file)",
)
argp.add_argument(
    "--do_not_share_dir",
    type=Path,
    required=True,
    default="./",
    help="Folder to save pseudocode lookup file in",
)
argp.add_argument(
    "-c", "--config_file",
    type=Path,
    required=True,
    help="path to YAML file containing pipeline configuration",
)
argp.add_argument(
    "--max_workers",
    type=int,
    help="defaults to max available workers; set to 1 for no parallelization",
)
argp.add_argument(
    "--mp_start_method",
    choices=["spawn", "fork"],
    default="spawn",
    help="multiprocessing start method",
)

args = argp.parse_args()

if not args.input_dir.exists() or not args.input_dir.is_dir():
    raise ValueError(f"'{args.input_dir}' doesn\'t exist or is not a directory")

if args.output_dir and args.output_dir.exists() and not args.input_dir.is_dir():
    raise ValueError(f"'{args.output_dir}' is not a directory")

valid_extensions = list(map(lambda x: f".{x.lower().lstrip('.')}", args.extensions))
logger.debug("Extension(s): %s" % valid_extensions)
input_files = [x for x in glob.glob(f"{args.input_dir}/*.*") if Path(x).suffix.lower() in valid_extensions]

if len(input_files)==0:
    logger.warning("No files found in %s" % args.input_dir)
    exit()

logger.info("Found %s files in '%s'" % (len(input_files), args.input_dir))

if args.output_dir:
    args.output_dir.mkdir(parents=True, exist_ok=True)

args.do_not_share_dir.mkdir(parents=True, exist_ok=True)

while True:
    run_start = datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S')
    pseudocode_file = args.do_not_share_dir / f'pseudocodes_{run_start}.txt'
    if not pseudocode_file.exists():
        break

config = read_config_file(args.config_file)

# overriding various output folders, checks etc
for step, step_cfg in config.items():

    if not CONFIG_MODULE_CLASS_KEY in step_cfg:
        raise ValueError("'%s' misses '%s' key; run 'tools/update_config.py' to update config file" % (step, CONFIG_MODULE_CLASS_KEY))

    s_mod = step_cfg[CONFIG_MODULE_CLASS_KEY]

    if s_mod == str(Plot) and args.output_dir:
        step_cfg['save_folder'] = args.output_dir / 'plots'

    elif s_mod == str(SaveOutput):
        
        if TPL_SUBJECT_ID not in step_cfg['output_file']:
            tmp = Path(step_cfg['output_file'])
            step_cfg['output_file'] = tmp.parent / f"{TPL_SUBJECT_ID}_{tmp.name}"

        if args.output_dir:
            step_cfg['output_file'] = args.output_dir / Path(step_cfg['output_file']).name

    elif s_mod == str(BIDSConversion) and args.output_dir:
        step_cfg['bids_root'] = args.output_dir / 'bids'
        Path(step_cfg['bids_root']).mkdir(parents=True, exist_ok=True)

    # checking eventifile's presence
    elif s_mod in [str(Segmentation), str(BIDSConversion)] \
        and 'eventsfile' in step_cfg and not Path(step_cfg['eventsfile']).exists():
        raise FileNotFoundError("%s: eventsfile '%s' not found" % (step, step_cfg['eventsfile']))

try:
    p = Pipeline.from_config(
        config=config,
        input_file=None,
        subject_id='test'
    ).check_steps()

except Exception as e:
    logger.critical("Pipeline steps check raised error: %s" % str(e))
    exit()

input_sets = get_pseudocoded_file_list(input_files)

para = ParallelRunner(
    input_sets=input_sets,
    output_dir=args.output_dir,
    config=config,
    max_workers=args.max_workers,
    mp_spawn_or_fork=args.mp_start_method,
)

f_sep = '\t'
v_sep = ';'
with open(pseudocode_file, 'w+') as f:
    f.write(f"{f_sep.join(['input_file', 'pseudocode', 'saved_files', 'exit_code'])}\n")
    for result in para.results:
        fields = [
            result['input_file'],
            result['pseudocode'],
            v_sep.join(map(str, result['saved_files'])),
            v_sep.join(map(str, result['exit_code']))]
        f.write(f"{f_sep.join(fields)}\n")

    logger.critical(f"Pseudcodes file: '{pseudocode_file}'. DO NOT SHARE FILE!")
