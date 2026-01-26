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
                mode='interpolation',
                max_gradient_uv=50,
                max_amplitude_uv=75,
                **kwargs):
        
        if not isinstance(raw, mne.Epochs):
            raise TypeError(
                f"the input must be an mne.Epochs instance, "
                f"got {type(raw)} instead."
            )
    
        self.epochs = raw
        self.mode = mode
        self.max_gradient_uv = max_gradient_uv
        self.max_amplitude_uv = max_amplitude_uv

        try:

            bad_mask, picks = find_bad_channels(
                self.epochs,
                self.max_gradient_uv,
                self.max_amplitude_uv,
            )

            if mode == "nan_replacement":
                apply_nan_replacement(bad_mask, picks)

            elif mode == "interpolation":
                apply_interpolation(bad_mask, picks)

            else:
                raise ValueError(
                    f"Unknown mode '{mode}'. "
                    "Use 'nan_replacement' or 'interpolation'."
                )
            
            self.processed = self.epochs

        except Exception as e:
            print(f"Error: {e}")

# TODO: Rewrite this function   
@staticmethod
def find_bad_channels(
     epochs,
     max_gradient_uv,
     max_amplitude_uv
):
          
    # Thresholds
    max_gradient_uv=50 * 1e-6  # data is in Volts?
    max_amplitude_uv=75 * 1e-6  # data is in Volts?
    # min_activity_uv=0.5 * 1e-6 
    # activity_window_ms=100

    # Thresholds in relation to time
    sfreq = epochs.info["sfreq"] # sampling frequency per second (=500)
    grad_thresh = max_gradient_uv * (1000 / sfreq)
    # activity_win = int(activity_window_ms * sfreq / 1000)

    # if picks is None:
    #     picks = mne.pick_types(epochs.info, meg=False, eeg=True, exclude="bads")
 
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


def apply_nan_replacement(self, bad_mask, picks):
    """
    Replace bad channels with NaNs per epoch
    """
    data = self.epochs._data

    bad_mask_3d = bad_mask[:, :, np.newaxis]

    data[:, picks, :] = np.where(
        bad_mask_3d,
        np.nan,
        data[:, picks, :]
    )


def apply_interpolation(self, bad_mask, picks):
    """
    Interpolate bad channels per epoch
    """
    ch_names = np.array(self.epochs.ch_names)[picks]

    for epoch_i, bad_ch in enumerate(bad_mask):
        if not np.any(bad_ch):
            continue

        ep = self.epochs[epoch_i]
        ep.info["bads"] = list(ch_names[bad_ch])
        ep.interpolate_bads(reset_bads=False)  # reset_bads = remove the bads from info          
