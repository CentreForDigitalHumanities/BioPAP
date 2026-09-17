import mne
from random import randint
from typing import Union
from biopap.modules.base_class import BaseClass

class Anonymize(BaseClass):
    """
    Class for anonymizing raw or epoched data.

    Applies MNE's built-in anonymization (``Raw.anonymize()`` or
    ``Epochs.anonymize()``) to the provided data object.

    MNE-modules used:
    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.anonymize
    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.anonymize

    Parameters
    ----------
    raw : mne.io.Raw | mne.Epochs
        Input data to anonymize.
    daysback : int | None
        Number of days to subtract from all dates.
    experimenter : str
        Name of the experimenter to store in the anonymized metadata.
    participant_id : str
        Participant identifier to store in the anonymized metadata.
    **kwargs
        Additional keyword arguments passed to the underlying MNE
        ``Raw.anonymize()`` or ``Epochs.anonymize()`` method.

    Attributes
    ----------
    processed : mne.io.Raw | mne.Epochs
        Anonymized output data.
    """

    log_config = False
    alters_data = False

    def __init__(self,
                 raw: mne.io.Raw,
                 daysback: Union[int, str],
                 experimenter: str=None,
                 participant_id: str=None,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:

            if not isinstance(daysback, int) and daysback.lower() != 'random':
                raise ValueError(f"daysback must be either int or 'random' (got '{daysback}')")

            if not isinstance(daysback, int):
                daysback = randint(1, 100)

            self.processed = raw

            self.processed.anonymize(
                daysback=daysback,
                verbose=self.verbose,
                **kwargs)

            if experimenter is not None:
                self.processed.info['experimenter'] = str(experimenter)

            if participant_id is not None:
                self.processed.info['subject_info'] = {'his_id': str(participant_id)}
