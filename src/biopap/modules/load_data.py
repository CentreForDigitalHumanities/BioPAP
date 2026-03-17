"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Union, Optional
from biopap.modules.base_class import BaseClass

class LoadData():
    """
    Class for loading BDF data from file.

    Parameters
    ----------
    file_path : str | Path
        Path to the input BDF file.
    preload : bool | str, default True
        Preload data into memory for data manipulation and faster indexing. If True, the data will be 
        preloaded into memory (fast, requires large amount of memory). If preload is a string, 
        preload is the file name of a memory-mapped file which is used to store the data on the 
        hard drive (slower, requires less memory).
    **kwargs
        Additional keyword arguments passed to the underlying
        ``mne.io.read_raw_bdf()`` method.

    Attributes
    ----------
    raw : mne.io.Raw
        Loaded raw data.
    """

    loaded_file = None

    def __init__(self, 
                 file_path: str | Path,
                 preload: bool=True,
                 verbose: Optional[Union[bool, str, int]]=None,
                 **kwargs) -> None:

        p_log_level = mne.set_log_level(verbose=verbose, return_old_level=True)

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if file_path.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_path, preload, **kwargs)
            else:
                raise ValueError(f"'{file_path}' is not a supported file")

            self.loaded_file = file_path

        except Exception as e:
            print(f"Error: {e}")

        mne.set_log_level(verbose=p_log_level, return_old_level=False)

    @staticmethod
    def read_bdf(file_path, preload, **kwargs):
        return mne.io.read_raw_bdf(file_path, preload=preload, **kwargs)

    def run(self):
        pass
