import mne
from biopap.modules.base_class import BaseClass

class IIRFilter(BaseClass):
    """
    Class for applying IIR filtering.

    Filters the input data using an IIR filter with MNE's ``filter()`` method.

    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    l_freq : float
        Low cutoff frequency in Hz.
    h_freq : float
        High cutoff frequency in Hz.
    order : int, default 4
        Order of the IIR filter.
    ftype : {'butter', 'cheby1', 'cheby2', 'ellip', 'bessel'}, default 'butter'
        Type of IIR filter to design:

        - ``'butter'`` (Butterworth)
        - ``'cheby1'`` (Chebyshev I)
        - ``'cheby2'`` (Chebyshev II)
        - ``'ellip'`` (Cauer/elliptic)
        - ``'bessel'`` (Bessel/Thomson)
    **kwargs
        Additional keyword arguments passed to MNE's ``filter()`` method.

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Filtered output data.
    """

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
