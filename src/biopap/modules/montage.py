"""Class for creating montage"""

import mne
from biopap.modules.base_class import BaseClass

class Montage(BaseClass):

    # TODO:
    # what if montage is not a standard mne?
    # in our case biosemi64 doesn't have EXG.. channels, need to be set to misc type. So very specific to each research setup.
    # how can we make this as generic and user friendly as possible?

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
