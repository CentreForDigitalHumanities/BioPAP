"""Class for loading files"""

import mne
import yaml
from pathlib import Path
from typing import Union, Optional
from biopap.modules.base_class import BaseClass


class LoadData(BaseClass):
    """
    Class for loading BDF data from file.

    mne-functions used:
    https://mne.tools/stable/generated/mne.io.read_raw_bdf.html
    https://mne.tools/stable/generated/mne.read_epochs.html
    https://mne.tools/stable/generated/mne.io.read_raw_fif.html

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
        ``mne.io.read_raw_bdf()``  or ``mne.io.read_raw_fif()`` method.

    Attributes
    ----------
    raw : mne.io.Raw
        Loaded raw data.
    """

    loaded_file = None
    alters_data = False

    def __init__(self, 
                 file_path: str | Path,
                 preload: bool=True,
                 verbose: Optional[Union[bool, str, int]]=None,
                 silent: bool=False,
                 **kwargs
                 ) -> None:

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            file_path = Path(file_path)

            if not file_path.exists():
                raise ValueError(f"File '{file_path}' does not exist")

            if file_path.suffix.lower()=='.bdf':
                self.raw = self.read_bdf(file_path, preload, **kwargs)
            elif file_path.suffix.lower()=='.fif':
                self.raw = self.read_fif(file_path, preload, **kwargs)
            else:
                raise ValueError(f"'{file_path}' is not a supported file")

            self.loaded_file = file_path

    @staticmethod
    def read_bdf(file_path, preload, **kwargs):
        raw_bdf = mne.io.read_raw_bdf(file_path, preload=preload, **kwargs)
        return raw_bdf

    @staticmethod
    def read_fif(file_path, preload, **kwargs):
        try:
            raw_fif = mne.read_epochs(file_path, preload=preload)
        except ValueError as e:
            if str(e).strip().lower() == "could not find event data":
                raw_fif = mne.io.read_raw_fif(file_path, preload=preload, **kwargs)
            else:
                raise e

        return raw_fif
