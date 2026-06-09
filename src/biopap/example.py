import argparse
import logging
import warnings
from pathlib import Path
from biopap.modules.helpers import custom_formatwarning
from pipeline import PipelineStep, Pipeline

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
    pipe.add_step(SaveOutput)
    pipe.add_step(Plot)

    if args.stored_pipeline:
        pipe.to_file(
            save_path=args.stored_pipeline,
            label=args.label,
            author=args.author,
            overwrite=True
        )

    # pipe.inspect()
    # pipe.check_steps()
    pipe.run()
