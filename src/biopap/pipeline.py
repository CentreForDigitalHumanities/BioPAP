import argparse
import mne
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from biopap.modules.load_data import LoadData
from biopap.modules.anonymize import Anonymize
from biopap.modules.rereference import Rereference
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.downsample import Downsample
from biopap.modules.segmentation import Segmentation

@dataclass
class PipelineStep:
    Module: Any
    Cfg: dict
    Order: int

    def __repr__(self):
        return f"{self.Order}: {self.Module.__name__} ← {self.Cfg}"

class Pipeline:

    _steps = []

    def __init__(self, config_file, data):
        self.config = self.read_config(config_file)
        self._initial_data = data
        self._processed_data = None

    @staticmethod
    def read_config(config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        return config

    def add_step(self, module, cfg=None, cfg_label=None):
        """
        cfg adds to/overwrites values from config file (if any)
        cfg_label for referencing different settings for same class
        """
        lookup = cfg_label if cfg_label else module.__name__

        if lookup in self.config:
            p_cfg = self.config[lookup]
            cfg = p_cfg if cfg is None else p_cfg | cfg

        order = max([x.Order+1 for x in self._steps], default=0)
        self._steps.append(
            PipelineStep(
                Module=module,
                Cfg=cfg,
                Order=order
            ))

    def run(self):
        self.steps.sort(key=lambda x: x.Order)
        self._processed_data = self._initial_data.copy()
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__} ← {step.Cfg}")
            cfg = step.Cfg if step.Cfg else {}
            inst = step.Module(** {'raw' : self._processed_data } | cfg )
            self._processed_data = inst.processed
            del inst

    def reset(self):
        self._steps = []

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
    parser.add_argument('-c', '--config_file', type=Path, required=True)
    args = parser.parse_args()

    # assuming BDF file as input
    data = LoadData(args.input_file).raw

    pipe = Pipeline(
        config_file=args.config_file,
        data=data)

    pipe.add_step(Anonymize)
    pipe.add_step(Rereference)
    pipe.add_step(EOGChannels)
    pipe.add_step(IIRFilter)
    pipe.add_step(Downsample)

    pipe.run()
