"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Union, Optional
from biopap.modules.base_class import BaseClass

class LoadData():

    loaded_file = None

    def __init__(self, 
                 file_path: str | Path,
                 preload: bool=True,
                 verbose: Optional[Union[bool, str, int]]=None
                 ) -> None:

        p_log_level = mne.set_log_level(verbose=verbose, return_old_level=True)

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if file_path.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_path, preload)
            else:
                raise ValueError(f"'{file_path}' is not a supported file")

            self.loaded_file = file_path

        except Exception as e:
            print(f"Error: {e}")

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    @staticmethod
    def read_bdf(file_path, preload):
        return mne.io.read_raw_bdf(file_path, preload=preload)

    def run(self):
        pass
