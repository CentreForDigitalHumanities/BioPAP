import mne
from biopap.modules.base_class import BaseClass
import re

class Segmentation(BaseClass):
    """
    Class for segmentation (Epoching).
        
    Extracts events from the specified stimulation channel and creates
    epochs around selected markers using MNE's ``find_events()`` and
    ``Epochs`` functions.

    Parameters
    ----------
    raw : mne.io.Raw
        Input data.
    stim_channel : str
        Name of the stimulation channel used to detect events
        (e.g., 'Status').
    start : float
        Start time of each epoch in seconds relative to the event.
    end : float 
        End time of each epoch in seconds relative to the event
    baseline : tuple of (float, float) | None
        Time interval for baseline correction passed to MNE Epochs.
        Use None to disable baseline correction.
    reference_markers :  dict
        Marker selection configuration with the following optional keys:
        - "list" : list of int | None  
        Explicit marker IDs to include.
        - "range" : str | None  
        Inclusive marker range as ``"min-max"`` (e.g. ``"10-69"``).

        If both keys are provided, their union is used.
        If None or empty, all detected events are used.
    **kwargs
        Additional keyword arguments passed to MNE's
        ``find_events`` and ``Epochs`` functions.

    Attributes
    ----------
    processed : mne.Epochs
        Epoched output data.
    """

    def __init__(self,
                 raw,
                 stim_channel,
                 start,
                 end,
                 baseline=None,
                 reference_markers=None,
                 silent: bool=False,
                 **kwargs):
        
        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.processed = raw

            f_kwargs = kwargs['find_events'] if 'find_events' in kwargs else {}
            e_kwargs = kwargs['Epochs'] if 'Epochs' in kwargs else {}

            events = mne.find_events(self.processed,
                                        stim_channel=stim_channel,
                                        verbose=self.verbose,
                                        **f_kwargs)

            include = None

            if reference_markers.get("range"):
                range_markers = re.split('-|,|:', reference_markers.get("range"))
                include = list(range(int(range_markers[0]), int(range_markers[1])+1))

            elif reference_markers.get("list"):
                include = reference_markers["list"]

            if include:
                events = mne.pick_events(events, include=include)
            else:
                print("No reference markers provided; epochs are created with all events")
            
            self.processed = mne.Epochs(self.processed, 
                                events, 
                                tmin=start, 
                                tmax=end, 
                                baseline=baseline,
                                preload=True,
                                **e_kwargs)
