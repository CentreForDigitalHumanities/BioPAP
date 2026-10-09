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
from biopap.modules.helpers import (read_config_file, read_config_string, YamlDumper)
from biopap.modules.iir_filter import IIRFilter
from biopap.modules.load_data import LoadData
from biopap.modules.plot import Plot
from biopap.modules.rereference import Rereference
from biopap.modules.save_output import SaveOutput
from biopap.modules.segmentation import Segmentation
from biopap.modules.set_channel_type_and_montage import SetChannelTypeAndMontage


class ConfigurationUpdater:

    """
    The class is for updating configuration files that lack explicit references to each
    step's BioPAP module. In order to create the pipeline at runtime, each step in the
    configuration file requires the key '_biopap_module' with a value pointing to the
    correct module. Example:

        ArtifactReject:
            _biopap_module: <class 'biopap.modules.artifact_reject.ArtifactReject'>
            [...]

    If the pipeline steps lack the `_biopap_module'-key, they can be added calling either
    ConfigurationUpdater.convert_file() on your configuration file, or 
    ConfigurationUpdater.convert() on an in-memory configuration dictionary.
    """

    def __init__(self):
        # list of loaded BioPAP modules
        self.modules_avail = [{'name': obj.__name__, 'class': obj} for name, obj in globals().items()
                        if re.fullmatch(r"\<class \'biopap\.modules\.([a-z_]+)\.([A-Za-z]+)\'\>",
                        str(obj)) and obj.standalone_module]

    def get_modules(self):
        return self.modules_avail

    def _convert(self, config):
        for step, step_cfg in config.items():

            if step == 'Pipeline':
                continue

            if CONFIG_MODULE_CLASS_KEY not in step_cfg:
                # try by resolving the step's name (backward compatibility)
                # do substring from start (rather than equals) to catch "<module>_1" etc
                biopap_module = [str(v['class']) for v in self.modules_avail if v['name'] == step[:len(v['name'])]]
                if len(biopap_module)==0:
                    raise ValueError("'%s' missing from '%s'; could not resolve '%s' to BioPAP module" %
                        (CONFIG_MODULE_CLASS_KEY, step, step))
                else:
                    print("Inferred module %s from key name '%s'" % (biopap_module[0], step))
                    step_cfg[CONFIG_MODULE_CLASS_KEY] = biopap_module[0]
            else:
                biopap_module = [v for v in self.modules_avail if str(v['class']) == step_cfg[CONFIG_MODULE_CLASS_KEY]]
                if len(biopap_module)==0:
                    raise ValueError("%s.%s: '%s' does not match any BioPAP module" %
                                     (step, CONFIG_MODULE_CLASS_KEY, step_cfg[CONFIG_MODULE_CLASS_KEY]))
                else:
                    print("%s.%s already present: '%s'" %
                          (step, CONFIG_MODULE_CLASS_KEY, step_cfg[CONFIG_MODULE_CLASS_KEY]))

        return config
            
    def convert(self, config_in):
        config = read_config_string(config_in)
        new_config = self._convert(config)
        return yaml.dump(new_config, Dumper=YamlDumper)

    def convert_file(self, config_file_in):
        if not Path(config_file_in).exists():
            raise FileNotFoundError("File not found: '%s'" % config_file_in)

        new_config = self._convert(read_config_file(Path(config_file_in)))

        if new_config != read_config_file(Path(config_file_in)):
            new_file = Path(config_file_in).parent / f"{Path(config_file_in).stem}_new{Path(config_file_in).suffix}"
            with open(new_file, 'w+') as f:
                yaml.dump(new_config, f, default_flow_style=False, Dumper=YamlDumper)
            print("Wrote new configuration to '%s" % new_file)
        else:
            print("No changes made")
