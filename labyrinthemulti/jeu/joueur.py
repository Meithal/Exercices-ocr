import jeu
import random


class Joueur:
    def __init__(self, port):
        print ("On ajoute un joueur sur le port " + str(port))
        self.port = port
        self.position = None
        for i in range(30):
            index_ = random.randrange(len(jeu.carte.flux))
            emplacement = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)
            if emplacement.est_valide():
                if emplacement.distance_vers_sortie() > 5:
                    self.position = jeu.emplacement.Emplacement(index_, jeu.carte.taille_ligne)
