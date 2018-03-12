import jeu


class Emplacement:
    """
    Cette classe caracterise un emplacement au sein de la carte.

    """

    def __init__(self, index_, taille_ligne):
        """
        Definit x et y dans la quadrillage, conserve l'index

        :param index_: la position au sein du flux de la carte.
        :param taille_ligne: utilisé comme modulo pour trouver la ligne et la colonne
        """
        self.index_ = index_
        self.ligne, self.colonne = divmod(index_, taille_ligne)  # equivalent a (index // taille_ligne, index_ % taille_ligne)

    def est_valide(self, depuis=None):
        """
        Verifie si cet emplacement est valide (pas dans un mur, hors limite, etc.).
        :param depuis: un autre objet Emplacement, dans le cas d'un deplacement.
        :return: True ou False
        """
        if self.oob():
            return False
        if self.bloque():
            return False
        if depuis:
            if abs(self.colonne != depuis.colonne):  # on demande un deplacement horizontal (colonne différente)
                if self.ligne != depuis.ligne:  # mais on se retrouve au final sur une autre ligne...
                    return False  # c'est possible car notre aire de jeu est un flux d'octets continu.
        return True

    def oob(self):
        """Cet emplacement n'est pas dans la limite de la carte."""
        return self.index_ < 0 or self.index_ > len(jeu.carte.flux)

    def bloque(self):
        """Cet emplacement contient un caractère bloquant."""
        if jeu.carte.flux[self.index_] in jeu.reglages.BLOCKING_CHARS:
            return True
        return False

    def fait_gagner(self):
        """Cet emplacement contient un caractère qui fait gagner."""
        if jeu.carte.flux[self.index_] in jeu.reglages.VICTORY_CHARS:
            return True
        return False

    # On peut rajouter d'autres fonctions ici comme "fait changer d'étage"
