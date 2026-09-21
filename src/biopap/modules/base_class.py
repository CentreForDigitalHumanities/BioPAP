import yaml
from abc import ABC, abstractmethod
from typing import Union, Optional
from biopap.modules import CONFIG_MODULE_CLASS_KEY
from biopap.modules.helpers import CaptureStdout, get_new_filename, YamlDumper

class BaseClass(ABC):

    mod = None
    mne_config = None
    raw = None
    processed = None
    verbose = None
    stdout = []
    log_config = True
    halt_on_exceptions = True
    alters_data = True
    standalone_module = True

    def __init__(self,
                 silent: bool=False):
        # https://mne.tools/stable/generated/mne.verbose.html#mne.verbose
        # The verbose keyword argument can be ‘DEBUG’, ‘INFO’, ‘WARNING’, ‘ERROR’, ‘CRITICAL’, 
        # True (an alias for ‘INFO’), or False (an alias for ‘WARNING’), or
        # 10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR, or 50 for CRITICAL
        self.capture_stdout = CaptureStdout(do_capture=silent)

    def set_config(self, cfg):
        self.mod = cfg['__class__']
        self.mne_config = {self.mod.__name__: cfg}

        for key in ['self', '__class__', 'raw', 'copy', 'silent', 'verbose', 'steps_completed']:
            self.mne_config[self.mod.__name__].pop(key, None)

        if 'kwargs' in cfg:
            for key, val in cfg['kwargs'].items():
                self.mne_config[self.mod.__name__][key] = val
            self.mne_config[self.mod.__name__].pop('kwargs', None)

    def save_config(self, path, cfg_label=None):
        mne_config = self.mne_config
        mod_name = self.mod.__name__

        if cfg_label:
            mne_config[cfg_label] = mne_config.pop(self.mod.__name__)
            mod_name = cfg_label

        mne_config[mod_name][CONFIG_MODULE_CLASS_KEY] = str(self.mod)
        mne_config[mod_name] = {k:v for k,v in mne_config[mod_name].items() if v is not None}

        with open(path, 'a+') as outfile:
            yaml.dump(mne_config, outfile, default_flow_style=False, Dumper=YamlDumper)

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed
