import jeu
import random


class Joueur:
    def __init__(self, carte):

        self.connexion = None
        self.sock = None
        self.addresse = None
        self.port = None

        self.serveur = None

        print("On ajoute un joueur sur le port " + str(self.port))
        self.carte = carte
        self.position = None

        self.est_pret = False

        self.position = random.choice(list(self.carte.departs()))

        self.buffer_clavier = bytes()

    def __eq__(self, other):
        return self.sock is other

    def __del__(self):
        self.serveur.kick_client(self.sock)
        # self.deconnecter()

    def connecter(self, connexion, serveur):
        self.connexion = connexion
        self.sock = connexion.socket
        self.addresse = self.sock.getpeername()[0]
        self.port = self.sock.getpeername()[1]

        self.serveur = serveur

    def deconnecter(self):
        self.connexion = None
        self.sock = None
        self.addresse = None
        self.port = None

        self.serveur = None

    def pop_clavier_buffer(self):
        rv = self.buffer_clavier.decode("utf-8")
        self.buffer_clavier = bytes()
        return rv
