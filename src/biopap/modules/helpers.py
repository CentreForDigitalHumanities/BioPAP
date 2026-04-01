import sys
from pathlib import Path
from io import StringIO

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
