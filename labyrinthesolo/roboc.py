# executer avec "py -3 .\roboc.py"
# Pour Openclass rooms

import os, re

SAVE_FILE = 'cur.txt'  # ce fichier sera utilisé pour sauvegarder la partie
LEGAL_CHARS = ' O.XU'  # rajouter des caractères ici pour enrichir le jeu
BLOCKING_CHARS = 'O'   # rajouter des caractères dans cette chaine pour creer des bloqueurs
VICTORY_CHARS = 'U'    # les caractères de cette chaine font gagner
CARACTERE_JOUEUR = 'X' # ce caractère sera affiché à la position du joueur et recherché pour déterminer sa position initiale

VALID_INPUT_CHARS = 'QNSEO23456789'
LONGUEUR_MAX_INPUT = 100

class Carte:
    def __init__(self, texte, nom, place_joueur = -1):
        """
        Calcule la longueur d'une colonne (par rapport au premier saut de ligne rencontré),
        Enlève tous les sauts de ligne et les caractères illégaux,
        Definit éventuellement les coordonnées initiales du joueur.
        Enlève la caractère qui correspond au joueur.
        :param texte: contenu brut du fichier
        :param nom: nom de la carte incluse dans la sauvegarde
        :param place_joueur: si different de 0, force à celà l'emplacement du joueur
        """
        self.raw = texte
        self.nom = nom
        self.longueur_colonne = len(self.raw.split("\n")[0].strip())
        for l in self.raw:
            if l not in LEGAL_CHARS:
                self.raw = self.raw.replace(l, '')
        if place_joueur == -1:
            self.place = self.raw.index(CARACTERE_JOUEUR)
        else:
            self.place = int(place_joueur)
        self.raw = self.raw.replace(CARACTERE_JOUEUR, ' ')


    def affiche(self):
        """
        Rien d'exceptionnel sinon qu'on saute une ligne à
        chaque fois qu'on affiche un nombre de caractères
        équivalent à self.longueur_colonne
        :return:
        """
        for (i, c) in enumerate(self.raw):
            if i == self.place:
                print(CARACTERE_JOUEUR, end = '')
            else:
                print (c, end = '')
            if not (i + 1) % self.longueur_colonne:
                print()
        print()

    def save(self):
        """
        On sauvegarde juste le nom de la map et la position
        Ce qui fait que quand on charge la carte on passera
        cette position dans le constructeur.
        :return:
        """
        with open(SAVE_FILE, 'w') as f:
            f.write(self.nom + "\n" + str(self.place))

def execute_input(i):

    # on filtre l'entrée
    i = i.strip().upper()
    i = i[:LONGUEUR_MAX_INPUT]
    for c in i:
        if c not in VALID_INPUT_CHARS:
            i = i.replace(c, '')
    if i == 'Q':
        return False
    if not i or i[0] not in 'NSEO':
        return True

    # on recupère la direction et le nombre de fois qu'on veut se déplacer
    # depuis l'entrée filtrée
    dir = i[0]
    combien_de_fois = 1
    if len(i) == 2 and i[1] in '23456789':
        combien_de_fois = int(i[1])

    # on teste la validité du déplacement, si il est correct, on l'exécute
    for _ in range(combien_de_fois):
        dests = {
            'N': co.place - co.longueur_colonne,
            'S': co.place + co.longueur_colonne,
            'E': co.place + 1,
            'O': co.place - 1
        }
        if dests[dir] < 0 or dests[dir] > len(co.raw):
            return True
        if co.raw[dests[dir]] in BLOCKING_CHARS:
            return True
        elif co.raw[dests[dir]] in VICTORY_CHARS:
            print("Vous avez gagné !")
            os.unlink(SAVE_FILE)
            return False
        else:
            co.place = dests[dir]
            if _ < combien_de_fois - 1:
                co.affiche()
            co.save()
    return True


co = None
cartes = []

if SAVE_FILE in os.listdir('.'):
    if input("Voulez-vous continuer la partie en cours ? (O/N)\n> ").strip().upper() == 'O':
        with open(SAVE_FILE) as f:
            try:
                nom, place = f.read().split("\n")
                co = Carte(open('cartes/' + nom).read(), nom, place)
            except:
                co = None
if co is None:
    print("Veuillez choisir une carte")
    i = 0
    for f in os.listdir('cartes'):
        with open('cartes/' + f) as carte:
            cartes.append(Carte(carte.read(), f))
        print("[{}] {}".format(i + 1, f[:-4]))
        i += 1

    selected_carte = min(max(int(re.sub(r"\D", "0", input("") or '1')), 1), i)
    co = cartes[selected_carte - 1]

co.affiche()
while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n> ")):
    co.affiche()