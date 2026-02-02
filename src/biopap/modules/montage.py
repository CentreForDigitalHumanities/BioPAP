"""Class for creating montage"""

import mne
from biopap.modules.base_class import BaseClass

class Montage(BaseClass):

    def __init__(self,
                raw,
                mne_standard_montage,
                **kwargs):

        self.raw = raw

        try:

            montage = mne.channels.make_standard_montage(mne_standard_montage)
            self.raw.set_montage(montage)

            self.processed = self.raw

        except Exception as e:
            print(f"Error: {e}")
