"""Class for filtering"""

import mne
from biopap.modules.base_class import BaseClass

class IIRFilter(BaseClass):

    def __init__(self,
                 raw,
                 logger,
                 l_freq,
                 h_freq,
                 order=4, 
                 ftype='butter',
                 **kwargs):

        self.processed = raw

        try:

            # Zero phase shift Butterworth filters.
            # Global filter settings:
            # Low cutoff: 0.1 Hz, time constant 1.5915494309189535, order 4
            # High cutoff: 35 Hz, order 4 
            # Notch filter: ---

            # https://mne.tools/stable/generated/mne.filter.construct_iir_filter.html#mne.filter.construct_iir_filter

            iir_params = dict(order=order, ftype=ftype)

            self.processed = self.processed.filter(l_freq=l_freq,
               h_freq=h_freq,
               method='iir',
               iir_params=iir_params, 
               verbose=self.verbose,
               **kwargs)

        except Exception as e:
            logger.error(str(e))
            self.exit_code = 1
