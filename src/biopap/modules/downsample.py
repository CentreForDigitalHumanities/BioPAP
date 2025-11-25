"""Class for downsampling"""

import mne
from biopap.modules.base_class import BaseClass

class Downsample(BaseClass):

    def __init__(self,
                 raw,
                 sfreq,
                 resample_events=True,
                 auto_run: bool=True):

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
        self.raw = raw
        self.sfreq = sfreq
        self.resample_events = resample_events
        if auto_run:
            self.run()

    def run(self):
        try:
            if self.resample_events:
                events = mne.find_events(self.raw)
                self.processed, self.events = self.raw.resample(
                    sfreq=self.sfreq, 
                    events=events,
                    verbose=self.verbose)
            else:
                self.processed = self.raw.resample(
                    sfreq=self.sfreq, 
                    verbose=self.verbose)

            # RuntimeWarning: Resampling of the stim channels caused event information 
            # to become unreliable. Consider finding events on the original data and 
            # passing the event matrix as a parameter.

        except Exception as e:
            print(f"Error: {e}")
