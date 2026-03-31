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


def custom_formatwarning(message, category, filename, *args, **kwargs):
    return f"{str(Path(filename).stem)}:{str(message)}"


def get_new_filename(filename, save_folder, save_postfix, save_overwrite):
    d_out = Path(save_folder)
    d_out.mkdir(parents=True, exist_ok=True)
    f_src = Path(filename)

    if save_postfix:
        f_new = Path(f_src.with_name(f'{f_src.stem}_{save_postfix}{f_src.suffix}').name)
    else:
        f_new = f_src.name

    p_out = d_out / f_new

    if not save_overwrite:
        i = 1
        while p_out.exists():
            if i>=999:
                raise ValueError(f"too many copies of '{filename}' already exist in '{save_folder}")
            p_out = d_out / f_new.with_name(f'{f_new.stem}_({i}){f_src.suffix}').name
            i += 1

    return p_out
