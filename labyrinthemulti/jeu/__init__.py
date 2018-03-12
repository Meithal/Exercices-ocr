import os

import jeu.carte_  # on utilise deja le nom 'carte' pour stocker l'instance de Carte
import jeu.emplacement
import jeu.reglages

cartes = []  # une liste de nom de cartes
carte = jeu.carte_.Carte()  # l'instance de Carte où on joue


def execute_input(i):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param i: une chaine de caractères demandée par le joueur
    :return: True, le jeu continue, False, le jeu s'arrête
    """

    i = i[:jeu.reglages.LONGUEUR_MAX_INPUT].strip().upper()

    if i == 'Q':
        return False

    if not i:
        return True

    direction = i[0]

    if direction not in 'NSEO':
        return True

    repetitions = 1
    if len(i) == 2 and i[1] in '23456789':
        repetitions = int(i[1])

    for step in range(repetitions):  # on répete le deplacement autant de fois que demande

        destination = {
            'N': carte.place_joueur.index_ - carte.taille_ligne,
            'S': carte.place_joueur.index_ + carte.taille_ligne,
            'E': carte.place_joueur.index_ + 1,
            'O': carte.place_joueur.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = jeu.emplacement.Emplacement(destination, carte.taille_ligne)

        if not cible.est_valide(depuis=carte.place_joueur):
            return True  # si l'emplacement cible ne permet pas de s'y trouver, on quitte la procédure ici

        if cible.fait_gagner():
            print("Vous avez gagné !")
            os.unlink(jeu.reglages.SAVE_FILE)
            return False

        carte.place_joueur = cible  # l'état du jeu est modifié ici

        if step < repetitions - 1:
            carte.affiche()  # on affiche les déplacements intermédiaires

        carte.save()  # on sauvegarde chaque déplacement
    return True


def main():
    """La boucle principale du jeu"""
    if jeu.reglages.SAVE_FILE in os.listdir('.'):
        if input("Voulez-vous continuer la partie en cours ? (O/N)").strip().upper() == 'O':
            with open(jeu.reglages.SAVE_FILE) as f:
                nom, place = f.read().split("\n")
                carte.load_level(nom, int(place))

    if not carte.loaded:
        print("Veuillez choisir une carte")
        i = 1
        for f in os.listdir('cartes'):
            cartes.append(f)
            print("[{}] {}".format(i, f.replace('.txt', '')))
            i += 1
        while True:
            selected_carte = input("> ")
            if selected_carte.isdigit() and int(selected_carte) - 1 in range(len(cartes)):
                selected_carte = int(selected_carte) - 1
                break
            else:
                print("Ce n'est pas valide")

        carte.load_level(cartes[selected_carte])
        carte.save()

    carte.affiche()
    while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n")):
        carte.affiche()

    print("Merci d'avoir joué")