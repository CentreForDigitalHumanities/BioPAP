"""Class for anonymizing raw data"""

import mne
from biopap.modules.base_class import BaseClass
# from datetime import datetime
# from datetime import timezone

class Anonymize(BaseClass):

    #TODO: what about filename? randomize?
    #TODO: description

    def __init__(self,
                 raw: mne.io.Raw,
                 daysback: int,
                 experimenter: str=None,
                 participant_id: str=None,
                 **kwargs):

        self.raw = raw.copy()

        try:
            self.raw.anonymize(
                daysback=daysback,
                verbose=self.verbose,
                **kwargs)

            # self.raw.set_meas_date(datetime.now(tz=timezone.utc))
            
            if experimenter is not None:
                self.raw.info['experimenter'] = str(experimenter)
            if participant_id is not None:
                self.raw.info['subject_info'] = {'his_id': str(participant_id)}

            self.processed = self.raw
        except Exception as e:
            print(f"Error: {e}")
