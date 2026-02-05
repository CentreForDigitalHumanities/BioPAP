"""Class for setting channel types"""

import mne
from biopap.modules.base_class import BaseClass

class SetChannelType(BaseClass):

    def __init__(self,
                raw,
                channel_types,
                **kwargs):

        self.raw = raw

        try:
            
            for type in channel_types: 
                self.raw.set_channel_types({chs: type for chs in channel_types.get(type)}, **kwargs)

            self.processed = self.raw
        
        except Exception as e:
            print(f"Error: {e}")
