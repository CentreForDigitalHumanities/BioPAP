"""Class for adding vEOG and hEOG"""

import mne
from biopap.modules.base_class import BaseClass

class EOGChannels(BaseClass):

    # https://mne.tools/stable/auto_tutorials/preprocessing/10_preprocessing_overview.html#ocular-artifacts-eog

    # *** Linear Derivation ***
    # Keep old channels.
    # The new channels are appended.
    # Coefficient Matrix:
    #         EXG3     EXG4   EXG5  EXG6      
    # hEOG      1         -1        0         0         
    # vEOG      0         0         1         -1     

    def __init__(self,
                 raw,
                 ref_channels=['hEOG', 'vEOG'],
                 anode_channels=['EXG3','EXG5'], 
                 cathode_channels=['EXG4','EXG6'],
                 misc_channels=[],
                 copy=False,
                 drop_refs=False,
                 **kwargs):

        self.raw = raw

        try:
            # drop existing channels with same name as new ref channels
            exist_channels = [x for x in ref_channels if x in self.raw.ch_names]
            self.raw.drop_channels(exist_channels)

            # check if anode & cathode channels exist
            missing_channels = [x for x in 
                anode_channels + cathode_channels if x not in self.raw.ch_names]

            if len(missing_channels)>0:
                raise ValueError(f"Non-existant channels: {'; '.join(missing_channels)}")

            # raw = mne.add_reference_channels(raw, ref_channels=ref_channels, copy=False)
            mne.set_bipolar_reference(
                self.raw,
                anode=anode_channels,
                cathode=cathode_channels,
                ch_name=ref_channels,
                copy=copy,
                drop_refs=drop_refs,
                verbose=self.verbose,
                **kwargs)
            
            # Set channel type 'eog' for reference channels
            self.raw.set_channel_types({eog_ch: 'eog' for eog_ch in ref_channels})
            self.raw.set_channel_types({misc_ch: 'misc' for misc_ch in misc_channels})
            self.processed = self.raw

        except Exception as e:
            print(f"Error: {e}")
