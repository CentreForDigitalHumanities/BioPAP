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

    intmd_postfix = '_partial'

    def __init__(self,
                 raw,
                 export_formats: Union[str, int, list[str]]=None,
                 output_file: str=None,
                 overwrite: bool=True,
                 steps_completed: list[PipelineStep]=[],
                 intermediate: Union[str, int, bool]=True,
                 silent: bool=False):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw
            e_frmts = ExportFormats(export_formats)

            if isinstance(intermediate, bool) and not intermediate:
                intmd_postfix = None
            elif isinstance(intermediate, bool):
                intmd_postfix = self.intmd_postfix
            elif isinstance(intermediate, (str, int)):
                intmd_postfix = ''.join(c for c in str(intermediate) 
                                        if c.isalpha() or c.isdigit() or c in [' ','_','-']
                                       ).rstrip().replace(' ', '_')[:25]
            else:
                raise ValueError(f'intermediate must be bool, int or str (got {type(intermediate)})')

            saved_files = []

            if e_frmts.is_selected(ExportFormats.FIF):
                saved_files.append(self.save_fif(
                    filename=output_file,
                    overwrite=overwrite,
                    save_postfix=intmd_postfix))

            if e_frmts.is_selected(ExportFormats.CSV):
                saved_files.append(self.save_csv(
                    filename=output_file,
                    overwrite=overwrite,
                    save_postfix=intmd_postfix))

            self.save_steps_completed(
                steps_completed=steps_completed,
                saved_files=saved_files)

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
    def save_steps_completed(steps_completed, saved_files):
        if len(saved_files)==0:
            return
        f_new = Path(saved_files[0]).with_suffix('.txt')
        f_new = get_new_filename(
            filename=f_new.name,
            save_folder=f_new.parent,
            save_overwrite=True)

        with open(f_new, 'w', encoding='utf-8') as f:
            f.write("# Steps completed:\n")
            for step in steps_completed:
                f.write(str(step) + '\n')
            f.write("\n")
            f.write(f"# Output ({datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}):\n")
            for saved_file in saved_files:
                f.write(str(saved_file) + '\n')
