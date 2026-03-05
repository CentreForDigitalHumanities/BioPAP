"""Class for baseline correction"""

import mne
from biopap.modules.base_class import BaseClass

class BaselineCorrection(BaseClass):

    # *** Baseline Correction ***
    # Begin: -200.00 ms End: 0.00 ms

    def __init__(self,
                 raw,
                 logger,
                 baseline,
                 ):
        
        self.processed = raw
                     
        try:
        
            self.processed = self.processed.apply_baseline(baseline)
                                            
        except Exception as e:
            logger.error(str(e))
            self.exit_code = 1

