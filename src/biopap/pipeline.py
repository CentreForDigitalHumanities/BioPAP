import json
import logging
import mne
import re
import sys
import warnings
import yaml
from collections import ChainMap
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Union, Optional
from biopap.modules import CONFIG_MODULE_CLASS_KEY
from biopap.modules.anonymize import Anonymize
from biopap.modules.apply_ica import ApplyICA
from biopap.modules.artifact_reject import ArtifactReject
from biopap.modules.baseline_correction import BaselineCorrection
from biopap.modules.bids import BIDSConversion
from biopap.modules.blink_detection import BlinkDetection
from biopap.modules.downsample import Downsample
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.events_from_annotations import EventsFromAnnotations
from biopap.modules.helpers import custom_formatwarning
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.load_data import LoadData
from biopap.modules.pipeline_step import PipelineStep
from biopap.modules.plot import Plot, PlotTypes
from biopap.modules.rereference import Rereference
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage

log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logging.captureWarnings(True)
warnings.formatwarning = custom_formatwarning
logger = logging.getLogger(__name__)

class Pipeline:

    _steps = []

    def __init__(self, 
                 config_file = Union[str, Path],
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

        self._config_file = config_file
        self._config = self.read_config_file(path=self._config_file)

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
            raise ValueError("No subject_id set")

        self._processed_data = None

    @staticmethod
    def read_config_file(path):
        if path is None:
            return {}

        if not Path(path).exists:
            raise FileNotFoundError(f"'{save_path}' does not exist")

        with open(path, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                logger.error("Error while reading YAML: %s" % str(e))

        return config

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

    def add_step(self, module, cfg=None, cfg_label=None):
        """
        cfg adds to/overwrites values from config file (if any)
        cfg_label for referencing different settings for same class
        """

        def parse_template(s):
            reps = [('{subject_id}', self._subject_id)]

            if not isinstance(s, str):
                return s

            for rep in reps:
                s = s.replace(rep[0], rep[1])

            return s

        if isinstance(module, LoadData):
            raise ValueError("LoadData is automatically part of the pipeline; " \
                "there is no need to add it explicitly. Instantiate Pipeline "\
                "with input_file=<your file> instead.")

        lookup = cfg_label if cfg_label else module.__name__

        if lookup in self._config:
            p_cfg = self._config[lookup]
            cfg = p_cfg if cfg is None else p_cfg | cfg
            cfg = {k: parse_template(v) for k, v in cfg.items()}

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
        min_data_alter = min([x.Order for x in self.steps if x.Module.alters_data == True], default=-1e6)
        max_data_alter = max([x.Order for x in self.steps if x.Module.alters_data == True], default=1e6)
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

        self.steps.sort(key=lambda x: x.Order)
        final_step = max([x.Order for x in self.steps])
        self.check_steps()
        self._processed_data = self._initial_data.copy()

        for step in self.steps:
            cfg = step.Cfg if step.Cfg else {}

            if step.Module.__name__ == SaveOutput.__name__:
                cfg['steps_completed'] = [x for x in self.steps if x.Order < step.Order]
                cfg['intermediate'] = step.Order != final_step

            msg = f"Running ({step.Order}) {step.Module.__name__}"
            if step.Module.log_config and cfg:
                msg = f"{msg} < {cfg}"
            msg = f"{msg} [{self.subject_id}]"
            logger.info(msg)

            try:
                inst = step.Module(** {'raw' : self._processed_data, 'silent' : True } | cfg )
                if len(inst.stdout)>0:
                    [logger.info(f"{step.Module.__name__}:{x} [{self.subject_id}]") for x in inst.stdout]

                self._processed_data = inst.processed
                del inst
            except Exception as e:
                if step.Module.halt_on_exceptions:
                    logger.critical(f"{step.Order}. {step.Module.__name__} failed: {str(e)} [{self.subject_id}]")
                    break
                logger.error(f"({step.Order}) {step.Module.__name__} failed: {str(e)} (non-blocking) [{self.subject_id}]")

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    @classmethod
    def from_config(cls, config_file, input_file, subject_id, **kwargs):
        # make a list of loaded BioPAP modules
        modules_avail = [{'name': obj.__name__, 'class': obj} for name, obj in globals().items()
                         if re.fullmatch(r"\<class \'biopap\.modules\.([a-z_]+)\.([A-Za-z]+)\'\>",
                                         str(obj))]
        # instantiate pipeline
        pipeline = cls(
            input_file=input_file,
            config_file=None,
            subject_id=subject_id,
            **kwargs)

        # read config file
        with open(config_file) as stream:
            try:
                config = yaml.safe_load(stream)
                order = 0
                # go through all config sections
                for step in config:

                    biopap_module = []

                    if config[step]:
                        # check if the BioPAP module class is listed
                        biopap_module = [v[CONFIG_MODULE_CLASS_KEY] for v in config[step] 
                                         if next(iter(v)) == CONFIG_MODULE_CLASS_KEY]

                    if len(biopap_module)==0:
                        # try again by just the name (backward compat)
                        # do substring from start (rather than equals) to catch "<module>_1" etc
                        biopap_module = [str(v['class']) for v in modules_avail if v['name'][:len(step)] == step]
                        if len(biopap_module)==0:
                            logger.warning("'%s' key missing from step %s" % (CONFIG_MODULE_CLASS_KEY, step))
                            continue
                        else:
                            logger.warning("Old config: inferred module %s from key name '%s'" %
                                           (biopap_module[0], step))

                    if len(biopap_module)>1:
                        logger.warning("Multiple '%s' keys in step %s" % (CONFIG_MODULE_CLASS_KEY, step))
                        continue

                    # check if the listed module is in the available modules
                    module_avail = [x for x in modules_avail if str(x['class']) == biopap_module[0]]
                    if len(module_avail)==0:
                        logger.warning("Module '%s' not in available modules" % biopap_module[0])
                        continue

                    if len(module_avail)>1:
                        logger.warning("Module '%s' matches multiple available modules!?" % biopap_module[0])
                        continue

                    if config[step]:
                        # backward compatibility
                        if isinstance(config[step], dict):
                            config[step] = [{k:v} for k,v in config[step].items()]
                        cfg = {k:v for k,v in dict(ChainMap(*config[step])).items() if k != CONFIG_MODULE_CLASS_KEY}
                    else:
                        cfg = {}

                    # add step to pipeline
                    pipeline._steps.append(
                        PipelineStep(
                            Module=module_avail[0]['class'],
                            Cfg=cfg,
                            Order=order
                        ))
                    order += 1
                        
            except yaml.YAMLError as e:
                logger.error("Error while reading YAML: %s" % str(e))

        return pipeline

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
