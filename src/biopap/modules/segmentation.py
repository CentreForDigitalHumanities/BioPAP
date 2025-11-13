"""Class for sefgmentaion (Epochs)"""

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
                 raw):
        try:
            self.raw = raw

            # , stim_channel="STI 014"
            events = mne.find_events(raw, stim_channel="Status")
            epochs = mne.Epochs(raw, events, tmin=-0.2, tmax=1)

            print(events)
            print(epochs)

            self.processed = raw
        except Exception as e:
            print(f"Error: {e}")
