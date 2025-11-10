"""Class for downsampling"""

import mne
from biopap.modules.base_class import BaseClass

class Downsample(BaseClass):

    def __init__(self,
                 raw,
                 sfreq,
                 resample_events=True):

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

        try:
            self.raw = raw

            if resample_events:
                events = mne.find_events(raw)
                self.processed, self.events = raw.resample(
                    sfreq=sfreq, 
                    events=events,
                    verbose=self.verbose)
            else:
                self.processed = raw.resample(
                    sfreq=sfreq, 
                    verbose=self.verbose)

            # RuntimeWarning: Resampling of the stim channels caused event information 
            # to become unreliable. Consider finding events on the original data and 
            # passing the event matrix as a parameter.

        except Exception as e:
            print(f"Error: {e}")
