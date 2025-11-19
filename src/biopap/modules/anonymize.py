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
                 participant_id: str=None):

        self.raw = raw.copy()
        self.daysback = daysback
        self.experimenter = experimenter
        self.participant_id = participant_id

    def run(self):
        try:
            self.raw.anonymize(
                daysback=self.daysback,
                verbose=self.verbose)
            # self.raw.set_meas_date(datetime.now(tz=timezone.utc))
            
            if self.experimenter is not None:
                self.raw.info['experimenter'] = str(self.experimenter)
            if self.participant_id is not None:
                self.raw.info['subject_info'] = {'his_id': str(self.participant_id)}

            self.processed = self.raw
        except Exception as e:
            print(f"Error: {e}")
