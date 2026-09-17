import mne
from biopap.modules.base_class import BaseClass

class Downsample(BaseClass):
    """
    Class for downsampling EEG data to a lower sampling rate.

    Applies MNE's built-in ``resample`` function to the input data.

    MNE-function used:
    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.resample
    
    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    sfreq : int
        Target sampling rate in Hz.
    resample_events : bool, default True
        Whether to resample event onsets along with the data.
    **kwargs
        Additional keyword arguments passed to MNE's ``resample`` method. Example:
        {'n_jobs': 'cuda'}

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Output data after resampling.
    """
    def __init__(self,
                 raw,
                 sfreq,
                 resample_events=True,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            self.processed = raw

            if resample_events and isinstance(self.raw, mne.io.BaseRaw):
                events = mne.find_events(self.raw)
                self.processed, self.events = self.raw.resample(** {
                    'sfreq': sfreq, 
                    'events': events,
                    'verbose': self.verbose
                    } | kwargs)
            else:
                self.processed.resample(** {
                    'sfreq': sfreq, 
                    'verbose': self.verbose
                    } | kwargs)


