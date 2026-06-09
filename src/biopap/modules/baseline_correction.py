import mne
from biopap.modules.base_class import BaseClass

class BaselineCorrection(BaseClass):
    """
    Class for applying baseline correction.

    Performs baseline correction on the input data using MNE's
    built-in ``apply_baseline()`` method (for Epochs).

    https://mne.tools/stable/generated/mne.Epochs.html#mne.Epochs.apply_baseline

    Parameters
    ----------
    raw : mne.Epochs
        Input data.
    baseline: tuple of length 2 | None
        The time interval (start, stop) in seconds to use for
        baseline correction. Use None to skip baseline correction.

    Attributes
    ----------
    processed : mne.Epochs
        Baseline corrected output data.
    """

    def __init__(self,
                 raw,
                 baseline,
                 silent: bool=False,
                 ):

        super().__init__(silent)

        self.set_mne_config({**locals()})

        with self.capture_stdout as self.stdout:
                  
            self.processed = raw

            if isinstance(self.processed, mne.Epochs):
                self.processed = self.processed.apply_baseline(baseline)
            else:
                raise TypeError(f"Baseline correction is only applicable to mne.Epochs objects (got {type(self.processed)})")
