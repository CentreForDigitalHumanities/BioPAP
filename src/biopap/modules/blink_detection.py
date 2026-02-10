"""Class for automatic blink detection"""

import mne
from biopap.modules.base_class import BaseClass

class BlinkDetection(BaseClass):
    
    def __init__(self,
                 raw,
                 **kwargs):
        
        self.processed = raw

        try:

            f_kwargs = kwargs['find_eog_events'] if 'find_eog_events' in kwargs else {}
            a_kwargs = kwargs['Annotations'] if 'Annotations' in kwargs else {}

            eog_events = mne.preprocessing.find_eog_events(self.processed, **f_kwargs)
            onsets = eog_events[:, 0] / self.processed.info["sfreq"] - 0.25
            durations = [0.5] * len(eog_events)
            descriptions = ["bad blink"] * len(eog_events)
            blink_annot = mne.Annotations(
                onsets, 
                durations, 
                descriptions, 
                orig_time=self.processed.info["meas_date"],
                **a_kwargs
            )
            self.processed.set_annotations(blink_annot)

        except Exception as e:
            print(f"Error: {e}")