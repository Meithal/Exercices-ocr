SAVE_FILE = 'cur.txt'  # le nom du fichier de sauvegarde
BLOCKING_CHARS = 'O'  # tous les caracteres de cette chaine bloqueront la progression du joueur
VICTORY_CHARS = 'U'  # marcher sur un des caracteres presents dans cette chaine fait gagner la partie
CARACTERE_JOUEUR = 'X'  # ce caractere sera recherche dans le flux de la carte pour determiner
                        # la position initiale du joueur, il sera affiché comme sprite du joueur
LONGUEUR_MAX_INPUT = 100

# la carte de jeu, alias
carte = None


class Emplacement:
    """
    Cette classe caracterise un emplacement au sein d'une carte
    """

    def __init__(self, index_):
        """
        Comme la carte est un flux d'octets continu, on trouve sa ligne et colone par une division de la taille d'une ligne
        :param index_: l'index numerique entier de cet emplacement, par rapport au flux
        """
        self.index_ = index_
        self.ligne, self.colonne = divmod(index_, carte.taille_ligne)

    def est_valide(self, depuis = None):
        """
        Verifie si cet emplacement est valide
        :param depuis: si cet emplacement est atteignable depuis celui la
        :return: True ou False
        """
        if self.oob():
            return False
        if self.bloque():
            return False
        if depuis:
            if abs(self.colonne != depuis.colonne): # deplacement horizontal
                if self.ligne != depuis.ligne: # qui nous teleporte sur une autre ligne
                    return False # retourne False
        return True

    def oob(self):
        """Cet emplacement n'est pas dans la limite de la carte"""
        return self.index_ < 0 or self.index_ > len(carte.flux)

    def bloque(self):
        """Cet emplacement contient un caractère bloquant"""
        if carte.flux[self.index_] in BLOCKING_CHARS:
            return True
        return False

    def fait_gagner(self):
        """Cet emplacement contient un caractère qui fait gagner"""
        if carte.flux[self.index_] in VICTORY_CHARS:
            return True
        return False