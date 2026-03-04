"""Class for converting EEG data to BIDS format"""

import mne
import pandas as pd
from pathlib import Path
from mne_bids import BIDSPath, write_raw_bids, make_dataset_description
from biopap.modules.base_class import BaseClass

# TODO: Check what the sanitize_events function does and check if we need it. It was in Gabriel's code.
# TODO: subject, session, task, run, can we extract from raw?
#       If not, find a way to change these when running multiple datafiles. 
#       It is used for folder structure and file naming. 
# TODO: Optional; build_event_dict() make it more flexible to given input in eventsfile.
#       not sure how.. 
#       Currently; ranges have to be written with '-' in between two numbers, and column names need to be ID and LABEL

class BIDSConversion(BaseClass):

    def __init__(self,
                 raw,
                 eventsfile,
                 bids_root,
                 subject,
                 session,
                 task,
                 run,
                 overwrite=False,
                 dataset_description=None,
                 logger=None,
                 **kwargs):
                
        self.processed = raw
        
        bids_root = Path(bids_root)

        if subject is None:
            subject = self.processed.info.get("subject_info", {}).get("his_id", None)

        dataset_description = dataset_description or {}

        if not isinstance(self.raw, mne.io.BaseRaw):
            raise ValueError(f"BIDS module can only handle 'mne.io.BaseRaw' class, got '{type(self.raw)}'")

        try:

            f_kwargs = kwargs['find_events'] if 'find_events' in kwargs else {}
            b_kwargs = kwargs['BIDSPath'] if 'BIDSPath' in kwargs else {}
            w_kwargs = kwargs['write_raw_bids'] if 'write_raw_bids' in kwargs else {}
            mdd_kwargs = kwargs['make_dataset_description'] if 'make_dataset_description' in kwargs else {}
        
            # Parse events from raw data
            events = mne.find_events(self.processed,
                                     **f_kwargs)

            # Build mappings from eventfile
            event_id, range_map = self.build_event_dict(eventsfile)
            merged_events = self.merge_event_ranges(events, range_map)
            merged_events = self.sanitize_events(merged_events, event_id)

            # Create BIDS Path
            bids_path = BIDSPath(
                subject=subject,
                session=session,
                task=task,
                run=run,
                datatype="eeg",
                root=bids_root,
                **b_kwargs
            )

            write_raw_bids(
                raw=self.processed, 
                format='BrainVision', 
                bids_path=bids_path, 
                events=merged_events, 
                event_id=event_id, 
                allow_preload=True, 
                overwrite=overwrite,
                **w_kwargs
            )

            # Write dataset_description.json
            self.write_dataset_description(dataset_description, bids_root, mdd_kwargs)

            print("BIDS conversion completed.")

        except Exception as e:
            print(f"[BIDSConversion ERROR] {e}")

    @staticmethod
    def write_dataset_description(dataset_description, bids_root, mdd_kwargs):
        dd = {
            "name": dataset_description.get("name", "Untitled EEG Dataset"),
            "data_license": dataset_description.get("data_license", "CC0"),
            "authors": dataset_description.get("authors", ["Unknown"]),
            "acknowledgements": dataset_description.get("acknowledgements", []),
            "how_to_acknowledge": dataset_description.get("how_to_acknowledge", []),
            "funding": dataset_description.get("funding", []),
            "references_and_links": dataset_description.get("references", []),
            "doi": dataset_description.get("doi", []),
            "dataset_type": dataset_description.get("dataset_type", "raw")
        }

        make_dataset_description(
            path=bids_root,
            overwrite=True,
            **dd,
            **mdd_kwargs
        )

    @staticmethod
    def build_event_dict(eventsfile):
        event_id = {}
        range_map = {}

        df = pd.read_csv(eventsfile)

        for _, row in df.iterrows():
            label = str(row["label"]).strip()
            id_value = str(row["ID"]).strip()

            if label in event_id:
                raise ValueError(f"Duplicate event label: {label}")

            if "-" in id_value:
                start, end = map(int, id_value.split("-"))
                ids = list(range(start, end + 1))
                event_id[label] = ids[0]
                range_map[label] = ids
            else:
                try: 
                    event_id[label] = int(id_value) 
                except ValueError: 
                    event_id[label] = id_value # keep id as string

        return event_id, range_map
    
    @staticmethod
    def merge_event_ranges(events, range_map):
        merged = events.copy()
        for label, ids in range_map.items():
            merged = mne.merge_events(merged, ids, ids[0])
        return merged
    
    # ---------------------------------- 
    # Gabriel's code; not sure what non-zero trigger channel and acquisition system means
    # ----------------------------------
    def sanitize_events(self, events, event_id=None):
        """Checks if offset exists in triggers.
        """
        # Non-zero trigger channel here linked to acquisition system, correcting:
        if sum(events[:,-1]) != 0:
            events[:,-1] -= events[:,1]       
        if all(events[:,-1] > 0):
            self.raw.add_events(events, replace=True)
        else:
            raise ValueError("Non-zero trigger channel, yet correction not possible")
        
        # Check if all events have been labeled
        if event_id is not None:
            if len(set(events[:,-1]) - set(event_id.values())) > 0:
                raise ValueError(f"Event {set(events[:,-1]) - set(event_id.values())}"
                                "has not been declared in eventsfile") 
        print(f"Found triggers: {[int(x) for x in set(events[:,-1])]}")
        
        return events
