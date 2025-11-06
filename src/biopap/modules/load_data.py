"""Class for loading BDF files"""

import mne
from pathlib import Path
from biopap.modules.base_class import BaseClass

class LoadData(BaseClass):

    def __init__(self, 
                 file_path: str | Path,
                 preload: bool=True) -> None:
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if not file_path.suffix.lower()=='.bdf':
                raise ValueError(f"'{file_path}' is not a BDF file")

            self.raw = mne.io.read_raw_bdf(file_path, preload=preload)

        except Exception as e:
            print(f"Error: {e}")
