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

    # *** Baseline Correction ***
    # Begin: -200.00 ms End: 0.00 ms

    def __init__(self,
                 raw,
                 stim_channel,
                 start,
                 end,
                 baseline=None,
                 **kwargs):
        
        self.raw = raw

        try:

            f_kwargs = kwargs['find_events'] if 'find_events' in kwargs else {}
            e_kwargs = kwargs['Epochs'] if 'Epochs' in kwargs else {}

            events = mne.find_events(self.raw,
                                     stim_channel=stim_channel,
                                     verbose=self.verbose,
                                     **f_kwargs)
            epochs = mne.Epochs(self.raw, 
                                events, 
                                tmin=start, 
                                tmax=end, 
                                baseline=baseline,
                                preload=True,
                                **e_kwargs)
            
            self.processed = epochs
        except Exception as e:
            print(f"Error: {e}")
