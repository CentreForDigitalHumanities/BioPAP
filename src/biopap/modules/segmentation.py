"""Class for segmentaion (Epochs)"""

import mne
from biopap.modules.base_class import BaseClass

class Segmentation(BaseClass):

    # Segmentation Critical words S1-6
    # *** Segmentation ***
    # Segmentation relative to reference marker positions
    # Reference markers:
    #     Stimulus    S  6
    #     Stimulus    S  5
    #     Stimulus    S  4
    #     Stimulus    S  3
    #     Stimulus    S  2
    #     Stimulus    S  1
    # Advanced Boolean Expression:    ---
    # Segment size and position relative to reference markers:
    # Start: -200.00 ms, End: 1000.00 ms, Length: 1200.00 ms
    # Allow overlapped segments? No
    # Skip bad intervals?        No
    # Data was cached to a temporary file.

    def __init__(self,
                 raw,
                 stim_channel,
                 start,
                 end,
                 auto_run: bool=True):
        
        self.raw = raw
        self.stim_channel = stim_channel
        self.start = start
        self.end = end
        if auto_run:
            self.run()
       
    def run(self):
        try:

            events = mne.find_events(self.raw, stim_channel=self.stim_channel, verbose='WARNING')
            epochs = mne.Epochs(self.raw, events, tmin=self.start, tmax=self.end, baseline=None)

            self.processed = self.raw
        except Exception as e:
            print(f"Error: {e}")
