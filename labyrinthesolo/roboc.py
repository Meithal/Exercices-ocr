# Pour Openclass rooms

import os, re

SAVE_FILE = 'cur.txt'
LEGAL_CHARS = ' O.XU'
BLOCKING_CHARS = 'O'
VICTORY_CHARS = 'U'
CARACTERE_JOUEUR = 'X'
VALID_INPUT_CHARS = 'QNSEO23456789'
VALID_INPUT_PATTERN = '(Q|[NSEO][2-9]*)'
LONGUEUR_MAX_INPUT = 100

cartes = []

class Carte:
    def __init__(self, texte, nom, place_joueur = 0):
        """
        Calcule la longueur d'une colonne, enlève tous les caractères illégaux,
        Definit les coordonnées du joueur et les sauvegarde
        :param texte: contenu brut du fichier
        :param nom: nom de la carte incluse dans la sauvegarde
        :param place_joueur: si different de 0, force à celà l'emplacement du joueur
        """
        self.raw = texte
        self.nom = nom
        self.len_col = len(self.raw.split("\n")[0].strip())
        for l in self.raw:
            if l not in LEGAL_CHARS:
                self.raw = self.raw.replace(l, '')
        if not place_joueur:
            self.place = self.raw.index(CARACTERE_JOUEUR)
            self.raw = self.raw.replace(CARACTERE_JOUEUR, ' ')
        else:
            self.raw = self.raw.replace(CARACTERE_JOUEUR, ' ')
            self.place = int(place_joueur)

    def affiche(self):
        for (i, c) in enumerate(self.raw):
            if i == self.place:
                print(CARACTERE_JOUEUR, end = '')
            else:
                print (c, end = '')
            if not (i + 1) % self.len_col:
                print()

    def save(self):
        with open(SAVE_FILE, 'w') as f:
            f.write(self.nom + "\n" + str(self.place))

def execute_input(i):
    i = i.strip()
    i = i[:LONGUEUR_MAX_INPUT]
    for c in i:
        if c not in VALID_INPUT_CHARS:
            i = i.replace(c, '')
    if i == 'Q':
        return False
    if i[0] not in 'NSEO':
        return True
    else:
        if len(i) == 2 and i[1] in '23456789':
            cb = int(i[1])
        else:
            cb = 1
    dir = i[0]
    for step in range(cb):
        dests = {
            'N': co.place - co.len_col,
            'S': co.place + co.len_col,
            'E': co.place + 1,
            'O': co.place - 1
        }
        if dests[dir] < 0 or dests[dir] > len(co.raw) or co.raw[dests[dir]] in BLOCKING_CHARS:
            return True
        elif co.raw[dests[dir]] in VICTORY_CHARS:
            print("Vous avez gagné !")
            os.unlink(SAVE_FILE)
            return False
        else:
            co.place = dests[dir]
            co.save()
    return True

co = None

if SAVE_FILE in os.listdir('.'):
    if input("Voulez-vous continuer la partie en cours ? (O/N)").strip() == 'O':
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

    selected_carte = min(max(int(re.sub("\D", "0", input()), 10), 1), i)
    co = cartes[selected_carte - 1]
    co.save()

co.affiche()
while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n")):
    co.affiche()