import mne
from biopap.modules.base_class import BaseClass

class NotchFilter(BaseClass):
    """
    Class for applying for notch filtering.

    Filters the input data using a notch filter with MNE's ``notch_filter()`` method.

    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.notch_filter

    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    Fs: float
        Sampling rate in Hz. 
    freqs: float | array of float | None
        Frequencies to notch filter in Hz.
    method: {'fir', 'iir'}, default 'iir'
    **kwargs
        Additional keyword arguments passed to MNE's ``notch_filter()`` method.
        Example: {'trans_bandwidth': 2, 'fir_window': 'blackman'}

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Filtered output data.
    """

    def __init__(self,
                 raw,
                 freqs,
                 method='iir',
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            self.processed = raw.copy().notch_filter(
                freqs=freqs,
                method=method,
                verbose=self.verbose,
                **kwargs)
