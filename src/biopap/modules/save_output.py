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
    def __init__(self,
                 raw,
                 export_formats: Union[str, int, list[str]]=None,
                 output_file: str=None,
                 overwrite: bool=True,
                 silent: bool=False):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw
            # self.export_format = export_format
            # self.output_file = output_file
            # self.overwrite = overwrite

            e_frmts = ExportFormats(export_formats)

            #TODO implement overwrite

            # if self.export_format == 'fif':
            if e_frmts.is_selected(ExportFormats.FIF):
                self.save_fif(output_file, overwrite)
            # elif self.export_format == 'csv':
            if e_frmts.is_selected(ExportFormats.CSV):
                self.save_csv(output_file, overwrite)

    @classmethod
    def check_config(cls, cfg):
        if cfg and 'export_formats' in cfg:
            # will generate error when unknown format
            _ = ExportFormats(cfg['export_formats'])

    def save_fif(self, filename, overwrite):
        #TODO: address:
        #   This filename (/data/BioPAP/out/test_save_CBN1BD071212-Cropped.fif) does not conform to MNE naming conventions.
        #   All raw files should end with raw.fif, raw_sss.fif, raw_tsss.fif, _meg.fif, _eeg.fif, _ieeg.fif, raw.fif.gz, raw_sss.fif.gz, raw_tsss.fif.gz, _meg.fif.gz, _eeg.fif.gz or _ieeg.fif.gz
        target_file = Path(filename).with_suffix('.fif')
        self.processed.save(target_file, overwrite=overwrite)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")
            
    def save_csv(self, filename, overwrite):
        #TODO also export events/annotations?
        target_file = Path(filename).with_suffix('.csv')
        df = self.processed.to_data_frame()
        df.to_csv(target_file, index=False)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")