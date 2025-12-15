"""Class for automatic blink detection"""

import mne
from biopap.modules.base_class import BaseClass

class BlinkDetection(BaseClass):
    
    def __init__(self,
                 raw,
                 **kwargs):
        
        self.raw = raw

        try:

            f_kwargs = kwargs['find_eog_events'] if 'find_eog_events' in kwargs else {}
            a_kwargs = kwargs['Annotations'] if 'Annotations' in kwargs else {}

            eog_events = mne.preprocessing.find_eog_events(self.raw, **f_kwargs)
            onsets = eog_events[:, 0] / self.raw.info["sfreq"] - 0.25
            durations = [0.5] * len(eog_events)
            descriptions = ["bad blink"] * len(eog_events)
            blink_annot = mne.Annotations(
                onsets, 
                durations, 
                descriptions, 
                orig_time=self.raw.info["meas_date"],
                **a_kwargs
            )
            self.raw.set_annotations(blink_annot)

            self.processed = self.raw

        except Exception as e:
            print(f"Error: {e}")