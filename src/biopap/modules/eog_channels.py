import mne
from biopap.modules.base_class import BaseClass

class EOGChannels(BaseClass):
    """
    Class for adding vertical and horizontal EOG channels.

    Creates new bipolar channels from specified reference, anode, and
    cathode channels using MNE's ``set_bipolar_reference()`` function.

    https://mne.tools/stable/generated/mne.set_bipolar_reference.html
    
    Parameters
    ----------
    raw : mne.Raw | mne.Epochs
        Input data.
    ref_channels : list of str
        Reference channels used for the bipolar derivation.
    anode_channels : list of str
        Channels to use as the anode in the bipolar derivation.
    cathode_channels : list of str
        Channels to use as the cathode in the bipolar derivation.
    copy : bool, default False
        If True, returns a copy of the data; otherwise, modifies in place.
    drop_refs : bool, default False
        If True, drop the original reference channels after creating the bipolar channels.
    **kwargs
        Additional keyword arguments passed to MNE's
        ``set_bipolar_reference()`` function.
        Example: {'on_bad': 'ignore'}

    Attributes
    ----------
    processed : mne.Raw | mne.Epochs
        Output data with EOG channels.
    """

    def __init__(self,
                 raw,
                 ref_channels=['hEOG', 'vEOG'],
                 anode_channels=['EXG3','EXG5'], 
                 cathode_channels=['EXG4','EXG6'],
                 copy=False,
                 drop_refs=False,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw
            # drop existing channels with same name as new ref channels
            exist_channels = [x for x in ref_channels if x in self.processed.ch_names]
            self.processed.drop_channels(exist_channels)

            # check if anode & cathode channels exist
            missing_channels = [x for x in 
                anode_channels + cathode_channels if x not in self.processed.ch_names]

            if len(missing_channels)>0:
                raise ValueError(f"Non-existant channels: {'; '.join(missing_channels)}")

            self.processed = mne.set_bipolar_reference(
                self.processed,
                anode=anode_channels,
                cathode=cathode_channels,
                ch_name=ref_channels,
                copy=copy,
                drop_refs=drop_refs,
                verbose=self.verbose,
                **kwargs)
            
            # Set channel type 'eog' for reference channels
            self.processed.set_channel_types({eog_ch: 'eog' for eog_ch in ref_channels})
