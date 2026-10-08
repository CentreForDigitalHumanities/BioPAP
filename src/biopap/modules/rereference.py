import mne
from biopap.modules.base_class import BaseClass

class Rereference(BaseClass):
    """
    Class for rereferencing EEG data.

    Applies MNE's ``set_eeg_reference()`` function to the input data.

    MNE-function used: [mne.set_eeg_reference](https://mne.tools/stable/generated/mne.set_eeg_reference.html#mne.set_eeg_reference)

    Parameters
    ----------
    raw : mne.io.Raw | mne.Epochs
        Input data.
    ref_channels : list of str
        Reference channel names to subtract from the EEG channels.
    copy : bool, default False
        If True, returns a copy of the data; otherwise modifies in place.
    **kwargs
        Additional keyword arguments passed to MNE's
        ``set_eeg_reference()`` function.

    Attributes
    ----------
    processed : mne.io.Raw | mne.Epochs
        Output data after rereferencing.
    """

    def __init__(self,
                 raw,
                 ref_channels=['EXG1', 'EXG2'],
                 copy=False,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            self.processed = raw

            self.processed, self.ref_data = mne.set_eeg_reference(
                self.processed,
                ref_channels=ref_channels,
                copy=copy,
                verbose=self.verbose,
                **kwargs)
