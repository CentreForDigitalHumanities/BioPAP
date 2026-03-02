import mne
from biopap.modules.base_class import BaseClass

class BaselineCorrection(BaseClass):
    """
    Class for applying baseline correction.

    Performs baseline correction on the input data using MNE's
    built-in ``apply_baseline()`` method (for Raw or Epochs).

    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    baseline: tuple of length 2 | None
        The time interval (start, stop) in seconds to use for
        baseline correction. Use None to skip baseline correction.

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Baseline corrected output data.
    """

    def __init__(self,
                 raw,
                 baseline):
        
        self.processed = raw
                     
        try:
        
            self.processed = self.processed.apply_baseline(baseline)
                                            
        except Exception as e:
            print(f"Error: {e}")
