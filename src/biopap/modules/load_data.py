"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Union, Optional
from biopap.modules.base_class import BaseClass


class LoadData(BaseClass):
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
                 silent: bool=False,
                 **kwargs
                 ) -> None:

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.preload = preload

            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if file_path.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_path, **kwargs)
            else:
                raise ValueError(f"'{file_path}' is not a supported file")

            self.loaded_file = file_path


    def read_bdf(self, file_path, **kwargs):
        raw_bdf = mne.io.read_raw_bdf(file_path, preload=self.preload, **kwargs)
        return raw_bdf
