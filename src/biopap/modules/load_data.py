"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from biopap.modules.base_class import BaseClass

class LoadData():

    loaded_file = None

    def __init__(self, 
                 file_path: str | Path,
                 preload: bool=True) -> None:

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

    @staticmethod
    def read_bdf(file_path, preload):
        return mne.io.read_raw_bdf(file_path, preload=preload)

    def run(self):
        pass
