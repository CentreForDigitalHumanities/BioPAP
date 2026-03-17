import mne
from biopap.modules.base_class import BaseClass
import numpy as np

class ArtifactReject(BaseClass):
    """
    Class for rejecting or correcting bad channels in EEG epochs.

    Identifies bad channels per epoch and either interpolates them
    using MNE's built-in functionality, or replaces them with NaNs.

    Parameters
    ----------
    raw : mne.Epochs
        Input data.
    mode : {'interpolation', 'nan_replacement'}
        Method for dealing with bad channels.
    max_gradient_uv : int
        Maximal allowed voltage step in µV/ms.
    max_amplitude_uv : int
        Maximal allowed amplitude in µV.
    min_activity_uv : int
        Lowest allowed activity in intervals in µV.
    interval_ms: int
        Interval length in milliseconds for checking activity.
    **kwargs
        Additional keyword arguments passed to the underlying
        ``Epochs.pick_types()`` and ``Epochs.interpolate_bads()`` methods.

    Attributes
    ----------
    processed : mne.Epochs
        Output data.
    """
    def __init__(self,
                raw,
                logger,
                mode='interpolation',
                max_gradient_uv=50,
                max_amplitude_uv=75,
                min_activity_uv=0.5,
                interval_ms=100,
                **kwargs):
          
        self.processed = raw

        try:

            if not isinstance(self.processed, mne.Epochs):
                raise TypeError(
                    "the input must be an mne.Epochs instance, "
                    f"got {type(self.processed)} instead."
                )
            
            p_kwargs = kwargs['pick_types'] if 'pick_types' in kwargs else {}
            i_kwargs = kwargs['interpolate_bads'] if 'interpolate_bads' in kwargs else {}

            bad_mask, picks = find_bad_channels(
                self.processed,
                max_gradient_uv,
                max_amplitude_uv,
                min_activity_uv,
                interval_ms,
                **p_kwargs
            )

            counts = bad_mask.sum(axis=0)

            # TODO (EXTRA): create a plot out of this
            for ch, n in zip(self.processed.ch_names, counts):
                print(f"{ch}: bad in {n} epochs")

            if mode == "nan_replacement":
                apply_nan_replacement(self.processed, bad_mask, picks)

            elif mode == "interpolation":
                apply_interpolation(self.processed, bad_mask, picks, **i_kwargs)

            else:
                raise ValueError(
                    f"Unknown mode '{mode}'. "
                    "Use 'nan_replacement' or 'interpolation'."
                )
            
        except Exception as e:
            logger.error(str(e))
            self.exit_code = 1

def find_bad_channels(
    epochs,
    max_gradient_uv_ms,
    max_amplitude_uv,
    min_activity_uv,
    interval_ms,
    **kwargs):
    """
    Determine bad channels based on criteria for gradient, amplitude, and activity
    """
    sfreq = epochs.info["sfreq"]

    picks = mne.pick_types(epochs.info, meg=False, eeg=True, exclude="bads", **kwargs)

    epoch_data = epochs.get_data(copy=False)[:, picks, :]  # (E, C, T)

    # 1. Gradient check (sample-to-sample)
    threshold_v_s = max_gradient_uv_ms * 1e-6 / 1e-3   # µV/ms → V/s
    threshold_v_sample = threshold_v_s / sfreq        # V/s → V/sample

    diff = np.diff(epoch_data, axis=2)                # (E, C, T-1)
    grad_bad = np.any(np.abs(diff) > threshold_v_sample, axis=2)

    # 2. Amplitude check
    amp_thresh = max_amplitude_uv * 1e-6               # µV → V
    amp_bad = np.max(np.abs(epoch_data), axis=2) > amp_thresh

    # 3. Low activity check
    min_activity_v = min_activity_uv * 1e-6            # 0.5 µV → V 
    interval_samples = (interval_ms / 1000) * sfreq    # samples in interval = seconds × (samples/second)

    low_activity = np.abs(epoch_data) < min_activity_v  # (E, C, T)

    # flatten epochs and channels
    E, C, T = epoch_data.shape
    flat = low_activity.reshape(-1, T)          # (E*C, T)

    # Adjusted code from https://stackoverflow.com/q/69886314/ 
    i = np.arange(T) + 1 
    last_break = np.maximum.accumulate((~flat) * i, axis=1)
    run_lengths = i - last_break
    low_activity_bad_flat = np.any(run_lengths >= interval_samples, axis=1)

    # reshape back to (E, C)
    low_act_bad = low_activity_bad_flat.reshape(E, C)

    # Combine criteria
    bad_mask = grad_bad | amp_bad | low_act_bad        # (E, C)

    return bad_mask, picks


def apply_nan_replacement(epochs, bad_mask, picks):
    """
    Replace bad channels with NaNs per epoch
    """
    data = epochs._data

    bad_mask_3d = bad_mask[:, :, np.newaxis]

    data[:, picks, :] = np.where(
        bad_mask_3d,
        np.nan,
        data[:, picks, :]
    )


def apply_interpolation(epochs, bad_mask, picks, **i_kwargs):
    """
    Interpolate bad channels per epoch
    """
    ch_names = np.array(epochs.ch_names)[picks]

    for epoch_i, bad_ch in enumerate(bad_mask):
        if not np.any(bad_ch):
            continue

        ep = epochs[epoch_i]
        ep.info["bads"] = list(ch_names[bad_ch])
        ep.interpolate_bads(reset_bads=False, **i_kwargs)  # reset_bads = remove the bads from info          
