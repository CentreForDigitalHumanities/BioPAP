import argparse
import matplotlib.pyplot as plt
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

@dataclass
class PipelineStep:
    Module: Any
    Cfg: dict
    Order: int
    Plot: bool

class Pipeline:

    _steps = []

    def __init__(self, config_file, initial_data):
        self.config = self.read_config(config_file)
        self.initial_data = initial_data

    @staticmethod
    def read_config(config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        return config

    def add_step(self, module, cfg=None, plot=False, cfg_label=None):
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
                Order=order,
                Plot=plot
            ))

    def run(self, plot=False):
        self.steps.sort(key=lambda x: x.Order)
        data = self.initial_data.copy()
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__} <- {step.Cfg}")
            inst = step.Module(**step.Cfg | {'raw': data })
            data = inst.processed
            if step.Plot:
                data.plot()
                plt.show()
        self.processed = inst.processed
        if plot:
            self.processed.plot()
            plt.show()


    @property
    def steps(self):
        return self._steps
        
    @property
    def processed_data(self):
        return self.processed


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=Path, required=True)
    parser.add_argument('-c', '--config_file', type=Path, required=True)
    args = parser.parse_args()

    # assuming BDF file as input
    data = LoadData(args.input_file).raw_data

    pipe = Pipeline(
        config_file=args.config_file,
        initial_data=data)

    pipe.add_step(Anonymize)
    pipe.add_step(Rereference)
    pipe.add_step(EOGChannels)
    pipe.add_step(IIRFilter)
    pipe.add_step(Downsample)
 
    pipe.run(plot=True)

    # ref_file = '/data/BioPAP/data/CBN1BD071212-Cropped-Change Sampling Rate.edf'
    # ref_data = mne.io.read_raw_edf(ref_file)
    # ref_data.plot()
    # plt.show()

