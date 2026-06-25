import mne
from biopap.modules.base_class import BaseClass
import pandas as pd

class Metadata(BaseClass):
    """

    """

    def __init__(self,
                 raw,
                 epochs_metadata,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:
            
            self.processed = raw
           
            if isinstance(self.processed, mne.Epochs):
                new_metadata = pd.read_csv(epochs_metadata)
                self.processed.metadata = new_metadata
                self.processed.metadata

# How to handle metadata preprocessing like Maike's code. Very specific for her data.
# Implement argument to include a python script that does this? 
# But creating such a script needs some inspection of the data, do transformations, see if it is correct. 
# Then it would not make sense to include it in a module, and should be done after preprocessing pipeline.

