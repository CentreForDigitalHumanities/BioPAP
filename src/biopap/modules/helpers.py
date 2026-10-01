import collections
import json
import logging
import mne
import pandas as pd
import re
import sys
import warnings
import yaml
from yaml import load, Loader, dumper
from io import StringIO
from os import getenv
from pathlib import Path
from termcolor import colored


class CustomFormatter(logging.Formatter):

    log_format = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"

    FORMATS = {
        logging.DEBUG: colored(log_format, 'white'),
        logging.INFO:  colored(log_format, 'white'),
        logging.WARNING:  colored(log_format, 'light_yellow'),
        logging.ERROR:  colored(log_format, 'light_red'),
        logging.CRITICAL: colored(log_format, 'light_red', attrs=['bold'])
    }

    def __init__(self, use_color=True):
        self.use_color = use_color

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno) if self.use_color else self.log_format
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(use_color=True):

    rootLogger = logging.getLogger()

    DEBUG = getenv('BIOPAP_DEBUG') == '1'
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    if (rootLogger.hasHandlers()):
        rootLogger.handlers.clear()

    LOG_FILE = getenv('BIOPAP_LOGFILE', None)
    if LOG_FILE:
        fileHandler = logging.FileHandler(LOG_FILE)
        fileHandler.setFormatter(CustomFormatter(use_color))
        rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(CustomFormatter(use_color))
    rootLogger.addHandler(consoleHandler)

    return rootLogger


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

            if int(ids[0]) in events[:, 2]:
                event_id[label] = int(ids[0])
                range_map[label] = ids
                
        else:
            if not int(id_value) in events[:, 2]:
                continue
            event_id[label] = int(id_value)

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
    for key, module in enumerate(modules):
        mod_name = module.__class__.__name__
        i = 2
        while mod_name in mod_list:
            mod_name = f"{module.__class__.__name__}_{str(i)}"
            i += 1
        module.save_config(
            path=config_path,
            cfg_label=mod_name,
            order=key)
        mod_list.append(mod_name)


def path_representer(dumper, obj):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


class YamlDumper(yaml.dumper.SafeDumper):
    standalone_module = False
    # also solves ' !!python/tuple' constructor, not sure why though
    pass

yaml.add_representer(
    type(Path()),
    path_representer,
    YamlDumper,
)


def _parse_config_lines(lines):
    keys = [x.strip(' :\n') for x in lines if len(x)>0 and x[0] not in ['-', '#', ' '] and len(x.strip())>0]
    multiples = [item for item, count in collections.Counter(keys).items() if count > 1]

    if len(multiples) > 0:
        raise KeyError(f"Your config-file has duplicate module keys: {'; '.join(multiples)}.")

    try:
        config = yaml.load("\n".join(lines), Loader=Loader)
    except yaml.YAMLError as e:
        logger.error("Error while reading YAML: %s" % str(e))
        return {}

    return config

def read_config_file(path):
    if path is None:
        return {}

    if not Path(path).exists:
        raise FileNotFoundError(f"'{save_path}' does not exist")

    with open(path, 'r') as f:
        lines = f.readlines()

    return _parse_config_lines(lines)

def read_config_string(data):
    if data is None:
        return {}

    return _parse_config_lines(data.strip().split("\n"))
