import mne
import pandas as pd
from pathlib import Path
from mne_bids import BIDSPath, write_raw_bids, make_dataset_description
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import build_event_dict, merge_event_ranges

class BIDSConversion(BaseClass):
    """
    Class for converting EEG data to BIDS format.

    It uses MNE-BIDS library for the conversion. The module reads event information from a provided eventfile and maps it to the events in the raw data. It then writes the raw data, events, and other metadata to a BIDS-compliant directory structure.

    https://mne.tools/mne-bids/stable/generated/mne_bids.BIDSPath.html#mne_bids.BIDSPath
    https://mne.tools/mne-bids/stable/generated/mne_bids.write_raw_bids.html#mne_bids.write_raw_bids

    
    Parameters
    ----------
    raw : mne.Raw
        Input data.
    eventsfile : str
        Path to a csv file with 2 columns (ID, label). 
    bids_root : str
        Root directory for the BIDS dataset.
    session : str
        Session identifier.
    task : str
        Task identifier.
    run : str
        Run identifier.
    subject : str, optional
        Subject identifier. If not provided, it will be extracted from the raw data.
    datatype : str, default 'eeg'
        Data type for the BIDS files, e.g. 'anat', 'func', 'eeg', 'meg', 'ieeg'..
    format : ‘auto’ | ‘BrainVision’ | ‘BDF’ | ‘EDF’ | ‘FIF’ | ‘EEGLAB’, default 'BrainVision'
        File format for the output BIDS files. 
    overwrite : bool, default False
        Whether to overwrite existing BIDS files.
    **kwargs
        Additional keyword arguments passed to MNE-BIDS functions. Example:
        'BIDSPath': {'suffix': 'channels'}, 'write_raw_bids': {'acpc_aligned': True}}

    Attributes
    ----------
    processed : mne.Raw
        Output data after BIDS conversion.
    """

    alters_data = False

    def __init__(self,
                 raw,
                 eventsfile,
                 bids_root,
                 session: str=None,
                 task: str=None,
                 run: int=None,
                 subject: str=None,
                 datatype: str='eeg',
                 format: str='BrainVision',
                 overwrite: bool=False,
                 silent: bool=False,
                 **kwargs):

        super().__init__(silent)

        with self.capture_stdout as self.stdout:
                
            self.raw = raw
            
            bids_root = Path(bids_root)

            if subject is None:
                subject = self.raw.info.get("subject_info", {}).get("his_id", None)

            if not isinstance(self.raw, mne.io.BaseRaw):
                raise ValueError(f"BIDS module can only handle 'mne.io.BaseRaw' class, got '{type(self.raw)}'")

            f_kwargs = kwargs['find_events'] if 'find_events' in kwargs else {}
            b_kwargs = kwargs['BIDSPath'] if 'BIDSPath' in kwargs else {}
            w_kwargs = kwargs['write_raw_bids'] if 'write_raw_bids' in kwargs else {}
        
            # Build mappings from eventfile
            events = mne.find_events(self.raw, **f_kwargs)
            event_id, range_map = build_event_dict(events, eventsfile)
            merged_events = merge_event_ranges(events, range_map)

            unlabeled_events = set(merged_events[:, -1]) - set(event_id.values())
            if len(unlabeled_events) > 0:
                clean_unlabeled_events = [int(event) for event in unlabeled_events]
                raise ValueError(
                    f"Event {clean_unlabeled_events} has not been declared in eventsfile"
                )

            bids_path = BIDSPath(
                subject=subject,
                session=session,
                task=task,
                run=run,
                datatype=datatype,
                root=bids_root,
                **b_kwargs
            )

            write_raw_bids(
                raw=self.raw, 
                format=format, 
                bids_path=bids_path, 
                events=merged_events, 
                event_id=event_id, 
                allow_preload=True, 
                overwrite=overwrite,
                **w_kwargs
            )
