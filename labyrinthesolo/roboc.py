# executer avec "py -3 .\roboc.py"
# Pour Openclass rooms

import os

SAVE_FILE = 'cur.txt'   # ce fichier sera utilisé pour sauvegarder la partie
LEGAL_CHARS = ' O.XU'   # rajouter des caractères ici pour enrichir le jeu
BLOCKING_CHARS = 'O'    # rajouter des caractères dans cette chaine pour creer des bloqueurs
VICTORY_CHARS = 'U'     # les caractères de cette chaine font gagner
CARACTERE_JOUEUR = 'X'  # caractere qu'on recherche pour determiner la position initiale et comme 'sprite'

VALID_INPUT_CHARS = 'QNSEO23456789'
LONGUEUR_MAX_INPUT = 100


class Labyrinthe:
    def __init__(self, texte, nom):

        self.flux = texte
        self.nom = nom

        self.longueur_colonne = len(self.flux.split("\n")[0].strip())

        for l in self.flux:
            if l not in LEGAL_CHARS:
                self.flux = self.flux.replace(l, '')

        self.position_initiale = self.flux.index(CARACTERE_JOUEUR)
        self.flux = self.flux.replace(CARACTERE_JOUEUR, ' ')

        self.position_joueur = self.position_initiale

    def affiche(self):
        for (i, c) in enumerate(self.flux):
            if i == self.position_joueur:
                print(CARACTERE_JOUEUR, end='')
            else:
                print(c, end='')
            if not (i + 1) % self.longueur_colonne:
                print()
        print()

    def save(self):
        with open(SAVE_FILE, 'w') as f:
            f.write(self.nom + "\n" + str(self.position_joueur))


class Jeu:

    co = None
    cartes = []

    @staticmethod
    def execute_input(i):
        """
        Cette procedure modifie l'état du jeu après avoir filtré son input
        :param i: L'input généré par le joueur
        :return: Si on retourne True, on demande un autre input au joueur, si on retourne False, le jeu s'éteint
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
                'N': Jeu.co.position_joueur - Jeu.co.longueur_colonne,
                'S': Jeu.co.position_joueur + Jeu.co.longueur_colonne,
                'E': Jeu.co.position_joueur + 1,
                'O': Jeu.co.position_joueur - 1
            }
            if destinations[coord] < 0 or destinations[coord] > len(Jeu.co.flux):
                return True
            if Jeu.co.flux[destinations[coord]] in BLOCKING_CHARS:
                return True
            elif Jeu.co.flux[destinations[coord]] in VICTORY_CHARS:
                print("Vous avez gagné !")
                os.unlink(SAVE_FILE)
                return False
            else:
                Jeu.co.position_joueur = destinations[coord]
                if _ < combien_de_fois - 1:
                    Jeu.co.affiche()
                Jeu.co.save()
        return True

    @staticmethod
    def commencer():
        for f in os.listdir('cartes'):
            with open('cartes/' + f) as carte:
                Jeu.cartes.append(Labyrinthe(carte.read(), f))

        if SAVE_FILE in os.listdir('.'):
            if input("Voulez-vous continuer la partie en cours ? (O/N)\n> ").strip().upper() == 'O':
                with open(SAVE_FILE) as f:
                    try:
                        nom, place = f.read().split("\n")

                        Jeu.co = Jeu.cartes[nom]
                        Jeu.co.position_joueur = place
                    except (IndexError, ValueError):
                        print("Un problème est survenu en essayant de charger votre sauvegarde")
                        Jeu.co = None
        if Jeu.co is None:
            print("Veuillez choisir une carte")
            for _, c in enumerate(Jeu.cartes):
                print("[{}] {}".format(_ + 1, c.nom.replace('.txt', '')))

            try:
                selected_carte = Jeu.cartes[int(input()) - 1]
            except ValueError:
                selected_carte = Jeu.cartes[0]

            Jeu.co = selected_carte

        Jeu.co.affiche()
        while Jeu.execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n> ")):
            Jeu.co.affiche()


if __name__ == "__main__":
    Jeu.commencer()
