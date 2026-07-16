import mne
from biopap.modules.base_class import BaseClass
import pandas as pd

class Metadata(BaseClass):
    """
    Class for adding metadata to mne.Epochs objects.

    Adds metadata to the input data using MNE's built-in ``metadata`` attribute (for Epochs).

    Parameters
    ----------
    raw : mne.Epochs
        Input data.
    epochs_metadata: str
        Path to a CSV file containing the metadata for the epochs. Each row corresponds to one epoch.

    Attributes
    ----------
    processed : mne.Epochs
        Output data with added metadata.
    """

    def __init__(self,
                 raw: mne.Epochs,
                 epochs_metadata: str,
                 silent: bool=False):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:
            
            self.processed = raw
            
            if isinstance(self.processed, mne.Epochs):
                new_metadata = pd.read_csv(epochs_metadata)
                self.processed.metadata = new_metadata
                self.processed.metadata
            else:
                raise TypeError(f"Metadata can only be added to mne.Epochs objects (got {type(self.processed)})")

