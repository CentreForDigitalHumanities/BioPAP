import multiprocessing as mp
import psutil
from pathlib import Path
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_FILENAME)
from biopap.modules.helpers import (get_logger, read_config_file)
from biopap.modules.bids import BIDSConversion
from biopap.modules.anonymize import Anonymize
from biopap.pipeline import Pipeline
from biopap.modules.save_output import SaveOutput

logger = get_logger()

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
            max_workers = min(max_workers, len(psutil.Process().cpu_affinity()))
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
                        callback=handle_result
                    )

                pool.close()
                pool.join()

        elif max_workers == 1:
            for input_set in input_sets:
                handle_result(self.runner({
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

        for step, step_cfg in config.items():
            if step == 'Pipeline':
                continue

            if input_set['pseudocode'] is None:
                logger.warning(f"'{step_cfg[CONFIG_MODULE_CLASS_KEY]}': skipping pseudonymization")
            else:
                if step_cfg[CONFIG_MODULE_CLASS_KEY] == str(Anonymize):
                    step_cfg['participant_id'] = input_set['pseudocode']
                elif step_cfg[CONFIG_MODULE_CLASS_KEY] == str(BIDSConversion):
                    step_cfg['subject'] = input_set['pseudocode']

            if step_cfg[CONFIG_MODULE_CLASS_KEY] == str(SaveOutput):
                step_cfg['output_file'] = str(step_cfg['output_file']).replace(
                    TPL_FILENAME,
                    Path(input_set['input_file']).name)

        try:
            pipe = Pipeline.from_config(
                config=config,
                input_file=input_set['input_file'],
                subject_id=input_set['pseudocode']
            )
            # pipe.inspect()
            pipe.run()
            exit_code = (0, 'success')
            saved_files = pipe.saved_files
        except Exception as e:
            exit_code = (1, str(e))
            saved_files = []

        return {
            'input_file': input_set['input_file'],
            'pseudocode': input_set['pseudocode'],
            'saved_files': saved_files,
            'exit_code': exit_code
        }

    @property
    def results(self):
        # [{input_file, pseudocode, saved_files, exit_code}, ... ]
        return self._results
