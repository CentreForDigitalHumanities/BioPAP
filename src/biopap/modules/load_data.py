"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Optional
from biopap.modules.base_class import BaseClass

class LoadData():

    loaded_file = None

    def __init__(self, 
                 config_file: Optional[str | Path]=None,
                 file_path: Optional[str | Path]=None,
                 preload: bool=True) -> None:

        try:
            if file_path:
                file_to_load = Path(file_path)
            elif config_file:
                with open(config_file, 'r') as file:
                    config = yaml.safe_load(file)
                file_to_load = Path(config[self.__class__.__name__]['file_path'])
            else:
                raise ValueError("Need file_path or LoadData file_path-entry in config file")

            if not file_to_load.exists():
                raise ValueError(f"File '{file_to_load}' does not exist")

            if file_to_load.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_to_load, preload)
            else:
                raise ValueError(f"'{file_to_load}' is not a supported file")

            self.loaded_file = file_to_load

        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def read_bdf(file_path, preload):
        return mne.io.read_raw_bdf(file_path, preload=preload)

    def run(self):
        pass
