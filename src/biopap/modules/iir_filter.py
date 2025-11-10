"""Class for filtering"""

import mne
from biopap.modules.base_class import BaseClass

class IIRFilter(BaseClass):

    def __init__(self,
                 raw,
                 l_freq,
                 h_freq,
                 order=4, 
                 ftype='butter'):

        try:
            self.raw = raw
            self.apply_iir(
                l_freq=l_freq,
                h_freq=h_freq,
                order=order,
                ftype=ftype)
        except Exception as e:
            print(f"Error: {e}")

    def apply_iir(self, l_freq, h_freq, order, ftype):

        # Zero phase shift Butterworth filters.
        # Global filter settings:
        # Low cutoff: 0.1 Hz, time constant 1.5915494309189535, order 4
        # High cutoff: 35 Hz, order 4 
        # Notch filter: ---

        # https://mne.tools/stable/generated/mne.filter.construct_iir_filter.html#mne.filter.construct_iir_filter

        iir_params = dict(order=order, ftype=ftype)

        self.processed = self.raw.filter(l_freq=l_freq,
           h_freq=h_freq,
           method='iir',
           iir_params=iir_params, 
           verbose=self.verbose)
