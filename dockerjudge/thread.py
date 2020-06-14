'Extentions for Lib/threading.py'

import threading

from .status import Status


class Thread(threading.Thread):
    'Subclass of threading.Thread with return value and callback'

    def __init__(self, callback, *args, **kwargs):
        self.return_value = (Status.UE, .0)
        self._callback = callback
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            try:
                self._callback(self._args[2] - 1, *self.return_value)
            except TypeError:
                pass
            finally:
                del self._target, self._args, self._kwargs, self._callback
