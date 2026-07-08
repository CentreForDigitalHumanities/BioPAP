import argparse
import glob
import multiprocessing as mp
import os
import time
import warnings
from datetime import datetime
from pathlib import Path
from termcolor import colored
from biopap.modules import CONFIG_MODULE_CLASS_KEY 
from biopap.modules.helpers import (custom_formatwarning, generate_pseudonym_file_list,
                                    update_config_value, get_logger)
from biopap.modules.bids import BIDSConversion
from biopap.modules.plot import Plot
from biopap.modules.anonymize import Anonymize
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.pipeline import Pipeline


class ParallelRunner:
    def __init__(
        self,
        input_sets,
        output_dir,
        config,
        max_workers=None,
        mp_spawn_or_fork="spawn",
    ):

        logger.info(f"Processing {len(input_sets):,} file(s)")

        if max_workers:
            max_workers = min(max_workers, len(os.sched_getaffinity(0)))
            logger.info(f"Using {max_workers} worker(s)")

        if max_workers is None or max_workers > 1:
            with mp.get_context(mp_spawn_or_fork).Pool(
                processes=max_workers, maxtasksperchild=1
            ) as pool:
                for input_set in input_sets:
                    pool.apply_async(
                        self.runner,
                        args=({
                            "config": config,
                            "input_set": input_set,
                            "logger": logger
                        },),
                        callback=logger.info,
                    )

                pool.close()
                pool.join()

        elif max_workers == 1:
            for input_set in input_sets:
                logger.info(self.runner({
                    "config": config,
                    "input_set": input_set,
                    "logger": logger
                }))
        else:
            raise ValueError(f"No workers available ({max_workers}).")

    @staticmethod
    def runner(params):
        config = params["config"]
        input_set = params["input_set"]
        logger = params["logger"]

        def subst_pseudocode(old_path):
            new_path = str(old_path).replace('{subject_id}',input_set['pseudocode'])
            if str(old_path) == new_path:
                old = Path(old_path)
                new_path = old.parent / f"{old.stem}_{input_set['pseudocode']}{old.suffix}"
            return Path(new_path)

        for step in config:

            for item in [
                    (Anonymize, 'participant_id', input_set['pseudocode']),
                    (BIDSConversion, 'subject', input_set['pseudocode']),
                    (SaveOutput, 'output_file', subst_pseudocode)
                ]:

                new_val = update_config_value(
                    module=item[0], 
                    mod_config=config[step],
                    key=item[1],
                    new_value=item[2])

                if new_val:
                    logger.debug("%s: '%s' set to '%s'" % (step, item[1], new_val))

        Pipeline.from_config(
            config=config,
            input_file=input_set['input_file'],
            subject_id=input_set['pseudocode']
        ).run()

        return f"'{input_set['input_file']} [{input_set['pseudocode']}]' done"


if __name__ == "__main__":

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
        default=[".bdf", ".edf"]
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

    config = Pipeline.read_config_file(args.config_file)

    def update_path(string):
        return args.output_dir / Path(string).name

    if args.output_dir:
        for step in config:
            for item in [
                    (Plot, 'save_folder', args.output_dir),
                    (SaveOutput, 'output_file', update_path),
                    (BIDSConversion, 'bids_root', args.output_dir / 'bids')
                ]:

                new_val = update_config_value(
                    module=item[0], 
                    mod_config=config[step],
                    key=item[1],
                    new_value=item[2])

                if item[1] == 'bids_root' and new_val:
                    Path(new_val).mkdir(parents=True, exist_ok=True)

                if new_val:
                    logger.debug("%s: '%s' set to '%s'" % (step, item[1], new_val))

    for step in config:
        biopap_module = [v[CONFIG_MODULE_CLASS_KEY] for v in config[step] 
                        if next(iter(v)) == CONFIG_MODULE_CLASS_KEY]        
        if len(biopap_module) > 0 and biopap_module[0] in [str(Segmentation), str(BIDSConversion)]:
            eventsfile = [x for x in config[step] if 'eventsfile' in x]
            if len(eventsfile) > 0:
                eventsfile = Path(eventsfile[0]['eventsfile'])
                if not eventsfile.exists():
                    logger.critical("%s: 'eventsfile' '%s' not found" % (step, eventsfile))
                    exit()

    try:
        Pipeline.from_config(
            config=config,
            input_file=None,
            subject_id='test'
        ).check_steps()
    except Exception as e:
        logger.critical("Pipeline steps check raised error: %s" % str(e))
        exit()

    input_sets = generate_pseudonym_file_list(input_files)
    sep = ';'
    with open(pseudocode_file, 'w+') as f:
        f.write(f"pseudocode{sep}original_file\n")
        for file in input_sets:
            f.write(f"{file['pseudocode']}{sep}{file['input_file']}\n")
    
    logger.info(colored(f"Pseudcodes file: '{pseudocode_file}'. DO NOT SHARE FILE!", 'red', attrs=["bold"]))

    ParallelRunner(
        input_sets=input_sets,
        output_dir=args.output_dir,
        config=config,
        max_workers=args.max_workers,
        mp_spawn_or_fork=args.mp_start_method,
    )

    logger.info(colored(f"Pseudcodes file: '{pseudocode_file}'. DO NOT SHARE FILE!", 'red', attrs=["bold"]))
