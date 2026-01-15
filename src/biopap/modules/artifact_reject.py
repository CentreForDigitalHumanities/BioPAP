"""Class for EEG artifact rejection: bad channels per epoch"""

import mne
from biopap.modules.base_class import BaseClass
import numpy as np

class ArtifactReject(BaseClass):
            
    # *** Artifact Rejection - Automatic Inspection ***
    # Used Channels: all

    # Check Gradient:
    # Maximal allowed voltage step: 50 µV/ms
    # Mark as Bad: Before Event: 200 ms After Event: 200 ms

    # Check Amplitude: VRAAG: Bedoel je hier Peak-to-peak (dus 150) of signal boven 75 of onder -75 uV.
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
            
            # epochs_before = self.epochs.copy()
            # epochs_before.set_eeg_reference("average")
            # evoked_before = epochs_before.average()

            ## VERY SLOW CODE ##

            bad_channels_per_epoch = find_bad_channels_in_epochs(self.epochs)
            for i, b in enumerate(bad_channels_per_epoch):
                if i == 20: 
                    break
                if len(b) > 0:
                    ep = self.epochs[i]
                    ep.info["bads"] = b

                    good_eeg = mne.pick_types(ep.info, meg=False, eeg=True)
                    all_eeg = mne.pick_types(ep.info, meg=False, eeg=True, exclude=[])
                    bad_channels_idx = np.setdiff1d(all_eeg, good_eeg)

                    self.epochs._data[i, bad_channels_idx, :] = np.nan
                    # print(f'data epoch {i}', self.epochs._data[i, :, :])

                    print("valid_channels_per_epoch = ", np.sum(~np.all(np.isnan(self.epochs._data[i]), axis=1)))
            
            
            # self.epochs.set_eeg_reference("average")
            # evoked_after = self.epochs.average()

            # evoked_before.plot()
            # evoked_after.plot()

            self.processed = self.epochs
        except Exception as e:
            print(f"Error: {e}")

def find_bad_channels_in_epochs(
    epochs,
    picks=None
    ):

    # Thresholds
    max_gradient_uv_per_ms=50 * 1e-6  # data is in Volts?
    max_amplitude_uv=75 * 1e-6  # data is in Volts?
    # min_activity_uv=0.5 * 1e-6 
    # activity_window_ms=100

    # Thresholds in relation to time
    sfreq = epochs.info["sfreq"] # sampling frequency per second (=500)
    grad_thresh = max_gradient_uv_per_ms * (1000 / sfreq)
    # activity_win = int(activity_window_ms * sfreq / 1000)

    if picks is None:
        picks = mne.pick_types(epochs.info, meg=False, eeg=True, exclude="bads")
 
    ch_names = np.array(epochs.ch_names)[picks]
    data = epochs.get_data(copy=False)[:, picks]

    bads_per_epoch = []

    for ep_data in data:
        bad_mask = np.zeros(ep_data.shape[0], dtype=bool)

        # 1. Gradient check
        gradient = np.abs(np.diff(ep_data, axis=1))
        bad_mask |= np.max(gradient, axis=1) > grad_thresh

        # 2. Amplitude check
        bad_mask |= np.max(np.abs(ep_data), axis=1) > max_amplitude_uv

        # 3. Low-activity check
        # TO DO

        bads_per_epoch.append(list(ch_names[bad_mask]))

    return bads_per_epoch