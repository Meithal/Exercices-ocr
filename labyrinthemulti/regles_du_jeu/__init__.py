SAVE_FILE = 'cur.txt'
BLOCKING_CHARS = 'O'  # on peut rajouter des caractères ici pour ajouter des bloqueurs
VICTORY_CHARS = 'U'
CARACTERE_JOUEUR = 'X'
LONGUEUR_MAX_INPUT = 100

# la carte sur laquelle on va tester nos règles, il faut l'initialiser à la main dans le constructeur de la carte
carte = None


class Emplacement:

    def __init__(self, emplacement):
        """
        Un emplacement dans la flux de la carte
        :param emplacement: l'index numérique de cet emplacement, par rapport au flux
        """
        self.emplacement = emplacement

    def est_valide(self):  # le joueur peut-il se trouver ici?
        if self.oob():
            return False
        if self.bloque():
            return False
        return True

    def oob(self):  # cet emplacement est en dehors de la carte
        return self.emplacement < 0 or self.emplacement > len(carte.flux)

    def bloque(self):  # cet emplacement est compris dans les caratcères bloquants
        if carte.flux[self.emplacement] in BLOCKING_CHARS:
            return True
        return False

    def fait_gagner(self):  # cet emplacement fait gagner
        if carte.flux[self.emplacement] in VICTORY_CHARS:
            return True
        return False

    # retourne notre position sur la carte lorsqu'on nous appelle comme fonction
    def coordonnee(self):
        return self.emplacement