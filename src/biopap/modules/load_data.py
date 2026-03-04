"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Union, Optional
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import Capturing


class LoadData():

    loaded_file = None

    def __init__(self, 
                 file_path: str | Path,
                 logger,
                 preload: bool=True,
                 mne_silent: bool=False,
                 verbose: Optional[Union[bool, str, int]]=None
                 ) -> None:

        p_log_level = mne.set_log_level(verbose=verbose, return_old_level=True)
        self.logger = logger

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if file_path.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_path, preload, mne_silent)
            else:
                raise ValueError(f"'{file_path}' is not a supported file")

            self.loaded_file = file_path

        except Exception as e:
            self.logger.error(f"Error: {e}")

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    def read_bdf(self, file_path, preload, mne_silent):
        if mne_silent:
            with Capturing() as self.mne_capture:
                raw_bdf = mne.io.read_raw_bdf(file_path, preload=preload)
            
            self.logger.info(f"MNE_stdout:{'; '.join(self.mne_capture)}")
        else:
            raw_bdf = mne.io.read_raw_bdf(file_path, preload=preload)

        return raw_bdf

    def run(self):
        pass
