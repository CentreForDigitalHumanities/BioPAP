import json
import logging
import mne
import pandas as pd
import random
import re
import string
import sys
import warnings
import yaml.dumper
from io import StringIO
from os import getenv
from pathlib import Path
from biopap.modules import CONFIG_MODULE_CLASS_KEY


def get_logger():
    log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"

    DEBUG = getenv('BIOPAP_DEBUG') == '1'
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO, format=log_format)
    logging.captureWarnings(True)
    warnings.formatwarning = custom_formatwarning
    logger = logging.getLogger(__name__)

    LOG_FILE = getenv('BIOPAP_LOGFILE', None)
    if LOG_FILE:
        fileHandler = logging.FileHandler(LOG_FILE)
        fileHandler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(fileHandler)

    return logger


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


class OptionsBaseClass:

    sel_options = 0

    def __init__(self, sel_options=0):
        if isinstance(sel_options, str):
            sel_options = [sel_options]

        if isinstance(sel_options, list):
            v_opts = 0
            for s in sel_options:
                s = s.upper()
                if len([x[1] for x in self.valid_options if x[0]==s])!=1:
                    raise ValueError(f"unknown option '{s}'")
                v_opts = v_opts + sum([x[1] for x in self.valid_options if x[0]==s])
            self._selected_options = v_opts

        else:
            self._selected_options = sel_options

    def is_selected(self, lookup):
        if self.selected_options is None:
            return False

        tmp = self.selected_options
        for opt, val in self.valid_options:
            if tmp >= val:
                if lookup == val:
                    return True
                tmp -= val
        return False

    @property
    def valid_options(self):
        return sorted([(x, getattr(self, x)) for x in dir(self) if not x.startswith('__') and x.isupper()], key=lambda y: -y[1])

    @property
    def selected_options(self):
        return self._selected_options


def custom_formatwarning(message, category, filename, *args, **kwargs):
    return f"{str(Path(filename).stem)}:{str(message)}"


def get_new_filename(filename, save_folder, save_postfix=None, save_overwrite=False):
    d_out = Path(save_folder)
    d_out.mkdir(parents=True, exist_ok=True)
    f_src = Path(filename)

    if save_postfix:
        f_new = Path(f_src.with_name(f'{f_src.stem}_{save_postfix}{f_src.suffix}').name)
    else:
        f_new = Path(f_src.name)

    p_out = d_out / f_new

    if not save_overwrite:
        i = 1
        while p_out.exists():
            p_out = d_out / f_new.with_name(f'{f_new.stem}_({i}){f_src.suffix}').name
            i += 1

    return p_out


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


def create_template_annotations_dict(in_path,
                                     out_path,
                                     encoding='latin-1',
                                     default_regex=r'(?<=(^RS232 Trigger: ))(\d+)'):
    a_dict = {}
    annots = mne.read_annotations(in_path, encoding=encoding)
    for annot in annots:
        match = re.search(default_regex, annot['description'])
        a_dict[str(annot['description'])] = int(match.group()) if match else '?'

    with open(out_path, 'w') as f:
        json.dump(a_dict, f, sort_keys=True, indent=4)

    print(f'Wrote template dictionary to {out_path}')
    

def save_modules_config(modules, config_path, append=False):
    """
    Saves ad hoc defined configuration settings of one or more
    modules to a yaml configuration file which can be used in
    subsequent BioPAP sessions.
    Parameters
    ----------
    modules : list
        List of BioPAP module instances
    config_path : str or Path
        Path to config yaml file
    append : bool (default: False)
        If True, appends to file or creates it if it doesn't
        exist; if False, deletes pre-existing file if it
        exists.
    """
    if not append:
        Path(config_path).unlink(missing_ok=True)

    mod_list = []
    for module in modules:
        mod_name = module.__class__.__name__
        i = 2
        while mod_name in mod_list:
            mod_name = f"{module.__class__.__name__}_{str(i)}"
            i += 1
        module.save_config(path=config_path, cfg_label=mod_name)
        mod_list.append(mod_name)
        i = 2


def path_representer(dumper, obj):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))

class YamlDumper(yaml.dumper.SafeDumper):
    # also solves ' !!python/tuple' constructor, not sure why though
    pass

yaml.add_representer(
    type(Path()),
    path_representer,
    YamlDumper,
)

def generate_pseudonym_file_list(files, code_length=4, include_date=True):
    pseudo = []
    for file in files:
        while True:
            p = ''.join([random.choice(string.ascii_letters[26:]) for x in range(code_length)])
            if p not in [x['pseudocode'] for x in pseudo]:
                pseudo.append({
                    'input_file': file, 
                    'pseudocode': p
                    })
                break

    return pseudo
