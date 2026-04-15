import argparse
# import gc
import glob
import logging
import multiprocessing as mp
import os
import time
import warnings
from pathlib import Path
from biopap.modules.helpers import custom_formatwarning
from biopap.pipeline import Pipeline

log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logging.captureWarnings(True)
warnings.formatwarning = custom_formatwarning
logger = logging.getLogger(__name__)


class ParallelRunner:
    def __init__(
        self,
        input_files,
        output_dir,
        stored_pipeline,
        max_workers=None,
        mp_spawn_or_fork="spawn",
    ):

        logger.info(f"Processing {len(input_files):,} houses")

        if max_workers:
            max_workers = min(max_workers, len(os.sched_getaffinity(0)))
            logger.info(f"Using {max_workers} worker(s)")

        if max_workers is None or max_workers > 1:
            with mp.get_context(mp_spawn_or_fork).Pool(
                processes=max_workers, maxtasksperchild=1
            ) as pool:
                for input_file in input_files:
                    pool.apply_async(
                        self.runner,
                        args=({
                            "stored_pipeline": stored_pipeline,
                            "input_file": input_file,
                            "output_dir": output_dir,
                            "logger": logger
                        },),
                        callback=logger.info,
                    )

                pool.close()
                pool.join()

        elif max_workers == 1:
            for input_file in input_files:
                logger.info(self.runner({
                    "stored_pipeline": stored_pipeline,
                    "input_file": input_file,
                    "output_dir": output_dir
                }))
        else:
            raise ValueError(f"No workers available ({max_workers}).")

    @staticmethod
    def runner(params):
        stored_pipeline = params["stored_pipeline"]
        input_file = params["input_file"]
        output_dir = params["output_dir"]
        logger = params["logger"]
        
        Pipeline.from_file(
            save_path=stored_pipeline,
            input_file=input_file
        ).run()

        return f"'{input_file}' done"


if __name__ == "__main__":

    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument(
        "-i", "--input_dir", 
        type=Path,
        required=True,
        help="folder with files to process",
    )
    argp.add_argument(
        "-o", "--output_dir",
        type=Path,
        required=True,
        help="fodler to write results to",
    )
    argp.add_argument(
        "-s", "--stored_pipeline",
        type=Path,
        required=True,
        help="path to JSON file with stored pipeline",
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

    Pipeline.from_file(
        save_path=args.stored_pipeline
    ).check_steps()

    ParallelRunner(
        input_files=[x for x in glob.glob(f"{args.input_dir}/*.*") if Path(x).suffix in [".bdf", ".fif"]],
        # input_files=[x for x in glob.glob(f"{args.input_dir}/*.*")],
        output_dir=args.output_dir,
        stored_pipeline=args.stored_pipeline,
        max_workers=args.max_workers,
        mp_spawn_or_fork=args.mp_start_method,
    )
