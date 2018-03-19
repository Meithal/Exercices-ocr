import sys
import threading

verrou = threading.RLock()


class Afficheur(threading.Thread):

    def __init__(self, mot):
        super().__init__(daemon=True)
        self.mot = mot

    def run(self):
        with verrou:
            sys.stdout.write(self.mot)
            sys.stdout.flush()

    def __call__(self, *args, **kwargs):
        with verrou:
            print(*args)

class Envoyeur(threading.Thread):

    def __init__(self, connexion):
        super(Envoyeur, self).__init__()
        self.connexion = connexion

    def run(self):
        with verrou:
            self.connexion.socket.send(b"Test connexion")
            msg_recu = self.connexion.socket.recv(1024).decode()
            print ("Test:", msg_recu)

afficheur = Afficheur("Coucou")
afficheur.start()

envoyeur = None