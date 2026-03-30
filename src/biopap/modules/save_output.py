import mne
from biopap.modules.base_class import BaseClass

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
                 export_format: str=None,
                 output_file: str=None,
                 overwrite: bool=True,
                 silent: bool=False):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw
            self.export_format = export_format
            self.output_file = output_file
            self.overwrite = overwrite

            if self.export_format == 'fif':
                self.save_fif(self.output_file, self.overwrite)
            elif self.export_format == 'csv':
                self.save_csv(self.output_file, self.overwrite)

    def save_fif(self, filename, overwrite):
        self.processed.save(filename, overwrite=overwrite)
            
    def save_csv(self, filename, overwrite):
        #TODO: save as csv
        pass