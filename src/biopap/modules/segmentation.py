"""Class for segmentaion and artifact rejection (Epochs)"""

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

    # *** Artifact Rejection - Automatic Inspection ***
    # Used Channels: all

    # Check Gradient: # NOT IMPLEMENTED!
    # Maximal allowed voltage step: 50 µV/ms
    # Mark as Bad: Before Event: 200 ms After Event: 200 ms

    # Check Amplitude:
    # Minimal allowed amplitude: -75 µV
    # Maximal allowed amplitude: 75 µV
    # Mark as Bad: Before Event: 200 ms After Event: 200 ms

    # Check Low Activity:
    # Lowest allowed activity in intervals: 0.5 µV
    # Interval Length: 100 ms
    # Mark as Bad: Before Event: 200 ms After Event: 200 ms

    def __init__(self,
                 raw,
                 stim_channel,
                 start,
                 end,
                 baseline=None,
                 reject_tmin=None,
                 reject_tmax=None,
                 reject_criteria=None,
                 flat_criteria=None,
                 **kwargs):
        
        self.raw = raw
               
        reject_criteria = ({k: float(v) for k, v in reject_criteria.items()}
                           if reject_criteria else None)
        flat_criteria = ({k: float(v) for k, v in flat_criteria.items()}
                         if flat_criteria else None)
       
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
                                reject_tmin=reject_tmin,
                                reject_tmax=reject_tmax,
                                reject=reject_criteria,
                                flat=flat_criteria,
                                verbose=self.verbose,
                                **e_kwargs)
                                            
            epochs.drop_bad()

            self.processed = epochs
        except Exception as e:
            print(f"Error: {e}")
