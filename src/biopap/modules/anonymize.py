import mne
from biopap.modules.base_class import BaseClass
# from datetime import datetime
# from datetime import timezone

class Anonymize(BaseClass):
    """
    Class for anonymizing raw or epoched data.

    Applies MNE's built-in anonymization (``Raw.anonymize()`` or
    ``Epochs.anonymize()``) to the provided data object.

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

    #TODO: what about filename? randomize?
    #TODO: description

    def __init__(self,
                 raw: mne.io.Raw,
                 daysback: int,
                 logger,
                 experimenter: str=None,
                 participant_id: str=None,
                 **kwargs):

        self.processed = raw

        try:
            self.processed.anonymize(
                daysback=daysback,
                verbose=self.verbose,
                **kwargs)

            # self.processed.set_meas_date(datetime.now(tz=timezone.utc))
            
            if experimenter is not None:
                self.processed.info['experimenter'] = str(experimenter)
            if participant_id is not None:
                self.processed.info['subject_info'] = {'his_id': str(participant_id)}

        except Exception as e:
            logger.error(str(e))
            self.exit_code = 1
