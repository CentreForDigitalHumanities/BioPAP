import mne
from biopap.modules.base_class import BaseClass

class SetChannelTypeAndMontage(BaseClass):
    """
    Class for setting channel types and creating montage.
    
    Assigns channel types and applies an MNE standard montage
    using ``set_channel_types()``, ``make_standard_montage()``, and
    ``set_montage()``.

    https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.set_channel_types
    https://mne.tools/stable/generated/mne.channels.make_standard_montage.html
    https://mne.tools/stable/generated/mne.channels.make_standard_montage.html


    Parameters
    ----------
    raw : mne.io.Raw | mne.Epochs
        Input data.
    channel_types : dict with list of str
        Mapping of channel type to channel names. The dictionary key
        specifies the MNE channel type (e.g., ``'eeg'``, ``'eog'``,
        ``'misc'``), and the value is a list of channel names to assign
        that type to.

        Valid MNE channel types include:

        ``'bio'``, ``'chpi'``, ``'dbs'``, ``'dipole'``, ``'ecg'``,
        ``'ecog'``, ``'eeg'``, ``'emg'``, ``'eog'``, ``'exci'``,
        ``'eyetrack'``, ``'fnirs'``, ``'gof'``, ``'gsr'``, ``'ias'``,
        ``'misc'``, ``'meg'``, ``'ref_meg'``, ``'resp'``, ``'seeg'``,
        ``'stim'``, ``'syst'``, ``'temperature'``.
    mne_standard_montage : str, default 'biosemi64'
        Name of a built-in MNE montage. Use
        ``mne.channels.get_builtin_montages()`` to list available options.
    **kwargs
        Additional keyword arguments passed to MNE's
        ``set_channel_types()``, ``make_standard_montage()``, and
        ``set_montage()`` functions. Pass arguments for the different
        functions by using a dictionary with ``set_channel_types``,
        ``make_standard_montage``, and ``set_montage`` as keys.

    Attributes
    ----------
    processed : mne.io.Raw | mne.Epochs
        Output data with updated channel types and montage.
    """
    def __init__(self,
                raw,
                channel_types,
                mne_standard_montage,
                silent: bool=False,
                **kwargs):

        super().__init__(silent)

        self.set_mne_config({**locals()})

        with self.capture_stdout as self.stdout:

            self.processed = raw

            s_kwargs = kwargs['set_channel_types'] if 'set_channel_types' in kwargs else {}
            m_kwargs = kwargs['make_standard_montage'] if 'make_standard_montage' in kwargs else {}
            sm_kwargs = kwargs['set_montage'] if 'set_montage' in kwargs else {}
            
            # Set channel types
            for type in channel_types: 
                self.processed.set_channel_types({chs: type for chs in channel_types.get(type)}, **s_kwargs)

            # Create montage of electrodes
            montage = mne.channels.make_standard_montage(mne_standard_montage, **m_kwargs)
            self.processed.set_montage(montage, **sm_kwargs)
