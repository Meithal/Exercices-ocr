import jeu
import random


class Joueur:
    def __init__(self, sock):

        self.sock = sock
        self.addresse = sock.getsockname()[0]
        self.port = sock.getsockname()[1]

        print ("On ajoute un joueur sur le port " + str(self.port))
        self.position = None
        for i in range(30):
            index_ = random.randrange(len(jeu.carte.flux))
            emplacement = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)
            if emplacement.est_valide():
                if emplacement.distance_vers_sortie_plus_proche() > 5:
                    self.position = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)

    def pop_buffer_clavier(self):
        return "bar"