import mne
from biopap.modules.base_class import BaseClass

class Rereference(BaseClass):
    """
    Class for rereferencing EEG data.

    Applies MNE's ``set_eeg_reference()`` function to the input data.

    https://mne.tools/stable/generated/mne.set_eeg_reference.html#mne.set_eeg_reference

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

    # https://mne.tools/stable/generated/mne.set_eeg_reference.html#mne.set_eeg_reference
    # raw: Array of reference data subtracted from EEG channels.
    # ref_data: Array of reference data subtracted from EEG channels.
    #TODO: 'Channels to which the new reference applies to: ': cannot set explicitly (but it's all of them, right?)

    def __init__(self,
                 raw,
                 ref_channels=['EXG1', 'EXG2'],
                 copy=False,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw

            self.processed, self.ref_data = mne.set_eeg_reference(
                self.processed,
                ref_channels=ref_channels,
                copy=copy,
                verbose=self.verbose,
                **kwargs)
