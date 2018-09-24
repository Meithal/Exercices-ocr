import random
import libs.lib_reseau as lib_res


class Joueur:
    def __init__(self, carte):

        self.connexion = None
        self.addresse = None
        self.port = None

        self.serveur = None

        self.carte = carte
        self.position = None

        self.est_pret = False

        self.position = random.choice(list(self.carte.departs_valides()))

    def __hash__(self):
        return self.position.index_

    def __eq__(self, other):
        return self.connexion.socket is other

    def connecter(self, connexion):
        self.connexion = connexion
        self.addresse = self.connexion.socket.getpeername()[0]
        self.port = self.connexion.socket.getpeername()[1]

    def message(self, contenu):
        self.connexion.envoyer(contenu)

    def affiche_carte(self):
        return self.carte.afficher(self.position.index_)
