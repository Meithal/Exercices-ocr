import jeu
import random


class Joueur:
    def __init__(self, connexion):

        self.connexion = connexion
        self.sock = connexion.socket
        self.addresse = self.sock.getpeername()[0]
        self.port = self.sock.getpeername()[1]

        print ("On ajoute un joueur sur le port " + str(self.port))
        self.position = None
        for i in range(30):
            index_ = random.randrange(len(jeu.carte.flux))
            emplacement = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)
            if emplacement.est_valide():
                if emplacement.distance_vers_sortie_plus_proche() > 5:
                    self.position = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)

        self.buffer_clavier = bytes()

    def __eq__(self, other):
        return self.sock is other

    def pop_clavier_buffer(self):
        rv = self.buffer_clavier.decode("utf-8")
        self.buffer_clavier = bytes()
        return rv
