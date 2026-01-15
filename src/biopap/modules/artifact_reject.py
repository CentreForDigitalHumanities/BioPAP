"""Class for EEG artifact rejection: bad channels per epoch"""

import mne
from biopap.modules.base_class import BaseClass

from mne_faster import (
    find_bad_channels,
    find_bad_channels_in_epochs,
    find_bad_components,
    find_bad_epochs,
)
import numpy as np

class ArtifactReject(BaseClass):
            
    # *** Artifact Rejection - Automatic Inspection ***
    # Used Channels: all

    # Check Gradient:
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
                **kwargs):
        
        if not isinstance(raw, mne.Epochs):
            raise TypeError(
                f"the input must be an mne.Epochs instance, "
                f"got {type(raw)} instead."
            )
    
        self.epochs = raw

        try:
            
            ## VERY SLOW CODE ##

            bad_channels_per_epoch = find_bad_channels_in_epochs(self.epochs, eeg_ref_corr=False)
            for i, b in enumerate(bad_channels_per_epoch):
                if len(b) > 0:
                    ep = self.epochs[i]
                    ep.info["bads"] = b

                    good_eeg = mne.pick_types(ep.info, meg=False, eeg=True)
                    all_eeg = mne.pick_types(ep.info, meg=False, eeg=True, exclude=[])
                    bad_channels_idx = np.setdiff1d(all_eeg, good_eeg)

                    self.epochs._data[i, bad_channels_idx, :] = np.nan
                    print(f'data epoch {i}', self.epochs._data[i, :, :])

                    print("valid_channels_per_epoch = ", np.sum(~np.all(np.isnan(self.epochs._data[i]), axis=1)))
       
            self.processed = self.epochs
        except Exception as e:
            print(f"Error: {e}")