import mne
from pathlib import Path
from typing import Union
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import OptionsBaseClass, get_new_filename

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
        Program automatically adds appropriate suffix.
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
                 export_formats: Union[str, int, list[str]],
                 output_file: str,
                 subject_id: str,
                 overwrite: bool=True,
                 silent: bool=False):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw

            e_frmts = ExportFormats(export_formats)

            if e_frmts.is_selected(ExportFormats.FIF):
                self.save_fif(
                    filename=output_file.format(subject_id=subject_id),
                    overwrite=overwrite)

            if e_frmts.is_selected(ExportFormats.CSV):
                self.save_csv(
                    filename=output_file.format(subject_id=subject_id),
                    overwrite=overwrite)

    @classmethod
    def check_config(cls, cfg):
        if cfg and 'export_formats' in cfg:
            # will generate error when unknown format
            _ = ExportFormats(cfg['export_formats'])
        else:
            raise ValueError("'export_formats' missing")

        if not (cfg and 'output_file' in cfg):
            raise ValueError("'output_file' missing")


    def save_fif(self, filename, overwrite):
        target_file = get_new_filename(
            filename=Path(filename).with_suffix('.fif').name,
            save_folder=Path(filename).parent,
            save_overwrite=overwrite)

        self.processed.save(target_file, overwrite=overwrite)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")
            
    def save_csv(self, filename, overwrite):
        target_file = get_new_filename(
            filename=Path(filename).with_suffix('.csv').name,
            save_folder=Path(filename).parent,
            save_overwrite=overwrite)

        df = self.processed.to_data_frame()
        df.to_csv(target_file, index=False)
        print(f"wrote '{target_file}' ({target_file.stat().st_size:,})")