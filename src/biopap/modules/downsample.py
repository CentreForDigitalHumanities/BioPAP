import mne
from biopap.modules.base_class import BaseClass

class Downsample(BaseClass):
    """
    Class for downsampling EEG data to a lower sampling rate.

    Applies MNE's built-in ``resample`` function to the input data.
    
    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    sfreq : int
        Target sampling rate in Hz.
    resample_events : bool, default True
        Whether to resample event onsets along with the data.
    **kwargs
        Additional keyword arguments passed to MNE's ``resample`` method.

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Output data after resampling.
    """
    def __init__(self,
                 raw,
                 sfreq,
                 resample_events=True,
                 **kwargs):

        # Downsampling
        # *** Change Sampling Rate / Resolution ***
        # Conversion is based on spline interpolation.
        # New Sampling Rate [Hz]: 500
        # New Sampling Interval [µS]: 2000
        # Data was filtered before downsampling with 225Hz, 24dB/oct.

        # https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.resample
        # https://mne.tools/stable/auto_tutorials/preprocessing/30_filtering_resampling.html#resampling

        # In MNE-Python, the resampling methods (raw.resample(), epochs.resample() 
        # and evoked.resample()) apply a low-pass filter to the signal to avoid
        # aliasing, so you don’t need to explicitly filter it yourself first. 

        self.processed = raw

        try:
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

            # RuntimeWarning: Resampling of the stim channels caused event information 
            # to become unreliable. Consider finding events on the original data and 
            # passing the event matrix as a parameter.

        except Exception as e:
            print(f"Error: {e}")
