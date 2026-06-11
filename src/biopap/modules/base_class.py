import yaml
from abc import ABC, abstractmethod
from typing import Union, Optional
from biopap.modules.helpers import CaptureStdout, get_new_filename

class BaseClass(ABC):

    mod = None
    mne_config = None
    raw = None
    processed = None
    verbose = None
    stdout = []
    log_config = True
    halt_on_exceptions = True

    def __init__(self,
                 silent: bool=False):
        # https://mne.tools/stable/generated/mne.verbose.html#mne.verbose
        # The verbose keyword argument can be ‘DEBUG’, ‘INFO’, ‘WARNING’, ‘ERROR’, ‘CRITICAL’, 
        # True (an alias for ‘INFO’), or False (an alias for ‘WARNING’), or
        # 10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR, or 50 for CRITICAL
        self.capture_stdout = CaptureStdout(do_capture=silent)

    def set_config(self, cfg):
        self.mod = cfg['__class__']
        self.mne_config = {self.mod.__name__: [{k:v} for k,v in cfg.items() \
            if k not in [ 'self', 'raw', 'copy', 'silent', 'verbose', '__class__', 'kwargs']] }
        if 'kwargs' in cfg:
            self.mne_config[self.mod.__name__].extend([{k:v} for k,v in cfg['kwargs'].items()])

    def save_config(self, path, cfg_label=None):
        mne_config = self.mne_config
        mod_name = self.mod.__name__

        if cfg_label:
            mne_config[cfg_label] = mne_config.pop(self.mod.__name__)
            mod_name = cfg_label

        for key, val_pair in enumerate(mne_config[mod_name]):
            # turn tuples into lists to avoid ' !!python/tuple' constructor tags
            for var, val in [(var, val) for var, val in val_pair.items() if isinstance(val, tuple)]:
                mne_config[mod_name][key][var] = list(val)
            # remove None values
            for var in [var for var, val in val_pair.items() if val is None]:
                del mne_config[mod_name][key][var]
            # remove empty vars
            if not val_pair:
                del mne_config[mod_name][key]

        mne_config[mod_name].append({'__biopap_module': str(self.mod)})

        # append to yaml file
        with open(path, 'a+') as outfile:
            yaml.dump(mne_config, outfile, default_flow_style=False)

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed

    @property
    def config(self):
        return self.mne_config
