import sys
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
