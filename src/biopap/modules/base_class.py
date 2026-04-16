from abc import ABC, abstractmethod
from typing import Union, Optional
from biopap.modules.helpers import CaptureStdout, get_new_filename

class BaseClass(ABC):

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

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed
