"""Class for Independent Component Analysis (ICA)"""

import mne
from biopap.modules.base_class import BaseClass

class ApplyICA(BaseClass):
    
    def __init__(self,
                 raw,
                 **kwargs):
        
        self.raw = raw

        try:

            n_components = 64
            ica = mne.preprocessing.ICA(n_components = n_components, method='fastica', max_iter='auto').fit(raw)
            raw = ica.apply(raw)

            # ica.plot_components()

            self.processed = self.raw

        except Exception as e:
            print(f"Error: {e}")