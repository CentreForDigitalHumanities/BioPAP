"""Class for automatic blink detection"""

import mne
from biopap.modules.base_class import BaseClass

class BlinkDetection(BaseClass):
    
    def __init__(self,
                 raw,
                 auto_run: bool=True):
        
        self.raw = raw
        if auto_run:
            self.run()


    def run(self):
        try:

            eog_events = mne.preprocessing.find_eog_events(self.raw)
            onsets = eog_events[:, 0] / self.raw.info["sfreq"] - 0.25
            durations = [0.5] * len(eog_events)
            descriptions = ["bad blink"] * len(eog_events)
            blink_annot = mne.Annotations(
                onsets, durations, descriptions, orig_time=self.raw.info["meas_date"]
            )
            self.raw.set_annotations(blink_annot)

            self.processed = self.raw

        except Exception as e:
            print(f"Error: {e}")