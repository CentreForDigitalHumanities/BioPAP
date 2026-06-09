import mne
from pathlib import Path
from typing import Union
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import OptionsBaseClass

class ExportFormats(OptionsBaseClass):

    FIF = 1
    CSV = 2

    def __init__(self, sel_options=0):
        super().__init__(sel_options)

class SaveOutput(BaseClass):
    """
    Class for saving the output data.

    mne-functions used:
    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.save
    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.to_data_frame
    https://mne.tools/stable/generated/mne.Epochs.html#mne.Epochs.to_data_frame

    Parameters
    ----------
    raw : mne.io.Raw | mne.Epochs
        Input data to be saved.
    export_format : 'fif' | 'csv' | None
        Format to save the data. If None, the data is not saved.
    output_file : str | None
        Path to the output file. If None, the data is not saved.
    overwrite : bool, default True
        Whether to overwrite existing files with the same name.
    silent : bool, default False
        If True, suppresses output messages.

    Attributes
    ----------
    processed : mne.io.Raw | mne.Epochs
        Output data (same as input data; this class is for saving, not processing).
    """

    alters_data = False

    def __init__(self,
                 raw,
                 export_formats: Union[str, int, list[str]]=None,
                 output_file: str=None,
                 overwrite: bool=True,
                 silent: bool=False):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw
            e_frmts = ExportFormats(export_formats)

            if e_frmts.is_selected(ExportFormats.FIF):
                self.save_fif(output_file, overwrite)
            if e_frmts.is_selected(ExportFormats.CSV):
                self.save_csv(output_file, overwrite)

    @classmethod
    def check_config(cls, cfg):
        if 'export_formats' in cfg:
            # will generate error when unknown format
            _ = ExportFormats(cfg['export_formats'])

    def save_fif(self, filename, overwrite):
        #TODO implement overwrite
        target_file = Path(filename).with_suffix('.fif')
        self.processed.save(target_file, overwrite=overwrite)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")
            
    def save_csv(self, filename, overwrite):
        #TODO implement overwrite
        target_file = Path(filename).with_suffix('.csv')
        df = self.processed.to_data_frame()
        df.to_csv(target_file, index=False)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")