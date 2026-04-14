import mne
from biopap.modules.base_class import BaseClass

class ApplyICA(BaseClass):
    """
    Class for applying Independent Component Analysis (ICA).

    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    n_components : int, optional, default 'None'
        Number of components to extract. If None, all components are extracted.
    method : 'fastica' | 'infomax' | 'picard', default 'fastica'
        ICA method to use.
    **kwargs
        Additional keyword arguments passed to MNE's ``ICA``,
        ``fit``, and ``apply`` methods.

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Output data after ICA.
    """
    
    def __init__(self,
                 raw,
                 n_components=None,
                 method='fastica',
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:
        
            self.processed = raw

            i_kwargs = kwargs['ICA'] if 'ICA' in kwargs else {}
            f_kwargs = kwargs['fit'] if 'fit' in kwargs else {}
            a_kwargs = kwargs['apply'] if 'apply' in kwargs else {}

            ica = mne.preprocessing.ICA(n_components=n_components, method=method, **i_kwargs).fit(self.processed, **f_kwargs)
            self.processed = ica.apply(self.processed, **a_kwargs)
