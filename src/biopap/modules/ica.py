"""Class for Independent Component Analysis (ICA)"""

import mne
from biopap.modules.base_class import BaseClass

class ApplyICA(BaseClass):
    
    def __init__(self,
                 raw,
                 n_components=None,
                 method='fastica',
                 **kwargs):
        
        self.processed = raw

        try:
            i_kwargs = kwargs['ICA'] if 'ICA' in kwargs else {}
            f_kwargs = kwargs['fit'] if 'fit' in kwargs else {}
            a_kwargs = kwargs['apply'] if 'apply' in kwargs else {}

            ica = mne.preprocessing.ICA(n_components=n_components, method=method, **i_kwargs).fit(self.processed, **f_kwargs)
            self.processed = ica.apply(self.processed, **a_kwargs)

            ### TEMP CODE ###
            ### DECIDE WHICH OUTPUT ###

            ica.plot_components(picks=range(20))
            ica.plot_overlay(self.processed, exclude=[0], picks="eeg")
            ica.plot_properties(raw, picks=[0, 1])

            ica.exclude = []
            # find which ICs match the EOG pattern
            eog_indices, eog_scores = ica.find_bads_eog(self.processed)
            ica.exclude = eog_indices

            # barplot of ICA component "EOG match" scores
            ica.plot_scores(eog_scores)

            # plot diagnostics
            ica.plot_properties(self.processed, picks=eog_indices)

            # plot ICs applied to raw data, with EOG matches highlighted
            ica.plot_sources(self.processed, show_scrollbars=False)


        except Exception as e:
            print(f"Error: {e}")