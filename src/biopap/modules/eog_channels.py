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
                 copy=False,
                 drop_refs=False,
                 auto_run: bool=True):

        self.raw = raw
        self.ref_channels = ref_channels
        self.anode_channels = anode_channels
        self.cathode_channels = cathode_channels
        self.copy = copy
        self.drop_refs = drop_refs
        if auto_run:
            self.run()

    def run(self):
        try:
            # drop existing channels with same name as new ref channels
            exist_channels = [x for x in self.ref_channels if x in self.raw.ch_names]
            self.raw.drop_channels(exist_channels)

            # check if anode & cathode channels exist
            missing_channels = [x for x in 
                self.anode_channels + self.cathode_channels if x not in self.raw.ch_names]

            if len(missing_channels)>0:
                raise ValueError(f"Non-existant channels: {'; '.join(missing_channels)}")

            # raw = mne.add_reference_channels(raw, ref_channels=ref_channels, copy=False)
            mne.set_bipolar_reference(
                self.raw,
                anode=self.anode_channels,
                cathode=self.cathode_channels,
                ch_name=self.ref_channels,
                copy=self.copy,
                drop_refs=self.drop_refs,
                verbose=self.verbose)

            self.processed = self.raw
        except Exception as e:
            print(f"Error: {e}")
