import argparse
import logging
import warnings
from pathlib import Path
from biopap.pipeline import Pipeline
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
from biopap.modules.pipeline_step import PipelineStep
from biopap.modules.plot import Plot, PlotTypes
from biopap.modules.rereference import Rereference
from biopap.modules.segmentation import Segmentation
from biopap.modules.save_output import SaveOutput
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_file', type=Path, required=True)
parser.add_argument('-c', '--config_file', type=Path, required=True)
args = parser.parse_args()


# Creating a new pipeline manually 
pipe = Pipeline(
    config_file=args.config_file,
    input_file=args.input_file)

# Adding steps
pipe.add_step(Anonymize)
pipe.add_step(BIDSConversion)
pipe.add_step(Rereference)
pipe.add_step(SetChannelTypeAndMontage)
pipe.add_step(EOGChannels)
pipe.add_step(IIRFilter)
pipe.add_step(Downsample)
pipe.add_step(BlinkDetection)

# Overriding settings from config file
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
pipe.add_step(SaveOutput)
pipe.add_step(SaveOutput, cfg={"export_formats": "fif", "output_file": "./preprocessed_raw.fif", "overwrite": True})

pipe.inspect()

if input('Run pipeline? (y/n) ').lower() == 'y':
    pipe.run()
