class Carte:

    def __init__(self):
        self.loaded = False

    def affiche(self):
        """
        Affiche la carte, saute une ligne quand on a affiché un nombre de caractères équivalent  une ligne
        :return:
        """
        for (i, c) in enumerate(self.flux):
            if i == self.place_joueur.index_:
                print(regles.CARACTERE_JOUEUR, end='')
            else:
                print(c, end='')
            if (i + 1) % self.taille_ligne == 0:
                print(end='\n')
        print(end='\n')

    def save(self):
        """
        Sauvegarde la carte en cours, le nom de la carte, et l'emplacement du jouer sont sauvegardées
        et séparées par une ligne.
        :return:
        """
        with open(regles.SAVE_FILE, 'w') as f:
            f.write(self.nom + "\n" + str(self.place_joueur.index_))


    def load_level(self, nom, place_joueur = -1):
        """Charge la carte donnée depuis un nom de fichier, positionne le joueur.

        Calcule la longueur d'une ligne, enlève tous les saut des lignes pour avoir un flux d'octets continu.
        Trouve les coordonnées du joueur et les sauvegarde.
        Enlève le sprite du jouer du flux
        :param nom: nom de la carte qu'on utilisera dans la fichier de sauvegarde.
        :param place_joueur: si supérieur à 0, force à celà l'emplacement du joueur, sinon
        la position du joueur sera celle par défaut. Permet de reprendre une partie en cours.
        """

        with open('cartes/' + nom) as texte:
            self.flux = texte.read()
        self.nom = nom
        self.taille_ligne = len(self.flux.split("\n")[0].strip())
        self.flux = self.flux.replace('\n', '').replace('\r', '')
        self.place_joueur = self.flux.index(regles.CARACTERE_JOUEUR)
        self.flux = self.flux.replace(regles.CARACTERE_JOUEUR, ' ')
        if place_joueur >= 0:
            self.place_joueur = place_joueur
        self.place_joueur = regles.emplacement.Emplacement(self.place_joueur, self.taille_ligne)

        self.loaded = True

import regles
# import regles.emplacement