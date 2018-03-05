# Pour Openclass rooms

import os
import regles_du_jeu as regles

cartes = []
co = None  # l'objet carte où on va jouer

class Carte:
    def __init__(self, nom, place_joueur = -1):
        """
        Charge la carte en mémoire
        Calcule la longueur d'une ligne, enlève tous les saut des lignes pour avoir un flux d'octets continu.
        Definit les coordonnées du joueur et les sauvegarde.
        :param nom: nom de la carte qu'on utilisera dans la fichier de sauvegarde.
        :param place_joueur: si supérieur à 0, force à celà l'emplacement du joueur, sinon
        la position du joueur sera celle par défaut.
        """
        with open('cartes/' + nom) as texte:
            self.flux = texte.read()
        self.nom = nom
        self.taille_ligne = len(self.flux.split("\n")[0].strip())
        self.flux = self.flux.replace('\n', '').replace('\r', '')
        self.place_joueur = self.flux.index(regles.CARACTERE_JOUEUR)
        self.flux = self.flux.replace(regles.CARACTERE_JOUEUR, ' ')
        regles.carte = self
        if place_joueur >= 0:
            self.place_joueur = place_joueur

    def affiche(self):
        """
        Affiche la carte, saute une ligne quand on a affiché un nombre de caractères équivalent  une ligne
        :return:
        """
        for (i, c) in enumerate(self.flux):
            if i == self.place_joueur:
                print(regles.CARACTERE_JOUEUR, end = '')
            else:
                print(c, end = '')
            if not (i + 1) % self.taille_ligne:
                print(end='\n')
        print(end='\n')

    def save(self):
        with open(regles.SAVE_FILE, 'w') as f:
            f.write(self.nom + "\n" + str(self.place_joueur))

def execute_input(i):
    i = i[:regles.LONGUEUR_MAX_INPUT].strip().upper()
    if i == 'Q':
        return False
    repetitions = 1
    if len(i) == 2 and i[1] in '23456789':
        repetitions = int(i[1])
    direction = i[0]
    for step in range(repetitions):  # on se déplace autant de fois que demandé
        emplacement = regles.Emplacement({  # on crée une instance d'Emplacement vie l'index numérique trouvé dans le dictionnaire
            'N': co.place_joueur - co.taille_ligne,
            'S': co.place_joueur + co.taille_ligne,
            'E': co.place_joueur + 1,
            'O': co.place_joueur - 1
        }.get(direction, co.place_joueur))  # si la direction donnée n'est pas valide, la joueur reste sur place

        if not emplacement.est_valide():
            return True  # si le déplacement n'est pas valide, on quitte ici

        if emplacement.fait_gagner():
            print("Vous avez gagné !")
            os.unlink(regles.SAVE_FILE)
            return False

        co.place_joueur = emplacement()  # on deplace le joueur si on arrive jusqu'ici (via Emplacement.__call__())

        if step < repetitions - 1:
            co.affiche()  # on affiche les déplacements intermédiaires

        co.save()
    return True


if regles.SAVE_FILE in os.listdir('.'):
    if input("Voulez-vous continuer la partie en cours ? (O/N)").strip().upper() == 'O':
        with open(regles.SAVE_FILE) as f:
            nom, place = f.read().split("\n")
            co = Carte(nom, int(place))
if co is None:
    print("Veuillez choisir une carte")
    i = 0
    for f in os.listdir('cartes'):
        cartes.append(f)
        print("[{}] {}".format(i + 1, f.replace('.txt', '')))
        i += 1
    while True:
        selected_carte = input("> ")
        if selected_carte.isdigit() and int(selected_carte) - 1 in range(len(cartes)):
            selected_carte = int(selected_carte) - 1
            break
        else:
            print("Ce n'est pas valide")

    co = Carte(cartes[selected_carte])
    co.save()

co.affiche()
while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n")):
    co.affiche()