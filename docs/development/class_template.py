import mne
from biopap.modules.base_class import BaseClass

class ExampleClass(BaseClass):
    """
    Class for ... .

    Short explanation.

    MNE-functions used: [mne.some_function](https://mne.tools/stable/generated/mne.some_function.html), [mne.another_function](https://mne.tools/stable/generated/mne.another_function.html)

    Parameters
    ----------
    raw : mne.raw
        Input data.
    some_var : int
        Some variable.
    another_var : str
        Another variable.
    **kwargs
        Additional keyword arguments passed to the underlying
        ``mne.some_function()`` and ``mne.another_function()`` methods.
        Pass arguments for the different functions by using a dictionary with
        `some_function`, and `another_function` as keys. Example:
        {'some_function' : {'var_a': False, 'var_b': 23}, 'another_function': {'var_c': 'slow'}}

    Attributes
    ----------
    processed : mne.raw
        Output data.
    """
    def __init__(self,
                raw,
                some_var=50,
                another_var='eeg',
                silent: bool=False,
                **kwargs):

        #TODO: explain
        super().__init__(silent)

        #TODO: explain
        self.set_config({**locals()})

        #TODO: explain
        with self.capture_stdout as self.stdout:

            #TODO: explain
            self.processed = raw

            #TODO: explain
            if not isinstance(self.processed, mne.raw):
                raise TypeError(
                    "the input must be an mne.raw instance, "
                    f"got {type(self.processed)} instead."
                )
                        
            if processing_type not in [1, 2]:
                raise ValueError(f"processing_type must 1 or 2, got {processing_type} instead.")
                        
            #TODO: explain
            s_kwargs = kwargs['some_function'] if 'some_function' in kwargs else {}
            a_kwargs = kwargs['another_function'] if 'another_function' in kwargs else {}

            add_values = mne.some_function(
                processed,
                some_var=some_var,
                **s_kwargs)

            add_value = self.transform_add_values(add_values)

            self.processed = mne.another_function(
                self.raw,
                another_var=another_var,
                additional_var=add_value,
                **a_kwargs)


    def transform_add_values(self, values):
        return values[:, 0] / 100
