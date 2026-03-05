"""Class for setting channel types and creating montage"""

import mne
from biopap.modules.base_class import BaseClass

class SetChannelTypeAndMontage(BaseClass):

    def __init__(self,
                raw,
                channel_types,
                mne_standard_montage,
                logger=None,
                **kwargs):

        self.processed = raw

        try:

            s_kwargs = kwargs['set_channel_types'] if 'set_channel_types' in kwargs else {}
            m_kwargs = kwargs['make_standard_montage'] if 'make_standard_montage' in kwargs else {}
            sm_kwargs = kwargs['set_montage'] if 'set_montage' in kwargs else {}
            
            # Set channel types
            for type in channel_types: 
                self.processed.set_channel_types({chs: type for chs in channel_types.get(type)}, **s_kwargs)

            # Create montage of electrodes
            montage = mne.channels.make_standard_montage(mne_standard_montage, **m_kwargs)
            self.processed.set_montage(montage, **sm_kwargs)
        
        except Exception as e:
            if logger:
                logger.error(str(e))
            else:
                print(f"ERROR:{__class__.__name__}: {str(e)}")

