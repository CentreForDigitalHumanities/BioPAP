import mne
import time
from pathlib import Path
from datetime import datetime
from typing import Union
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import (OptionsBaseClass, get_new_filename)
from biopap.modules.pipeline_step import PipelineStep

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
                 export_formats: Union[str, int, list[str]],
                 output_file: Union[str, Path],
                 overwrite: bool=True,
                 postfix: Union[str, None]=None,
                 _steps_completed: list[PipelineStep]=[],
                 _intermediate: bool=True,
                 silent: bool=False):

        self._saved_files = []

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            self.processed = raw

            f_postfix = postfix if postfix else ''
            if _intermediate:
                f_postfix = f"{f_postfix}_PARTIAL"

            e_frmts = ExportFormats(export_formats)

            if e_frmts.is_selected(ExportFormats.FIF):
                self._saved_files.append(self.save_fif(
                    filename=output_file,
                    overwrite=overwrite,
                    save_postfix=f_postfix))

            if e_frmts.is_selected(ExportFormats.CSV):
                self._saved_files.append(self.save_csv(
                    filename=output_file,
                    overwrite=overwrite,
                    save_postfix=f_postfix))

            self.save__steps_completed(
                _steps_completed=_steps_completed,
                saved_files=self._saved_files)

    @property
    def saved_files(self):
        return self._saved_files

    @classmethod
    def check_config(cls, cfg):
        if 'export_formats' in cfg:
            # will generate error when unknown format
            _ = ExportFormats(cfg['export_formats'])

    def save_fif(self, filename, overwrite, save_postfix=None):
        f_new = Path(filename).with_suffix('.fif')
        f_new = get_new_filename(
            filename=f_new.name,
            save_folder=f_new.parent,
            save_postfix=save_postfix,
            save_overwrite=overwrite)

        self.processed.save(f_new, overwrite=overwrite)
        print(f"wrote '{f_new}' ({f_new.stat().st_size:,})")
        return f_new
            
    def save_csv(self, filename, overwrite, save_postfix=None):
        f_new = Path(filename).with_suffix('.csv')
        f_new = get_new_filename(
            filename=f_new.name,
            save_folder=f_new.parent,
            save_postfix=save_postfix,
            save_overwrite=overwrite)

        df = self.processed.to_data_frame()
        df.to_csv(f_new, index=False)
        print(f"wrote '{f_new}' ({f_new.stat().st_size:,})")
        return f_new

    @staticmethod
    def save__steps_completed(_steps_completed, saved_files):
        if len(saved_files)==0:
            return

        f_tmp = Path(saved_files[0])
        f_new = f_tmp.parent / Path(f"{f_tmp.stem}__PIPELINE_PROGRESS").with_suffix('.txt')
        f_new = get_new_filename(
            filename=f_new.name,
            save_folder=f_new.parent,
            save_overwrite=True)

        with open(f_new, 'w', encoding='utf-8') as f:
            f.write("# Steps completed:\n")
            for step in _steps_completed:
                f.write(f"{str(step)}\n")
            f.write("\n")
            f.write(f"# Output ({datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}):\n")
            for saved_file in saved_files:
                f.write(f"{str(saved_file)}\n")
