# executer avec "py -3 .\roboc.py"
# Pour Openclass rooms

import os
import abc

SAVE_FILE = 'cur.txt'   # ce fichier sera utilis� pour sauvegarder la partie
LEGAL_CHARS = ' O.XU'   # rajouter des caract�res ici pour enrichir le jeu
BLOCKING_CHARS = 'O'    # rajouter des caract�res dans cette chaine pour creer des bloqueurs
VICTORY_CHARS = 'U'     # les caract�res de cette chaine font gagner
CARACTERE_JOUEUR = 'X'  # caractere qu'on recherche pour determiner la position initiale et comme 'sprite'

VALID_INPUT_CHARS = 'QNSEO23456789'
LONGUEUR_MAX_INPUT = 100


class DriverAffichage:

    @staticmethod
    @abc.abstractmethod
    def afficher(flux, longueur_colonne, position_joueur):
        """
        :param flux: un flux de caract�res � afficher
        :param longueur_colonne: sauter une ligne a chaque fois
        qu'on a affich� ce nombre de caract�res
        :param position_joueur: afficher le joueur � cette position
        :return: rien
        """
        pass


class AffichageASCII(DriverAffichage):
    """Ce driver affiche le jeu en mode ASCII"""
    @staticmethod
    def afficher(flux, longueur_colonne, position_joueur):
        for (i, c) in enumerate(flux):
            if i == position_joueur:
                print(CARACTERE_JOUEUR, end='')
            else:
                print(c, end='')
            if not (i + 1) % longueur_colonne:
                print()
        print()


class Jeu:

    driver_affichage = None
    cartes = []
    labyrinthe = None

    class Labyrinthe:
        def __init__(self, texte, nom):

            self.id = len(Jeu.cartes)

            self.flux = texte
            self.nom = nom

            self.longueur_colonne = len(self.flux.split("\n")[0].strip())

            for l in self.flux:
                if l not in LEGAL_CHARS:
                    self.flux = self.flux.replace(l, '')

            self.position_initiale = self.flux.index(CARACTERE_JOUEUR)
            self.flux = self.flux.replace(CARACTERE_JOUEUR, ' ')

            self.position_joueur = self.position_initiale

        def save(self):
            with open(SAVE_FILE, 'w') as f:
                f.write(self.nom + "\n" + str(self.position_joueur))

    @staticmethod
    def afficher():
        Jeu.driver_affichage.afficher(
            Jeu.labyrinthe.flux,
            Jeu.labyrinthe.longueur_colonne,
            Jeu.labyrinthe.position_joueur
        )

    @staticmethod
    def execute_input(i):
        """
        Cette procedure modifie l'�tat du jeu apr�s avoir filtr� son input
        :param i: L'input g�n�r� par le joueur
        :return: Si on retourne True, on demande un autre input au joueur, si on retourne False, le jeu s'�teint
        """
        i = i.strip().upper()
        i = i[:LONGUEUR_MAX_INPUT]
        for c in i:
            if c not in VALID_INPUT_CHARS:
                i = i.replace(c, '')
        if i == 'Q':
            return False
        if not i or i[0] not in 'NSEO':
            return True

        coord = i[0]  # N, S, E ou O
        combien_de_fois = 1
        if len(i) == 2 and i[1] in '23456789':
            combien_de_fois = int(i[1])

        for _ in range(combien_de_fois):
            destinations = {
                'N': Jeu.labyrinthe.position_joueur - Jeu.labyrinthe.longueur_colonne,
                'S': Jeu.labyrinthe.position_joueur + Jeu.labyrinthe.longueur_colonne,
                'E': Jeu.labyrinthe.position_joueur + 1,
                'O': Jeu.labyrinthe.position_joueur - 1
            }
            if destinations[coord] < 0 or destinations[coord] > len(Jeu.labyrinthe.flux):
                return True
            if Jeu.labyrinthe.flux[destinations[coord]] in BLOCKING_CHARS:
                return True
            elif Jeu.labyrinthe.flux[destinations[coord]] in VICTORY_CHARS:
                print("Vous avez gagn� !")
                os.unlink(SAVE_FILE)
                return False
            else:
                Jeu.labyrinthe.position_joueur = destinations[coord]
                if _ < combien_de_fois - 1:
                    Jeu.afficher()
                Jeu.labyrinthe.save()
        return True

    @staticmethod
    def charger_cartes():
        for f in os.listdir('cartes'):
            with open('cartes/' + f) as carte:
                Jeu.cartes.append(Jeu.Labyrinthe(carte.read(), f))

    @staticmethod
    def charger_sauvegarde(fichier):
        with open(fichier) as f:
            try:
                nom, place = f.read().split("\n")
                Jeu.labyrinthe = next(_ for _ in Jeu.cartes if _.nom == nom)
                Jeu.labyrinthe.position_joueur = int(place)
            except (IndexError, ValueError):
                print("Un probl�me est survenu en essayant de charger votre sauvegarde.")
                os.unlink(fichier)
                Jeu.labyrinthe = None

    @staticmethod
    def commencer():
        Jeu.afficher()
        while Jeu.execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n> ")):
            Jeu.afficher()


if __name__ == "__main__":
    Jeu.driver_affichage = AffichageASCII()
    Jeu.charger_cartes()
    if not len(Jeu.cartes):
        print("Aucune carte trouv�e.")
        exit()
    if SAVE_FILE in os.listdir('.'):
        if input("Voulez-vous continuer la partie en cours ? (O/N)\n> ").strip().upper() == 'O':
            Jeu.charger_sauvegarde(SAVE_FILE)
    if Jeu.labyrinthe is None:
        print("Veuillez choisir une carte")
        for _ in Jeu.cartes:
            print("[{}] {}".format(_.id + 1, _.nom.replace('.txt', '')))
        try:
            Jeu.labyrinthe = Jeu.cartes[int(input()) - 1]
        except (ValueError, IndexError):
            Jeu.labyrinthe = Jeu.cartes[0]

    Jeu.commencer()
