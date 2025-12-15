"""Class for rereferencing"""

import mne
from biopap.modules.base_class import BaseClass

class Rereference(BaseClass):

    # https://mne.tools/stable/generated/mne.set_eeg_reference.html#mne.set_eeg_reference
    # raw: Array of reference data subtracted from EEG channels.
    # ref_data: Array of reference data subtracted from EEG channels.
    #TODO: 'Channels to which the new reference applies to: ': cannot set explicitly (but it's all of them, right?)

    def __init__(self,
                 raw,
                 ref_channels=['EXG1', 'EXG2'],
                 copy=False,
                 **kwargs):
        """
            raw: Data with EEG channels re-referenced.
            ref_data: Array of reference data subtracted from EEG channels.
        """
        self.raw = raw

        try:
            self.processed, self.ref_data = mne.set_eeg_reference(
                self.raw,
                ref_channels=ref_channels,
                copy=copy,
                verbose=self.verbose,
                **kwargs)
        except Exception as e:
            print(f"Error: {e}")
