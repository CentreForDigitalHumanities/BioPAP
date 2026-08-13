import argparse
import glob
from pathlib import Path
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_SUBJECT_ID)
from biopap.modules.helpers import (get_logger, read_config_file)
from biopap.modules.anonymize import Anonymize
from biopap.modules.bids import BIDSConversion
from biopap.modules.plot import Plot
from biopap.modules.pseudocodes import PseudoCodes
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.pipeline import Pipeline

logger = get_logger()

argp = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
argp.add_argument(
    "-c", "--config_file",
    type=Path,
    required=True,
    help="path to YAML file containing pipeline configuration",
)
argp.add_argument(
    "-f", "--input_file",
    type=Path,
    required=True,
    help="path to file to process",
)
argp.add_argument(
    "--do_not_share_dir",
    type=Path,
    required=True,
    default="./",
    help="optional folder to save pseudocode lookup file in",
)
argp.add_argument(
    "--pseudocode_file",
    type=Path,
    required=False,
    help="path to file containing pseudocodes and output from previous run",
)

args = argp.parse_args()

if not args.input_file.exists() or not args.input_file.is_file():
    raise ValueError(f"'{args.input_file}' doesn\'t exist or is not a file")

if not args.do_not_share_dir.exists() or not args.do_not_share_dir.is_dir():
    raise ValueError(f"'{args.do_not_share_dir}' doesn\'t exist or is not a directory")

args.do_not_share_dir.mkdir(parents=True, exist_ok=True)

# read config and override various output folders, checks etc
config = read_config_file(args.config_file)

pseudo = PseudoCodes()

input_set = pseudo.get_pseudocoded_file_list(
    files=[args.input_file],
    filecode_list=pseudo.read_pseudocoded_file_list(file=args.pseudocode_file))[0]

for step, step_cfg in config.items():

    if not CONFIG_MODULE_CLASS_KEY in step_cfg:
        raise ValueError("'%s' misses '%s' key; run 'tools/update_config.py' to update config file" % (step, CONFIG_MODULE_CLASS_KEY))

    # checking eventfile's presence
    if step_cfg[CONFIG_MODULE_CLASS_KEY] in [str(Segmentation), str(BIDSConversion)] \
        and 'eventsfile' in step_cfg and not Path(step_cfg['eventsfile']).exists():
        raise FileNotFoundError("%s: eventsfile '%s' not found" % (step, step_cfg['eventsfile']))

    if step_cfg[CONFIG_MODULE_CLASS_KEY] == str(Anonymize):
        step_cfg['participant_id'] = input_set['pseudocode']

    elif step_cfg[CONFIG_MODULE_CLASS_KEY] == str(BIDSConversion):
        step_cfg['subject'] = input_set['pseudocode']

    elif step_cfg[CONFIG_MODULE_CLASS_KEY] == str(SaveOutput) and TPL_SUBJECT_ID not in step_cfg['output_file']:
        tmp = Path(step_cfg['output_file'])
        step_cfg['output_file'] = tmp.parent / f"{TPL_SUBJECT_ID}_{tmp.name}"

try:
    Pipeline.from_config(
        config=config,
        input_file=None,
        subject_id='test'
    ).check_steps()

except Exception as e:
    logger.critical("Pipeline steps check raised error: %s" % str(e))
    exit()

try:
    pipe = Pipeline.from_config(
        config=config,
        input_file=input_set['input_file'],
        subject_id=input_set['pseudocode']
    )
    pipe.run()
    saved_files = pipe.saved_files
    exit_code = (0, 'success')

except Exception as e:
    logger.critical(str(e))
    saved_files = []
    exit_code = (1, str(e))

result = {
    'input_file': str(input_set['input_file']),
    'pseudocode': input_set['pseudocode'],
    'saved_files': saved_files,
    'exit_code': exit_code
}

new_pseudocode_file = pseudo.get_pseudocode_filename(
    do_not_share_dir=args.do_not_share_dir,
    suffix=f"--{Path(args.config_file).stem}")
pseudo.write_pseudocode_file(results=[result], file=new_pseudocode_file)
logger.critical(f"Pseudcodes file: '{new_pseudocode_file}'. DO NOT SHARE FILE!")
