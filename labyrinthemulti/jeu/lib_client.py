import sys
import threading

verrou = threading.RLock()

class Afficheur(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.run()

    def run(self):
        self.coro().__next__()

    def coro(self):
        trucs = yield
        with verrou:
            print (trucs)


class Envoyeur(threading.Thread):

    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion
        self.run()

    def run(self):
        while True:
            with verrou:
                self.connexion.socket.send(b"Test connexion")
                msg_recu = self.connexion.socket.recv(1024).decode()
                print ("Test:", msg_recu)
