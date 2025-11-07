"""Class for anonymizing raw data"""

import mne
from biopap.modules.base_class import BaseClass
# from datetime import datetime
# from datetime import timezone

class Anonymize(BaseClass):

    #TODO: what about filename? randomize?
    #TODO: description

    def __init__(self,
                 raw,
                 daysback,
                 experimenter=None,
                 participant_id=None):
        try:              
            self.raw = raw.copy()
            raw.anonymize(daysback=daysback, verbose=True)
            # raw.set_meas_date(datetime.now(tz=timezone.utc))
            if experimenter is not None:
                raw.info['experimenter'] = str(experimenter)
            if participant_id is not None:
                raw.info['subject_info'] = {'his_id': str(participant_id)}
            self.processed = raw
        except Exception as e:
            print(f"Error: {e}")
