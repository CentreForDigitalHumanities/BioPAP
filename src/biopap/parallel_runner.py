import argparse
import glob
import multiprocessing as mp
import os
import re
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Union, Optional
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_SUBJECT_ID)
from biopap.modules.helpers import (custom_formatwarning, generate_pseudonym_file_list,
                                    get_logger, read_config_file)
from biopap.modules.bids import BIDSConversion
from biopap.modules.plot import Plot
from biopap.modules.anonymize import Anonymize
from biopap.modules.pipeline_step import PipelineStep
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

        self._results = []

        def handle_result(result):
            self._results.append(result)
            if result['exit_code'][0] == 0:
                logger.info(f"'{result['input_file']}' done [{result['pseudocode']}]")
            else:
                logger.error(f"'{result['input_file']}' raised error: {result['exit_code'][1]} [{result['pseudocode']}]")

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
                            "config": dict(config),
                            "input_set": input_set,
                            "logger": logger
                        },),
                        callback=handle_result,
                        # callback=logger.info,
                    )

                pool.close()
                pool.join()

        elif max_workers == 1:
            for input_set in input_sets:
                handle_result(self.runner({
                    "config": dict(config),
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

        for step, step_cfg in config.items():
            if step_cfg[CONFIG_MODULE_CLASS_KEY] == str(Anonymize):
                step_cfg['participant_id'] = input_set['pseudocode']
            elif step_cfg[CONFIG_MODULE_CLASS_KEY] == str(BIDSConversion):
                step_cfg['subject'] = input_set['pseudocode']

        try:
            pipe = Pipeline.from_config(
                config=config,
                input_file=input_set['input_file'],
                subject_id=input_set['pseudocode']
            )
            pipe.run()
            exit_code = (0, 'success')
        except Exception as e:
            exit_code = (1, str(e))

        return {
            'input_file': input_set['input_file'],
            'pseudocode': input_set['pseudocode'],
            'saved_files': pipe.saved_files,
            'exit_code': exit_code
        }

    @property
    def results(self):
        # [{input_file, pseudocode, saved_files, exit_code}]
        return self._results


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
