import jeu

class Joueur:
    def __init__(self, position):
        self.position = jeu.emplacement.Emplacement(position, jeu.carte.taille_ligne)
