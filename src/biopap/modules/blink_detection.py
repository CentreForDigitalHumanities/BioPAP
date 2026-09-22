import mne
from biopap.modules.base_class import BaseClass

class BlinkDetection(BaseClass):
    """
    Class for automatic blink detection.

    Detects blinks using MNE's ``find_eog_events()`` function and
    generates annotations for the input data.

    MNE-functions used: [mne.preprocessing.find_eog_events](https://mne.tools/stable/generated/mne.preprocessing.find_eog_events.html), [mne.Annotations](https://mne.tools/stable/generated/mne.Annotations.html)

    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    **kwargs
        Additional keyword arguments passed to the underlying
        ``find_eog_events()`` and ``Annotations()`` methods.
        Pass arguments for the different functions by using a dictionary with
        `find_eog_events`, and `Annotations` as keys. Example:
        {'find_eog_events' : {'filter_length': '5s'}, 'Annotations': {'duration': 1.5}}


    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Output data with annotations.

    Notes
    -----
    The implementation is based on the MNE tutorial:
    https://mne.tools/stable/auto_tutorials/preprocessing/20_rejecting_bad_data.html#generating-annotations-programmatically
    """
    def __init__(self,
                 raw,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:
        
            self.processed = raw

            f_kwargs = kwargs['find_eog_events'] if 'find_eog_events' in kwargs else {}
            a_kwargs = kwargs['Annotations'] if 'Annotations' in kwargs else {}

            eog_events = mne.preprocessing.find_eog_events(self.processed, **f_kwargs)
            onsets = eog_events[:, 0] / self.processed.info["sfreq"] - 0.25
            durations = [0.5] * len(eog_events)
            descriptions = ["bad blink"] * len(eog_events)
            blink_annot = mne.Annotations(
                onsets, 
                durations, 
                descriptions, 
                orig_time=self.processed.info["meas_date"],
                **a_kwargs
            )
            self.processed.set_annotations(blink_annot)
