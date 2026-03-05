"""Class for Independent Component Analysis (ICA)"""

import mne
from biopap.modules.base_class import BaseClass

class ApplyICA(BaseClass):
    
    def __init__(self,
                 raw,
                 logger=None,
                 **kwargs):
        
        self.processed = raw

        try:

            n_components = 64
            ica = mne.preprocessing.ICA(n_components = n_components, method='fastica', max_iter='auto').fit(self.processed)
            self.processed = ica.apply(self.processed)

            # ica.plot_components()

        except Exception as e:
            if logger:
                logger.error(str(e))
            else:
                print(f"ERROR:{__class__.__name__}: {str(e)}")