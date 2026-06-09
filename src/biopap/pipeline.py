import argparse
import json
import logging
import mne
import sys
import warnings
import yaml
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Any, Union, Optional

from biopap.modules.anonymize import Anonymize
from biopap.modules.apply_ica import ApplyICA
from biopap.modules.artifact_reject import ArtifactReject
from biopap.modules.baseline_correction import BaselineCorrection
from biopap.modules.bids import BIDSConversion
from biopap.modules.blink_detection import BlinkDetection
from biopap.modules.downsample import Downsample
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.helpers import custom_formatwarning
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.load_data import LoadData
from biopap.modules.plot import Plot, PlotTypes
from biopap.modules.rereference import Rereference
from biopap.modules.segmentation import Segmentation
from biopap.modules.save_output import SaveOutput
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage

log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logging.captureWarnings(True)
warnings.formatwarning = custom_formatwarning
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

    def __repr__(self):
        return f"{self.Order}: {self.Module.__name__} ← {self.Cfg}"

    def as_dict(self):
        return  {
            'module': self.Module.__name__,
            'cfg': self.Cfg,
            'order': self.Order,
            }


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
        self._config = self.read_config(self._config_file)

        self.verbose = verbose
        # self.output_file = Path(output_file) if output_file else None

        self._initial_data = None
        # if input_file is None and data is None:
        #     raise ValueError("need input_file or data")
        if data is not None:
            self._initial_data = data
        elif input_file is not None:
            self.load_data(input_file=input_file, **kwargs)
            logger.info(f"loaded '{input_file}'")

        # not using raw['subject_info']['his_id'], as this is before anonymizing
        if subject_id is not None:
            self._subject_id = subject_id
        elif hasattr(self._initial_data, 'filenames'):
            self._subject_id = Path(self._initial_data.filenames[0]).stem
        elif hasattr(self._initial_data, 'filename'):
            self._subject_id = Path(self._initial_data.filename).stem
        else:
            raise ValueError("no subject_id set")

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
            logger.critical(f"add {module.__name__} failed: {str(e)} [{self.subject_id}]")
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
        if SaveOutput.__name__ not in [x.Module.__name__ for x in self.steps]:
            raise ValueError("Pipeline contains no SaveOutput; add SaveOutput to save pipeline results")
        
        elif max([x.Order for x in self.steps if x.Module.__name__ == SaveOutput.__name__]) < \
             max([x.Order for x in self.steps if x.Module.alters_data == True]):
            warnings.warn("Pipeline contains data processing steps after SaveOutput")

        bids = [x for x in self.steps if x.Module.__name__ == BIDSConversion.__name__ ]
        if len(bids) > 0:
            first_data_alter = min([x.Order for x in self.steps if x.Module.alters_data == True])
            if bids[0].Order > first_data_alter:
                warnings.warn("The BIDS format is intended to save raw data only. " \
                              "Currently, there are steps in your pipeline preceding the BIDS " \
                              "module that alter data.")
            if len(bids) > 1:
                warnings.warn("The BIDS format is intended to save raw data only. " \
                              f"There is no reason to add additional BIDS modules (found {len(bids)}).")

    def run(self):

        if self._initial_data is None:
            raise ValueError("need input_file or data")

        p_log_level = mne.set_log_level(verbose=self.verbose, return_old_level=True)

        self.steps.sort(key=lambda x: x.Order)
        self.check_steps()
        self._processed_data = self._initial_data.copy()

        for step in self.steps:
            cfg = step.Cfg if step.Cfg else {}

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

    def to_file(self, save_path, label=None, author=None, overwrite=False):
        if not overwrite and save_path.exists():
            p_save_path = save_path
            n = 1
            while p_save_path.exists():
                p_save_path = save_path.parent / f"{save_path.stem}_({n}){save_path.suffix}"
                n += 1
            save_path = p_save_path

        data = {
            'biopap_pipeline': [x.as_dict() for x in self.steps],
            'config_file': str(self._config_file),  # not really necessary
            'label': label,
            'author': author,
            'created': datetime.now().strftime("%c"),
        }

        with open(save_path, 'w+', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=True)

        logger.info(f"wrote pipeline to '{save_path}'")

    @staticmethod
    def read_saved(save_path):
        if not Path(save_path).exists:
            raise FileNotFoundError(f"'{save_path}' does not exist")

        with open(save_path, 'r') as file:
            pipe_cfg = json.load(file)

        if not 'biopap_pipeline' in pipe_cfg:
            raise ValueError(f"'biopap_pipeline' section not found in '{save_path}'")

        return pipe_cfg

    @classmethod
    def from_file(cls, save_path, input_file, subject_id, **kwargs):
        pipe_cfg = cls.read_saved(save_path)
        pipeline = cls(
            input_file=input_file,
            config_file=None,
            subject_id=subject_id,
            **kwargs)

        for step in pipe_cfg['biopap_pipeline']:
            pipeline._steps.append(
                PipelineStep(
                    Module=getattr(sys.modules[__name__], step['module']),
                    Cfg=step['cfg'],
                    Order=step['order']
                ))

        return pipeline

    def print_cfg(self, data, indent=4):

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
                    self.print_cfg({subkey: subval}, indent+2)
            else:
                print(f"{' '*indent}{key}: {val}")

    def inspect(self):
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__}{' *' if step.Module.alters_data else ''}")
            self.print_cfg(step.Cfg)
            print()

        print("(modules marked * alter their input data)")

    @classmethod
    def inspect_saved(cls, save_path):
        pipe_cfg = cls.read_saved(save_path)
        print(f"   file: {save_path}")
        print(f"  label: {pipe_cfg['label']}")
        print(f" author: {pipe_cfg['author']}")
        print(f"created: {pipe_cfg['created']}")
        print()

        tmp = cls.from_file(
            save_path=save_path,
            input_file=None,
            subject_id=0)

        tmp.inspect()

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


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=Path, required=True)
    parser.add_argument('-c', '--config_file', type=Path)
    parser.add_argument('-s', '--stored_pipeline', type=Path)
    parser.add_argument('--label', type=str)
    parser.add_argument('--author', type=str)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--log_file', type=Path)
    args = parser.parse_args()

    if (not args.config_file and not args.stored_pipeline):
        raise ValueError('need either --config_file and/or --stored_pipeline')

    if (args.inspect and not args.stored_pipeline):
        raise ValueError('--inspect requires --stored_pipeline')

    add_logfile_handler(args.log_file)

    if args.stored_pipeline and args.inspect:

        Pipeline.inspect(save_path=args.stored_pipeline, compact=False)
    
    elif args.stored_pipeline and not args.config_file:

        Pipeline.from_file(
            save_path=args.stored_pipeline,
            input_file=args.input_file
        ).run()
    
    else:

        pipe = Pipeline(
            config_file=args.config_file,
            input_file=args.input_file)

        pipe.add_step(Anonymize)
        # pipe.add_step(BIDSConversion)
        pipe.add_step(Rereference)
        pipe.add_step(SetChannelTypeAndMontage)
        pipe.add_step(EOGChannels)
        pipe.add_step(IIRFilter)
        pipe.add_step(Downsample)
        pipe.add_step(BlinkDetection)
        pipe.add_step(Plot, cfg={
            'plot_types': PlotTypes.SPECTRUM_TOPO|PlotTypes.SPECTRUM_TOPO_MAP|PlotTypes.SPECTRUM_PLOT,
            'save_folder': './'})
        pipe.add_step(Segmentation)
        pipe.add_step(ArtifactReject)
        pipe.add_step(BaselineCorrection)
        pipe.add_step(ApplyICA)
        pipe.add_step(Plot, cfg={
            'plot_types': PlotTypes.PLOT|PlotTypes.SENSORS,
            'save_folder': './'})
        pipe.add_step(Plot)
        pipe.add_step(SaveOutput)

        if args.stored_pipeline:
            pipe.to_file(
                save_path=args.stored_pipeline,
                label=args.label,
                author=args.author,
                overwrite=True
            )

        # pipe.inspect()
        pipe.run()
