import jeu


class Carte:
    """
    L'aire de jeu.

    Pour changer de niveau ou simplement commencer le jeu, il faut appeller load_level().
    """

    def __init__(self):
        """Des valeurs fausses pour éviter les warnings de l'éditeur"""
        self.loaded = False
        self.flux = ""
        self.position_par_defaut = jeu.emplacement.Emplacement(-1, 1)

    def affiche_serveur(self):
        """
        Affiche la carte, saute une ligne quand on a affiché un nombre de caractères équivalent  une ligne
        :return:
        """
        for (i, c) in enumerate(self.flux):
            if i == self.position_par_defaut.index_:
                print(jeu.reglages.CARACTERE_JOUEUR, end='')
            else:
                print(c, end='')
            if (i + 1) % self.taille_ligne == 0:
                print(end='\n')
        print(end='\n')

    def load_level(self, nom):
        """Charge la carte donnée depuis un nom de fichier, positionne le joueur.

        Calcule la longueur d'une ligne, enlève tous les saut des lignes pour avoir un flux d'octets continu.
        Trouve les coordonnées du joueur et les sauvegarde.
        Enlève le sprite du jouer du flux
        Une fois l'index numérique du joueur trouvé, le remplace par un objet Emplacement

        :param nom: nom de la carte qu'on utilisera dans la fichier de sauvegarde.
        :param place_joueur: si supérieur à 0, force à celà l'emplacement du joueur, sinon
        la position du joueur sera celle par défaut. Permet de reprendre une partie en cours.
        """

        with open('cartes/' + nom) as texte:
            self.flux = texte.read()
        self.nom = nom
        self.taille_ligne = len(self.flux.splitlines()[0].strip())
        self.flux = self.flux.replace('\n', '').replace('\r', '')
        self.position_par_defaut = self.flux.index(jeu.reglages.CARACTERE_JOUEUR)
        self.flux = self.flux.replace(jeu.reglages.CARACTERE_JOUEUR, ' ')
        self.position_par_defaut = jeu.emplacement.Emplacement(self.position_par_defaut, self.taille_ligne)

        self.loaded = True
