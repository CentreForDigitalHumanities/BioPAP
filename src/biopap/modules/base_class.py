from abc import ABC, abstractmethod
from typing import Union, Optional

class BaseClass(ABC):

    raw = None
    processed = None
    verbose = None
    exit_code = 0

    def __init__(self, 
                 verbose: Optional[Union[bool, str, int]]=None,
                 export_format: Optional[str]=None,
                 output_file: Optional[str]=None,
                 overwrite: bool=True):
        # https://mne.tools/stable/generated/mne.verbose.html#mne.verbose
        # The verbose keyword argument can be ‘DEBUG’, ‘INFO’, ‘WARNING’, ‘ERROR’, ‘CRITICAL’, 
        # True (an alias for ‘INFO’), or False (an alias for ‘WARNING’), or
        # 10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR, or 50 for CRITICAL
        self.verbose = verbose
        self.export_format = export_format
        self.output_file = output_file
        self.overwrite = overwrite

        if self.export_format == 'fif':
            self.export_fif(self.output_file, self.overwrite)
        elif self.export_format == 'csv':
            self.export_csv(self.output_file, self.overwrite)

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed
    
    def export_fif(self, output_file, overwrite):
        if self.processed is None:
            raise ValueError("no processed data to export")

        self.processed.save(output_file, overwrite=overwrite)

    def export_csv(self, output_file, overwrite):
        if self.processed is None:
            raise ValueError("no processed data to export")

        # TODO: implement export_csv