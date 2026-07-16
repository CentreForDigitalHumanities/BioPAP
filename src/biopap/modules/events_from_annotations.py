import mne
import numpy as np
import re
from typing import Union
from biopap.modules.base_class import BaseClass

class EventsFromAnnotations(BaseClass):
    """
    Class for extracting events from annotations in MNE Raw objects, and adding them to the stim channel. If the stim channel does not exist, it will be created.

    https://mne.tools/stable/generated/mne.events_from_annotations.html 

    Parameters
    ----------
    raw : mne.Raw
        Input Raw object containing annotations.
    event_id : dict | callable() | None | 'auto', default 'auto'
        Can be:
            dict: map descriptions (keys) to integer event codes (values). Only the descriptions present will be mapped, others will be ignored.
            callable: must take a string input and return an integer event code, or return None to ignore the event.
            None: Map descriptions to unique integer values based on their sorted order.
            ‘auto’ (default): prefer a raw-format-specific parser:
                Brainvision: map stimulus events to their integer part; response events to integer part + 1000; optic events to integer part + 2000; ‘SyncStatus/Sync On’ to 99998; ‘New Segment/’ to 99999; all others like None with an offset of 10000.
                Other raw formats: Behaves like None.
    regex : str, default None
        Regular expression to extract event IDs from annotation descriptions. If regex is provided, event_id will be ignored and event IDs will be extracted using the regex pattern. The regex should contain a capturing group that extracts only the desired event ID.
    stim_channel : str, default 'STI 014'
        If the stim channel does not exist, give a name for the new stim channel to be created. If the stim channel already exists, this parameter is ignored.
    delete_annotations : bool, default False
        If True, deletes all annotations after extracting events.
    silent : bool, default False
        If True, suppresses print statements during processing.

    Attributes
    ----------
    processed : mne.io.Raw
        Output data with events added to the stim channel.
    """

    def __init__(self,
                 raw,
                 event_id: Union[dict, str, callable, None]='auto',
                 regex: str=None,
                 stim_channel: str='STI 014',
                 delete_annotations: bool=False,
                 silent: bool=False,
                 ):
        super().__init__(silent)

        self.set_config({**locals()})

        with self.capture_stdout as self.stdout:
                  
            self.processed = raw

            if regex:
                events, _event_dict = mne.events_from_annotations(
                    self.processed,
                    event_id=lambda string: get_eventid_from_string(string, regex))
            else:
                events, _event_dict = mne.events_from_annotations(self.processed, event_id=event_id)

            if 'stim' not in self.processed.get_channel_types():
                stim_data = np.zeros((1, len(self.processed.times)))
                info = mne.create_info([stim_channel], self.processed.info['sfreq'], ['stim'])
                stim_raw = mne.io.RawArray(stim_data, info)
                self.processed.add_channels([stim_raw], force_update_info=True)
            
            self.processed.add_events(events, replace=True)

            if delete_annotations == True:
                self.processed.annotations.delete(idx=range(len(self.processed.annotations)))

def get_eventid_from_string(event_string, regex):
    eventid = re.search(regex, event_string)

    if eventid:
        return int(eventid.group())
    
    return None
