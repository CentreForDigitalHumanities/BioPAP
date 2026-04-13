import sys
from pathlib import Path
from io import StringIO
import pandas as pd
import mne

class CaptureStdout(list):

    """
    captures stdout from func() in var captured
    """

    def __init__(self, do_capture = True):
        self.do_capture = do_capture

    def __enter__(self):
        if self.do_capture:
            self._stdout = sys.stdout
            sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        if self.do_capture:
            self.extend(self._stringio.getvalue().splitlines())
            del self._stringio
            sys.stdout = self._stdout


def custom_formatwarning(message, category, filename, *args, **kwargs):
    return f"{str(Path(filename).stem)}:{str(message)}"

def build_event_dict(events, eventsfile):
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

            if int(ids[0]) in events:
                event_id[label] = int(ids[0])
                range_map[label] = ids
                
        else:
            event_id[label] = int(id_value) if id_value.isnumeric() else id_value

    return event_id, range_map

def merge_event_ranges(events, range_map):
    merged = events.copy()
    for label, ids in range_map.items():
        merged = mne.merge_events(merged, ids, ids[0])
    return merged