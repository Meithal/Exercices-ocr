import jeu


class Carte:
    """
    L'aire de jeu.

    Pour changer de niveau ou simplement commencer le jeu, il faut appeller load_level().
    """

    def __init__(self, nom):
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
        self.flux = self.flux.replace('\n', '').replace('\r', '').strip()
        self.position_par_defaut = self.flux.index(jeu.reglages.CARACTERE_JOUEUR)
        self.flux = self.flux.replace(jeu.reglages.CARACTERE_JOUEUR, ' ')

        self.emplacements = [
            jeu.Emplacement(index, value, self) for index, value in enumerate(self.flux)
        ]

        self.position_par_defaut = self.emplacements[self.position_par_defaut]

        self.joueurs = []

    # def ajoute_joueur(self, socket):
    #     if self.partie_commencee:
    #         return False
    #     nouveau_joueur = jeu.joueur.Joueur(socket)
    #     if not nouveau_joueur.position:
    #         print("Il n'y a plus assez de place pour ajouter un joueur sur cette carte")
    #         return -1
    #     else:
    #         self.joueurs.append(nouveau_joueur)
    #         return len(self.joueurs) - 1

    def partie_commencee(self):
        return any([joueur.est_pret for joueur in self.joueurs])

    def afficher(self, pos_joueur = -1):
        """
        Affiche la carte, saute une ligne quand on a affiché un nombre de caractères équivalent  une ligne
        :return: string
        """
        idx_joueur = 1
        string = ""
        for (i, c) in enumerate(self.flux):
            if i in [joueur.position.index_ for joueur in self.joueurs]:
                if pos_joueur == -1:
                    string += str(idx_joueur)
                    idx_joueur += 1
                else:
                    if pos_joueur == i:
                        string += "X"
                    else:
                        string += "x"
            else:
                string += c
            if (i + 1) % self.taille_ligne == 0:
                string += '\n'
        string += '\n'
        return string
