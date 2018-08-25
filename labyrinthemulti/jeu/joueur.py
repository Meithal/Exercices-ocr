import jeu
import random


class Joueur:
    def __init__(self, carte):

        self.connexion = None
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
        return self.connexion.socket is other

    def connecter(self, connexion):
        self.connexion = connexion
        self.addresse = self.connexion.socket.getpeername()[0]
        self.port = self.connexion.socket.getpeername()[1]

    def deconnecter(self):
        self.connexion = None
        self.addresse = None
        self.port = None

        self.serveur = None

    def pop_clavier_buffer(self):
        rv = self.buffer_clavier.decode("utf-8")
        self.buffer_clavier = bytes()
        return rv
