import mne
from dataclasses import dataclass
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

class Pipeline:

    _steps = []

    def __init__(self, initial_data):
        self.initial_data = initial_data

    def add_step(self, module, cfg):
        order = max([x.Order+1 for x in self._steps], default=0)
        self._steps.append(
            PipelineStep(
                Module=module,
                Cfg=cfg,
                Order=order
            ))

    def run(self):
        self.steps.sort(key=lambda x: x.Order)
        data = self.initial_data.copy()
        for step in self.steps:
            print(f"{step.Order:>02}. {step.Module.__name__} <- {step.Cfg}")
            inst = step.Module(**step.Cfg | {'raw': data })
            data = inst.processed
        self.processed = inst.processed

    @property
    def steps(self):
        return self._steps
        
    @property
    def processed_data(self):
        return self.processed


if __name__=="__main__":

    bdf_file = '/data/BioPAP/data/CBN4IL230113.bdf'
    data = LoadData(bdf_file).raw_data

    pipe = Pipeline(initial_data=data)

    pipe.add_step(Downsample, {
        'sfreq': 500
    })

    pipe.add_step(Anonymize, {
        'daysback': 23,
        'experimenter': 'J. Jansen', 
        'participant_id': 'AB00123'
    })
 
    pipe.add_step(EOGChannels, {
        'ref_channels': ['hEOG', 'vEOG'],
        'anode_channels': ['EXG3','EXG5'],
        'cathode_channels': ['EXG4','EXG6']
    })

    pipe.add_step(IIRFilter, {
        'l_freq': 0.1,
        'h_freq': 35
    })

    pipe.add_step(Rereference, {
        'ref_channels': ['EXG1', 'EXG2']
    })

    print(pipe.initial_data.info['experimenter'])

    pipe.run()

    print(pipe.processed_data.info['experimenter'])
