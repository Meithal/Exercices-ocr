import jeu
import random


class Joueur:
    def __init__(self, connexion, serveur, carte):

        self.connexion = connexion
        self.sock = connexion.socket
        self.addresse = self.sock.getpeername()[0]
        self.port = self.sock.getpeername()[1]

        self.serveur = serveur

        print("On ajoute un joueur sur le port " + str(self.port))
        self.carte = carte
        self.position = None

        self.est_pret = False

        self.position = random.randrange(self.carte.departs())

        self.buffer_clavier = bytes()

    def __eq__(self, other):
        return self.sock is other

    def __del__(self):
        self.serveur.kick_client(self.sock)

    def pop_clavier_buffer(self):
        rv = self.buffer_clavier.decode("utf-8")
        self.buffer_clavier = bytes()
        return rv
