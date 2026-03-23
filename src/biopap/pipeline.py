import argparse
import json
import logging
import mne
import sys
import yaml
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any, Union, Optional

from biopap.modules.anonymize import Anonymize
from biopap.modules.artifact_reject import ArtifactReject
from biopap.modules.baseline_correction import BaselineCorrection
from biopap.modules.bids import BIDSConversion
from biopap.modules.blink_detection import BlinkDetection
from biopap.modules.downsample import Downsample
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.apply_ica import ApplyICA
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.load_data import LoadData
from biopap.modules.plot import Plot
from biopap.modules.rereference import Rereference
from biopap.modules.segmentation import Segmentation
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage


log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

def add_logfile_handler(log_file=None):
    global logger
    if not log_file:
        return
    fh = logging.FileHandler(log_file)
    fh.setFormatter(logging.Formatter(log_format))
    logger.addHandler(fh)


@dataclass
class PipelineStep:
    Module: Any
    Cfg: dict
    Order: int
    Save: Optional[Union[str, Path]] = None

    def __repr__(self):
        return f"{self.Order}: {self.Module.__name__} ← {self.Cfg} | save={self.Save}"

    def as_dict(self):
        return  {
            'module': self.Module.__name__,
            'cfg': self.Cfg,
            'order': self.Order,
            'save': self.Save
            }


class Pipeline:

    _steps = []

    def __init__(self, 
                 config_file,
                 input_file = None,
                 data = None,
                 verbose: Optional[Union[bool, str, int]]='WARNING',
                 **kwargs): 
        # **kwargs ultimately go into mne.io.read_raw_bdf via LoadData

        # https://mne.tools/stable/generated/mne.set_log_level.html
        # https://mne.tools/stable/generated/mne.verbose.html#mne.verbose
        # The verbose keyword argument can be ‘DEBUG’, ‘INFO’, ‘WARNING’, ‘ERROR’, ‘CRITICAL’, 
        # True (an alias for ‘INFO’), or False (an alias for ‘WARNING’), or
        # 10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR, or 50 for CRITICAL

        self.config_file = config_file
        self.config = self.read_config(self.config_file)

        self.verbose = verbose

        if input_file is None and data is None:
            raise ValueError("need input_file or data")
        elif data is not None:
            self._initial_data = data
        else:
            self._initial_data = self.load_data(input_file=input_file, **kwargs)
        
        self._processed_data = None

    @staticmethod
    def read_config(config_file):
        if config_file is None:
            return {}

        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        return config

    def load_data(self, input_file, **kwargs):
        load = LoadData(
            file_path=input_file,
            logger=logger,
            preload=True,
            mne_silent=True,
            verbose=self.verbose,
            **kwargs)

        if load.exit_code == 1:
            raise ValueError(f"could not load '{input_file}'")

        return load.raw

    def add_step(self, module, cfg=None, cfg_label=None, save=None):
        """
        cfg adds to/overwrites values from config file (if any)
        cfg_label for referencing different settings for same class
        """
        lookup = cfg_label if cfg_label else module.__name__

        if lookup in self.config:
            p_cfg = self.config[lookup]
            cfg = p_cfg if cfg is None else p_cfg | cfg

        if cfg and 'save' in cfg:
            if save:
                _save = cfg.pop('save')
                logger.warning(f"'save' defined in config file and in add_step. Using value from add_step: '{save}'")
            else:
                save = cfg.pop('save')

        order = max([x.Order+1 for x in self._steps], default=0)
        self._steps.append(
            PipelineStep(
                Module=module,
                Cfg=cfg,
                Order=order,
                Save=Path(save) if save else None
            ))

    def reset(self):
        self._steps = []

    def run(self):

        p_log_level = mne.set_log_level(verbose=self.verbose, return_old_level=True)

        self.steps.sort(key=lambda x: x.Order)
        self._processed_data = self._initial_data.copy()

        dgts = int(len(str(max([x.Order for x in self.steps]))))

        for step in self.steps:
            cfg = step.Cfg if step.Cfg else {}
            logger.info(f"step{step.Order:> {dgts}}; {step.Module.__name__}; {cfg}")

            try:
                inst = step.Module(** {'raw' : self._processed_data, 'logger' : logger } | cfg )
                if inst.exit_code != 0:
                    logger.critical(f"step {step.Order}. {step.Module.__name__} failed; exiting pipeline")
                    break
            except Exception as e:
                logger.error(str(e))
            
            self._processed_data = inst.processed

            if step.Save:
                step.Save.parent.mkdir(parents=True, exist_ok=True)
                inst.processed.save(step.Save, overwrite=True)
                logger.info(f"saved output of step {step.Order} to '{step.Save}'")

            del inst

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    def to_file(self, save_path, overwrite=False):
        if not overwrite and save_path.exists():
            p_save_path = save_path
            n = 1
            while p_save_path.exists():
                p_save_path = save_path.parent / f"{save_path.stem}_({n}){save_path.suffix}"
                n += 1
            save_path = p_save_path

        with open(save_path, 'w+', encoding='utf-8') as file:
            json.dump({
                    'biopap_pipeline': [x.as_dict() for x in self.steps],
                    'config_file': str(self.config_file)  # not really necessary
                }, file, ensure_ascii=True
            )

        logger.info(f"wrote pipeline to '{save_path}'")

    @classmethod
    def from_file(cls, save_path, input_file, **kwargs):
        if not Path(save_path).exists:
            raise FileNotFoundError(f"'{save_path}' does not exist")

        with open(save_path, 'r') as file:
            pipe_cfg = json.load(file)

        if not 'biopap_pipeline' in pipe_cfg:
            raise ValueError(f"'biopap_pipeline' section not found in '{save_path}'")

        pipeline = cls(input_file=input_file, config_file=None, **kwargs)

        for step in pipe_cfg['biopap_pipeline']:
            pipeline._steps.append(
                PipelineStep(
                    Module=getattr(sys.modules[__name__], step['module']),
                    Cfg=step['cfg'],
                    Order=step['order'],
                    Save=Path(step['save']) if step.get('save') else None
                ))

        return pipeline

    @property
    def steps(self):
        return self._steps
        
    @property
    def initial_data(self):
        return self._initial_data

    @property
    def processed_data(self):
        return self._processed_data


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=Path, required=True)
    parser.add_argument('-c', '--config_file', type=Path)
    parser.add_argument('-s', '--stored_pipeline', type=Path)
    parser.add_argument('--log_file', type=Path)
    args = parser.parse_args()

    if (not args.config_file and not args.stored_pipeline):
        raise ValueError('need either --config_file and/or --stored_pipeline')

    add_logfile_handler(args.log_file)

    if args.stored_pipeline and not args.config_file:

        Pipeline.from_file(
            save_path=args.stored_pipeline,
            input_file=args.input_file
        ).run()
    
    else:

        pipe = Pipeline(
            config_file=args.config_file,
            input_file=args.input_file)

        pipe.add_step(Anonymize)
        pipe.add_step(Rereference)
        pipe.add_step(EOGChannels)
        pipe.add_step(IIRFilter)
        pipe.add_step(Downsample)

        if args.stored_pipeline:
            pipe.to_file(save_path=args.stored_pipeline)

        pipe.run()
