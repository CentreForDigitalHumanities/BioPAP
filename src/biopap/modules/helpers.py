import sys
from io import StringIO

class Capturing(list):

    """
        usage:
            with Capturing() as captured:
                func(arg)
        captures stdout from func() in var captured
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout