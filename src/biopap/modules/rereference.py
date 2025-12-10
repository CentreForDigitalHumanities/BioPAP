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
                 auto_run: bool=True):
        """
            raw: Data with EEG channels re-referenced.
            ref_data: Array of reference data subtracted from EEG channels.
        """
        self.raw = raw
        self.ref_channels = ref_channels
        self.copy = copy
        if auto_run:
            self.run()

    def run(self):
        try:
            self.processed, self.ref_data = mne.set_eeg_reference(
                self.raw,
                ref_channels=self.ref_channels,
                copy=self.copy,
                verbose=self.verbose)
        except Exception as e:
            print(f"Error: {e}")
