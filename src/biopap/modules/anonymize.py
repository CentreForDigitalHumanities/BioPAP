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
