import mne
from biopap.modules.base_class import BaseClass

class ApplyICA(BaseClass):
    """
    Class for applying Independent Component Analysis (ICA).

    https://mne.tools/stable/generated/mne.preprocessing.ICA.html#mne.preprocessing.ICA
    https://mne.tools/stable/generated/mne.preprocessing.ICA.html#mne.preprocessing.ICA.fit
    https://mne.tools/stable/generated/mne.preprocessing.ICA.html#mne.preprocessing.ICA.apply

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
        ``fit``, and ``apply`` methods. Pass arguments for the different functions
        by using a dictionary with `fit`, `apply`, and `ICA` as keys. Example:
        {'ICA' : {'random_state': 23, 'max_iter': 500}, 'apply': {'on_baseline': 'ignore'} } 

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

        self.set_mne_config({**locals()})

        with self.capture_stdout as self.stdout:
        
            self.processed = raw

            i_kwargs = kwargs['ICA'] if 'ICA' in kwargs else {}
            f_kwargs = kwargs['fit'] if 'fit' in kwargs else {}
            a_kwargs = kwargs['apply'] if 'apply' in kwargs else {}

            ica = mne.preprocessing.ICA(n_components=n_components, method=method, **i_kwargs).fit(self.processed, **f_kwargs)
            self.processed = ica.apply(self.processed, **a_kwargs)
