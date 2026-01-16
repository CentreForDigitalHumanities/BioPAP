"""Class for plotting"""

import mne
from biopap.modules.base_class import BaseClass

class Plot(BaseClass):

    # https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.plot

    def __init__(self,
                 raw,
                 title=None,
                 **kwargs):

        self.raw = raw
        self.processed = self.raw.copy()
        try:
            events = mne.find_events(self.processed)
            _ = self.processed.plot(
                events=events,
                title=title,
                block=True,
                show=True,
                **kwargs)
        except Exception as e:
            print(f"Error: {e}")
