import select
import sys
import threading

verrou = threading.RLock()


class Afficheur(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.run()
        self._coro = None

    def run(self):
        self._coro = self.coro()
        self._coro.send(None)

    @staticmethod
    def coro():
        while True:
            trucs = yield
            with verrou:
                print(trucs)

    def show(self, things):
        self._coro.send(things)
