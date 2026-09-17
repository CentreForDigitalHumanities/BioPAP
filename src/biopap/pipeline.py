import json
import logging
import mne
import os
import re
import sys
import warnings
import yaml
from collections import ChainMap
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Union, Optional
from biopap.modules import (CONFIG_MODULE_CLASS_KEY, TPL_SUBJECT_ID)
from biopap.modules.anonymize import Anonymize
from biopap.modules.artifact_reject import ArtifactReject
from biopap.modules.baseline_correction import BaselineCorrection
from biopap.modules.bids import BIDSConversion
from biopap.modules.blink_detection import BlinkDetection
from biopap.modules.downsample import Downsample
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.events_from_annotations import EventsFromAnnotations
from biopap.modules.helpers import (custom_formatwarning, get_logger, read_config_file)
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.notch_filter import NotchFilter
from biopap.modules.load_data import LoadData
from biopap.modules.pipeline_step import PipelineStep
from biopap.modules.plot import Plot, PlotTypes
from biopap.modules.rereference import Rereference
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage

logger = get_logger()

class Pipeline:

    def __init__(self, 
                 config = Union[dict, str, Path],
                 input_file: Optional[Union[str, Path]] = None,
                 data = None,
                 subject_id: str = None,
                 verbose: Optional[Union[bool, str, int]]='WARNING',
                #  output_file: Optional[Union[str, Path]]='./output.fif',
                 **kwargs): 
        # **kwargs go into mne.io.read_raw_bdf via LoadData

        # https://mne.tools/stable/generated/mne.set_log_level.html
        # https://mne.tools/stable/generated/mne.verbose.html#mne.verbose
        # The verbose keyword argument can be ‘DEBUG’, ‘INFO’, ‘WARNING’, ‘ERROR’, ‘CRITICAL’, 
        # True (an alias for ‘INFO’), or False (an alias for ‘WARNING’), or
        # 10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR, or 50 for CRITICAL

        self._steps = []
        self._saved_files = []

        if isinstance(config, dict):
            self._config = config
        elif isinstance(config, (Path, str)):
            # self._config_file = config_file
            self._config = read_config_file(path=config)
        elif config is not None:
            raise ValueError("config should be str, Path or dict (got '%s')" % type(config))

        self.verbose = verbose
        # self.output_file = Path(output_file) if output_file else None

        self._initial_data = None
        # if input_file is None and data is None:
        #     raise ValueError("need input_file or data")
        if data is not None:
            self._initial_data = data
        elif input_file is not None:
            self.load_data(input_file=input_file, **kwargs)
            logger.info(f"Loaded '{input_file}'")

        # not using raw['subject_info']['his_id'], as this is before anonymizing
        if subject_id is not None:
            self._subject_id = subject_id
        elif hasattr(self._initial_data, 'filenames'):
            self._subject_id = Path(self._initial_data.filenames[0]).stem
        elif hasattr(self._initial_data, 'filename'):
            self._subject_id = Path(self._initial_data.filename).stem
        else:
            self._subject_id = None
            # raise ValueError("No subject_id set")
            logger.warning("No subject_id set")

        self._processed_data = None

    @property
    def config(self):
        return self._config

    @property
    def subject_id(self):
        return self._subject_id
        
    @property
    def steps(self):
        return self._steps
        
    @property
    def initial_data(self):
        return self._initial_data

    @property
    def processed_data(self):
        return self._processed_data

    @property
    def saved_files(self):
        return self._saved_files

    def load_data(self, input_file, **kwargs):
        load = LoadData(
            file_path=input_file,
            preload=True,
            silent=True,
            verbose=self.verbose,
            **kwargs)

        if len(load.stdout)>0:
            [logger.info(f"LoadData:{x}") for x in load.stdout]

        self._initial_data = load.raw

    def add_step(self, module, cfg={}, cfg_label=None):
        """
        cfg adds to/overwrites values from config file (if any)
        cfg_label for referencing different settings for same class
        """

        def parse_config_values(s):
            if not isinstance(s, (str, Path)):
                return s

            reps = [(TPL_SUBJECT_ID, self.subject_id)]
            tmp = str(s) if isinstance(s, Path) else s

            for rep in [x for x in reps if x[1] is not None]:
                tmp = tmp.replace(rep[0], rep[1])

            tmp = Path(tmp) if isinstance(s, Path) else tmp

            return tmp

        if isinstance(module, LoadData):
            raise ValueError("LoadData is automatically part of the pipeline; " \
                "there is no need to add it explicitly. Instantiate Pipeline "\
                "with input_file=<your file> instead.")

        lookup = cfg_label if cfg_label else module.__name__

        if lookup in self._config:
            p_cfg = self._config[lookup]
            cfg = p_cfg if cfg is None else p_cfg | cfg
        
        cfg = {k: parse_config_values(v) for k, v in cfg.items() if k != CONFIG_MODULE_CLASS_KEY}

        try:
            check_config = getattr(module, "check_config", None)
            if callable(check_config):
                check_config(cfg=cfg)
        except Exception as e:
            logger.critical(f"Add {module.__name__} failed: {str(e)} [{self.subject_id}]")
            exit()

        order = max([x.Order+1 for x in self._steps], default=0)
        self._steps.append(
            PipelineStep(
                Module=module,
                Cfg=cfg,
                Order=order
            ))

    def reset(self):
        self._steps = []

    def check_steps(self):

        if len(self.steps) == 0:
            warnings.warn("Pipeline contains no steps.")
            return

        anon = [x for x in self.steps if x.Module == Anonymize]
        bids = [x for x in self.steps if x.Module == BIDSConversion]
        save = [x for x in self.steps if x.Module == SaveOutput]
        min_data_alter = min([x.Order for x in self.steps if x.Module.alters_data == True], default=1e6)
        max_data_alter = max([x.Order for x in self.steps if x.Module.alters_data == True], default=-1e6)
        min_anon = min([x.Order for x in self.steps if x.Module.__name__ == Anonymize.__name__], default=1e6)

        # make sure LoadData isn't called directly
        if LoadData in [x.Module for x in self.steps]:
            raise ValueError("LoadData is automatically part of the pipeline; " \
                "there is no need to add it explicitly. Instantiate Pipeline "\
                "with input_file=<your file> instead.")

        # check presence of SaveOutput
        if len(save) == 0:
            raise ValueError("Pipeline contains no SaveOutput; add SaveOutput to save results.")

        # check presence of data altering modules after SaveOutput
        elif max([x.Order for x in save]) < max_data_alter:
            warnings.warn("Pipeline contains data processing steps after SaveOutput.")

        # check presence of Anonymize before SaveOutput
        if len(anon) == 0 or (min([x.Order for x in save]) < min_anon):
            warnings.warn("Consider adding Anonymize before SaveOutput.")

        # BIDS checks
        if len(bids) > 0:
            # check BIDS is in place before data is altered
            if min([x.Order for x in bids]) > min_data_alter:
                warnings.warn("There are steps in your pipeline preceding BIDSConversion " \
                              "that alter data (BIDS is intended to save raw data).")

            # check single BIDS instance
            if len(bids) > 1:
                warnings.warn("The BIDS format is intended to save raw data only, there " \
                              f"is no point to adding additional BIDS modules (found {len(bids)})")
            
            if len(anon) == 0 or \
                min([x.Order for x in bids]) < min_anon:
                warnings.warn("Consider adding Anonymize before exporting to BIDS.")

    def run(self):

        if self._initial_data is None:
            raise ValueError("Need input_file or data")

        p_log_level = mne.set_log_level(verbose=self.verbose, return_old_level=True)

        self._processed_data = self._initial_data.copy()

        self.steps.sort(key=lambda x: x.Order)
        self.check_steps()
        final_step = max([x.Order for x in self.steps])

        for step in self.steps:
            cfg = step.Cfg if step.Cfg else {}

            msg = f"Running ({step.Order}) {step.Module.__name__}"
            if step.Module.log_config and cfg:
                msg = f"{msg} < {cfg}"
            logger.info(f"{msg} [{self.subject_id}]")

            if step.Module.__name__ == SaveOutput.__name__:
                cfg['_steps_completed'] = [x for x in self.steps if x.Order < step.Order]
                cfg['_intermediate'] = step.Order != final_step

            try:
                inst = step.Module(** {'raw': self._processed_data, 'silent': True } | cfg )
                if len(inst.stdout)>0:
                    [logger.info(f"{step.Module.__name__}:{x} [{self.subject_id}]") for x in inst.stdout]

                self._processed_data = inst.processed

                if step.Module.__name__ == SaveOutput.__name__:
                    self._saved_files = inst.saved_files

                del inst
            except Exception as e:
                if step.Module.halt_on_exceptions:
                    logger.critical(f"{step.Order}. {step.Module.__name__} failed: {str(e)} [{self.subject_id}]")
                    break
                logger.error(f"({step.Order}) {step.Module.__name__} failed: {str(e)} (non-blocking) [{self.subject_id}]")

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    def _print_cfg(self, data, indent=4):

        def valfrmt(x):
            return f"'{x}'" if isinstance(x, str) else str(x)

        if not data:
            return

        for key, val in data.items():
            if isinstance(val, (float, int, bool, str)) or val is None:
                print(f"{' '*indent}{key}: {valfrmt(val)}")
            elif isinstance(val, list):
                print(f"{' '*indent}{key}: [{', '.join(map(valfrmt, val))}]")
            elif isinstance(val, dict):
                print(f"{' '*indent}{key}:")
                for subkey, subval in val.items():
                    self._print_cfg({subkey: subval}, indent+2)
            else:
                print(f"{' '*indent}{key}: {val}")

    def inspect(self):
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__}{' *' if step.Module.alters_data else ''}")
            self._print_cfg(step.Cfg)
            print()

        if len(self.steps) > 0:
            print("(modules marked * alter their input data)")

    @classmethod
    def from_config(cls, config: Union[dict, str, Path], input_file, subject_id, **kwargs):

        # check config format
        if isinstance(config, (Path, str)):
            config = read_config_file(config)
        elif not isinstance(config, dict):
            raise ValueError("config should be str, Path or dict (got '%s')" % type(config))

        if 'Pipeline' in config:
            kwargs = kwargs | config['Pipeline']

        # instantiate empty pipeline
        pipe = cls(
            input_file=input_file,
            config={},
            subject_id=subject_id,
            **kwargs)

        # make a list of loaded BioPAP modules
        modules_avail = [{'name': obj.__name__, 'class': obj} for name, obj in globals().items()
                         if re.fullmatch(r"\<class \'biopap\.modules\.([a-z_]+)\.([A-Za-z]+)\'\>",
                                         str(obj))]
        for step, step_cfg in config.items():

            if step == 'Pipeline':
                continue

            if not CONFIG_MODULE_CLASS_KEY in step_cfg:
                raise ValueError("'%s' misses '%s' key; run 'tools/update_config.py' to update config file" % (step, CONFIG_MODULE_CLASS_KEY))

            biopap_module = step_cfg[CONFIG_MODULE_CLASS_KEY]

            # check if the listed module is in the available modules
            module_avail = [x for x in modules_avail if str(x['class']) == biopap_module]

            if len(module_avail)==0:
                raise ValueError("Module '%s' not in available modules" % biopap_module)

            if len(module_avail)>1:
                raise ValueError("Module '%s' matches multiple available modules!?" % biopap_module)

            pipe.add_step(
                module=module_avail[0]['class'],
                cfg={k: v for k,v in step_cfg.items() if k != CONFIG_MODULE_CLASS_KEY},
            )
    
        return pipe
