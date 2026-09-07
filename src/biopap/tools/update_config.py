import re
import sys
import yaml
from pathlib import Path
from biopap.modules import CONFIG_MODULE_CLASS_KEY
from biopap.modules.anonymize import Anonymize
from biopap.modules.artifact_reject import ArtifactReject
from biopap.modules.baseline_correction import BaselineCorrection
from biopap.modules.bids import BIDSConversion
from biopap.modules.blink_detection import BlinkDetection
from biopap.modules.downsample import Downsample
from biopap.modules.eog_channels import EOGChannels
from biopap.modules.events_from_annotations import EventsFromAnnotations
from biopap.modules.helpers import (read_config_file, YamlDumper)
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.load_data import LoadData
from biopap.modules.plot import Plot, PlotTypes
from biopap.modules.rereference import Rereference
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage

if len(sys.argv) == 1:
    print("Need config file path as argument")
    exit()

cfg_file = sys.argv[1]

# list of loaded BioPAP modules
modules_avail = [{'name': obj.__name__, 'class': obj} for name, obj in globals().items()
                 if re.fullmatch(r"\<class \'biopap\.modules\.([a-z_]+)\.([A-Za-z]+)\'\>",
                 str(obj))]

config = read_config_file(cfg_file)

for step, step_cfg in config.items():
    if step != 'Pipeline' and CONFIG_MODULE_CLASS_KEY not in step_cfg:
        # try by resolving the step's name (backward compatibility)
        # do substring from start (rather than equals) to catch "<module>_1" etc
        biopap_module = [str(v['class']) for v in modules_avail if v['name'] == step[:len(v['name'])]]
        if len(biopap_module)==0:
            raise ValueError("'%s' missing from '%s'; could not resolve '%s' to BioPAP module" % (CONFIG_MODULE_CLASS_KEY, step, step))
        else:
            print("Inferred module %s from key name '%s'" % (biopap_module[0], step))
            step_cfg[CONFIG_MODULE_CLASS_KEY] = biopap_module[0]

if config != read_config_file(cfg_file):
    new_file = Path(cfg_file).parent / f"{Path(cfg_file).stem}_new{Path(cfg_file).suffix}"
    with open(new_file, 'w+') as f:
        yaml.dump(config, f, default_flow_style=False, Dumper=YamlDumper)
    print("Wrote '%s" % new_file)
else:
    print("No changes made")