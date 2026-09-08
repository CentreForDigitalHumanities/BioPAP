import argparse
import glob
from pathlib import Path
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_SUBJECT_ID)
from biopap.modules.helpers import (get_logger, read_config_file)
from biopap.modules.bids import BIDSConversion
from biopap.modules.plot import Plot
from biopap.modules.pseudocodes import PseudoCodes
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.parallel_runner import ParallelRunner
from biopap.pipeline import Pipeline

# required for correct forking of child processes
if __name__ == "__main__":

    logger = get_logger()

    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument(
        "-c", "--config_file",
        type=Path,
        required=True,
        help="Path to YAML file containing pipeline configuration",
    )
    argp.add_argument(
        "-i", "--input", 
        type=Path,
        required=True,
        help="Path to file or folder with files to process",
    )
    argp.add_argument(
        "--extensions", 
        nargs="+",
        help="Valid extensions for input files",
        default=[".bdf", ".edf", ".fif"]
    )
    argp.add_argument(
        "-o", "--output_dir",
        type=Path,
        required=True,
        help="Folder to write results to (overrides output paths of Plot, BIDS and SaveOutput modules in config file)",
    )
    argp.add_argument(
        "--do_not_share_dir",
        type=Path,
        required=False,
        help="Folder to save pseudocode lookup file in (cannot be combined with --no_pseudo)",
    )
    argp.add_argument(
        "--no_pseudo",
        action='store_true',
        required=False,
        help="Do not create and apply pseudocodes (cannot be combined with --do_not_share_dir)",
    )
    argp.add_argument(
        "--max_workers",
        type=int,
        help="Maximun number of workers. Defaults to maximum available number. Set to 1 for no parallelization",
    )
    argp.add_argument(
        "--mp_start_method",
        choices=["spawn", "fork"],
        default="spawn",
        help="Multiprocessing start method",
    )

    args = argp.parse_args()

    if not args.input.exists():
        raise ValueError(f"'{args.input}' doesn\'t exist")

    if args.output_dir and args.output_dir.exists() and not args.output_dir.is_dir():
        raise ValueError(f"'{args.output_dir}' is not a directory")

    if args.no_pseudo and args.do_not_share_dir:
        raise ValueError("--do_not_share_dir and --no_pseudo cannot be combined")
    elif not args.no_pseudo and not args.do_not_share_dir:
        raise ValueError("Either --do_not_share_dir or --no_pseudo cannot is required")

    if args.do_not_share_dir and (not args.do_not_share_dir.exists() or not args.do_not_share_dir.is_dir()):
        raise ValueError(f"'{args.do_not_share_dir}' doesn\'t exist or is not a directory")

    valid_extensions = list(map(lambda x: f".{x.lower().lstrip('.')}", args.extensions))
    logger.debug("Extension(s): %s" % valid_extensions)

    if args.input.is_file():
        if not Path(args.input).suffix.lower() in valid_extensions:
            logger.warning("Unknown extension: '%s' (valid extensions: %s)" % (Path(args.input).suffix, ';'.join(valid_extensions)))
            exit()
        input_files = [str(args.input)]
    else:
        input_files = [x for x in glob.glob(f"{args.input}/*.*") if Path(x).suffix.lower() in valid_extensions]

        if len(input_files)==0:
            logger.warning("No files found in %s" % args.input)
            exit()

        logger.info("Found %s files in '%s'" % (len(input_files), args.input    ))

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.do_not_share_dir:
        args.do_not_share_dir.mkdir(parents=True, exist_ok=True)

    # read config and override various output folders, checks etc
    config = read_config_file(args.config_file)

    # overriding settings that are identical for all input files
    for step, step_cfg in config.items():

        # key 'Pipeline' allows for passing kwargs to embedded LoadData module
        if step == 'Pipeline':
            continue

        if not CONFIG_MODULE_CLASS_KEY in step_cfg:
            raise ValueError("'%s' misses '%s' key; run 'tools/update_config.py' to update config file" % (step, CONFIG_MODULE_CLASS_KEY))

        s_mod = step_cfg[CONFIG_MODULE_CLASS_KEY]

        if s_mod == str(Plot) and args.output_dir:
            step_cfg['save_folder'] = args.output_dir / 'plots'
            Path(step_cfg['save_folder']).mkdir(parents=True, exist_ok=True)

        elif s_mod == str(SaveOutput):
            tmp = Path(step_cfg['output_file'])
            if args.no_pseudo:
                step_cfg['output_file'] = tmp.parent / tmp.name
            elif TPL_SUBJECT_ID not in tmp.name:
                step_cfg['output_file'] = tmp.parent / f"{tmp.stem}_{TPL_SUBJECT_ID}{tmp.suffix}"

            if args.output_dir:
                step_cfg['output_file'] = args.output_dir / Path(step_cfg['output_file']).name

        elif s_mod == str(BIDSConversion) and args.output_dir:
            step_cfg['bids_root'] = args.output_dir / 'bids'
            Path(step_cfg['bids_root']).mkdir(parents=True, exist_ok=True)

        # checking eventfile's presence
        elif s_mod in [str(Segmentation), str(BIDSConversion)] \
            and 'eventsfile' in step_cfg and not Path(step_cfg['eventsfile']).exists():
            raise FileNotFoundError("%s: eventsfile '%s' not found" % (step, step_cfg['eventsfile']))

    # create "empty" new pipeline to check steps
    try:
        Pipeline.from_config(
            config=config,
            input_file=None,
            subject_id=None
        ).check_steps()

    except Exception as e:
        logger.critical("Pipeline steps check raised error: %s" % str(e))
        exit()

    # create sets of input files + pseudocode
    if args.no_pseudo:
        input_sets = [{'input_file': x, 'pseudocode': None} for x in input_files]
    else:
        pseudo = PseudoCodes()
        input_sets = pseudo.get_pseudocoded_file_list(files=input_files)

    # launch runner
    para = ParallelRunner(
        input_sets=input_sets,
        output_dir=args.output_dir,
        config=config,
        max_workers=args.max_workers,
        mp_spawn_or_fork=args.mp_start_method,
    )

    if not args.no_pseudo:
        new_pseudocode_file = pseudo.get_pseudocodes_filepath(
            do_not_share_dir=args.do_not_share_dir,
            suffix=f"--{Path(args.config_file).stem}")
        pseudo.write_pseudocode_file(results=para.results, file=new_pseudocode_file)
        logger.critical(f"Pseudocodes file: '{new_pseudocode_file}'. DO NOT SHARE FILE!")
