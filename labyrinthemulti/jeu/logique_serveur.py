import os
import enum
import random

import jeu.reglages as regles
from jeu.carte import Carte
from jeu.joueur import Joueur
from libs import lib_reseau


class Instruction(enum.Enum):
    deplacer = 1
    percer = 2
    murer = 3

def dechiffre_input(chaine):
    """
    Dechiffre une requete de type "n4", "pe" vers un tuple décrivant l'action,
    la direction et le nombre de répétitions
    :param chaine: String
    :return: Tuple
    """

    chaine = chaine[:regles.LONGUEUR_MAX_INPUT].strip().lower()
    valide = True

    if not chaine:
        valide = False

    instruction = {
        'p': Instruction.percer,
        'm': Instruction.murer
    }.get(chaine[0], Instruction.deplacer)

    if instruction in {Instruction.percer, Instruction.murer}:
        if len(chaine) != 2:
            valide = False
        direction = chaine[1]
    else:
        direction = chaine[0]

    if direction not in 'nseo':
        valide = False

    repetitions = 1
    if instruction == Instruction.deplacer and len(chaine) == 2 and chaine[1] in '23456789':
        repetitions = int(chaine[1])

    return instruction, direction, repetitions, valide


def execute_input(chaine, ct):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param ct: La carte
    :param chaine: une chaine de caractères demandée par le joueur
              les formats valides sont "n/s/e/o(2-9)"
              "pn/s/e/o" ou "mn/s/e/o"
    :return: Un Tuple contenant la validité de l'instruction,
             un Emplacement cible,
             un contenu (None si l'emplacement n'est pas altéré) et
             l'instruction (On saura quoi faire avec la cible)
    """

    instruction, direction, repetitions, valide = dechiffre_input(chaine)

    contenu = None

    for step in range(repetitions):  # on répete le deplacement autant de fois que demande

        destination = {
            'n': ct.joueur_actif.position.index_ - ct.taille_ligne,
            's': ct.joueur_actif.position.index_ + ct.taille_ligne,
            'e': ct.joueur_actif.position.index_ + 1,
            'o': ct.joueur_actif.position.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = ct.emplacements[destination]

        if instruction in {Instruction.murer, Instruction.percer}:

            if cible.contenu not in {regles.CARACTERE_MUR, regles.CARACTERE_PORTE}:
                valide = False
                break

            if instruction == Instruction.murer:
                contenu = regles.CARACTERE_MUR
            elif instruction == Instruction.percer:
                contenu = regles.CARACTERE_PORTE
            break

        if not cible.est_valide(depuis=ct.joueur_actif.position):
            break  # si on cogne contre un mur, le tour se finit

        # if cible.fait_gagner():
        #     return InstructionCheck.A_GAGNE

        # ct.joueur_actif.position = cible  # l'état du jeu est modifié ici

        # if step < repetitions - 1:
        #     ct.afficher()  # on affiche les déplacements intermédiaires

    return valide, cible, contenu, instruction


def serveur():
    """La boucle principale du jeu"""

    cartes = []  # une liste de nom de cartes

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

    with lib_reseau.ConnexionEnTantQueServeur(
        '',
        regles.PORT_CONNEXION,
        "Connexion principale"
    ) as serveur:

        if not serveur:
            print("Echec de connexion avec le serveur")
            return

        carte = Carte(cartes[selected_carte], serveur)  # l'instance de Carte où on joue

        print(carte.afficher())

        while not carte.gagnant():

            if not carte.partie_commencee():
                nouvelle_connexion = next(serveur.nouvelles_connexions())
                if nouvelle_connexion:
                    nouveau_joueur = Joueur(carte)
                    if nouveau_joueur.position:
                        nouveau_joueur.connecter(nouvelle_connexion)
                        print("Nouveau joueur ajouté à la carte sur port {}".format(nouveau_joueur.port))
                        carte.joueurs.append(nouveau_joueur)
                        for c in carte.connexions_des_clients():
                            c.envoyer("Bienvenue au nouveau joueur sur le port %d\n" % nouveau_joueur.port)
                        nouveau_joueur.message(nouveau_joueur.affiche_carte())
                    else:
                        print("impossible d'ajouter un nouveau joueur")

            if carte.joueurs:
                for joueur, message in carte.joueurs_bavards():
                    print(joueur.port, ": ", message)
                    if message == "ERROR":
                        carte.joueurs.remove(joueur)
                        continue
                    if not carte.partie_commencee():
                        if message == regles.CHAINE_COMMENCER:
                            joueur.est_pret = True
                            carte.joueur_actif = carte.prochain_joueur()
                    elif joueur is carte.joueur_actif:
                        valide, cible, contenu, instruction = execute_input(message, carte)
                        if valide:
                            if contenu:
                                cible.contenu = contenu
                            if instruction == Instruction.deplacer:
                                joueur.position = cible

                            carte.joueur_actif = carte.prochain_joueur()
                        else:
                            joueur.message("Mouvement illégal, veuillez recommencer")

                        if cible.fait_gagner():
                            for c in carte.connexions_des_clients():
                                c.envoyer("Le joueur %d a gagné !" % (carte.joueurs.index(carte.joueur_actif) + 1))
                            print("Merci d'avoir joué")
                            return
