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
from biopap.modules.segmentation import Segmentation

@dataclass
class PipelineStep:
    Module: Any
    Cfg: dict
    Order: int
    Plot: bool = False

    def __repr__(self):
        return f"{self.Order}: {self.Module.__name__} ← {self.Cfg}; {'' if self.Plot else 'not '}plotting"

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

    def add_step(self, module, cfg=None, cfg_label=None, plot=False):
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

    def run(self, plot=False, test_config=False):
        if test_config:
            if not self.test_config(quiet=True):
                print("Encountered errors in config. Run 'test_config()' for details.")
                return

        self.steps.sort(key=lambda x: x.Order)
        data = self._initial_data.copy()
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__} ← {step.Cfg}")
            inst = step.Module(**{'raw': data } | step.Cfg if step.Cfg else {})
            inst.run()
            data = inst.processed

            if step.Plot:
                data.plot(block=True)
            
        self._processed_data = inst.processed
        if plot:
            self._processed_data.plot(block=True)

    def test_config(self, quiet=False):
        errors = 0
        for step in self.steps:
            try:
                inst = step.Module(** {'raw': self._initial_data, 'auto_run': False } | step.Cfg if step.Cfg else {})
            except Exception as e:
                if not quiet:
                    print(f"{step.Module.__name__}: {str(e)}")
                errors += 1

        if errors==0 and not quiet:
            print("No errors")
            return True

        return False

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

    # pipe.add_step(Segmentation)

    if pipe.test_config():
        pipe.run(plot=True)

    # ref_file = '/data/BioPAP/data/CBN1BD071212-Cropped-Change Sampling Rate.edf'
    # ref_data = mne.io.read_raw_edf(ref_file)
    # ref_data.plot()
    # plt.show()

