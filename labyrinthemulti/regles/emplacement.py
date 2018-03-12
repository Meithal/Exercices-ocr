
class Emplacement:
    """
    Cette classe caracterise un emplacement au sein de la carte.
    """

    def __init__(self, index_, taille_ligne):
        """
        Comme la carte est un flux d'octets continu, on trouve sa ligne et
        colone par une division de la taille d'une ligne.
        :param index_: l'index numerique entier de cet emplacement, par rapport au flux.
        """
        self.index_ = index_
        self.ligne, self.colonne = divmod(index_, taille_ligne)

    def est_valide(self, depuis = None):
        """
        Verifie si cet emplacement est valide (pas dans un mur, en oob, etc.).
        :param depuis: un autre objet Emplacement qu'il faut pouvoir atteindre.
        :return: True ou False
        """
        if self.oob():
            return False
        if self.bloque():
            return False
        if depuis:
            if abs(self.colonne != depuis.colonne): # on demande un deplacement horizontal (colonne différente)
                if self.ligne != depuis.ligne: # mais on se retrouve au final sur une autre ligne...
                    return False # c'est possible car notre aire de jeu est un flux continu d'octets.
        return True

    def oob(self):
        """Cet emplacement n'est pas dans la limite de la carte."""
        return self.index_ < 0 or self.index_ > len(game.carte.flux)

    def bloque(self):
        """Cet emplacement contient un caractère bloquant."""
        if game.carte.flux[self.index_] in regles.BLOCKING_CHARS:
            return True
        return False

    def fait_gagner(self):
        """Cet emplacement contient un caractère qui fait gagner."""
        if game.carte.flux[self.index_] in regles.VICTORY_CHARS:
            return True
        return False

    # On peut rajouter d'autres fonctions ici comme "fait changer d'étage"

import game, regles
print ("submo", id(game.carte))
