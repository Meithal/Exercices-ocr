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


def execute_input(chaine, carte):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param carte: La carte
    :param chaine: une chaine de caractères demandée par le joueur
              les formats valides sont "n/s/e/o(2-9)"
              "pn/s/e/o" ou "mn/s/e/o"
    :return: Un Tuple contenant la validité de l'instruction, si faux le joueur peut en demander une nouvelle
             un Emplacement cible,
             un contenu (None si l'emplacement n'est pas altéré) et
             l'instruction (On saura si on doit se deplacer sur la cible)
    """

    instruction, direction, repetitions, valide = dechiffre_input(chaine)

    contenu = None
    cible = carte.emplacements[carte.joueur_actif.position.index_]

    for step in range(repetitions):  # on répete le deplacement autant de fois que demande

        destination = carte.emplacements[{
            'n': cible.index_ - carte.taille_ligne,
            's': cible.index_ + carte.taille_ligne,
            'e': cible.index_ + 1,
            'o': cible.index_ - 1
        }[direction]]  # en fonction de la direction demandée, la destination sera differente

        if instruction is Instruction.deplacer:
            if not destination.est_valide(depuis=carte.joueur_actif.position):
                break  # si on cogne contre un mur, le tour se finit

        if instruction in {Instruction.murer, Instruction.percer}:

            if destination.contenu not in {regles.CARACTERE_MUR, regles.CARACTERE_PORTE}:
                valide = False
                break

            if instruction is Instruction.murer:
                contenu = regles.CARACTERE_MUR
            elif instruction is Instruction.percer:
                contenu = regles.CARACTERE_PORTE

        cible = destination

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
                        broadcast(carte, "Bienvenue au nouveau joueur sur le port %d\n" % nouveau_joueur.port)
                        nouveau_joueur.message(nouveau_joueur.affiche_carte())

                    else:
                        print("impossible d'ajouter un nouveau joueur")

            for joueur, message in carte.joueurs_bavards():
                print(joueur.port, ": ", message)
                if message == lib_reseau.ConnexionPerdue:
                    carte.joueurs.remove(joueur)
                    broadcast(carte, "Nous avons perdu la connexion avec le joueur %d" % joueur.numero())
                if not carte.partie_commencee():
                    if message == regles.CHAINE_COMMENCER:
                        joueur.est_pret = True
                        carte.joueur_actif = passer_au_joueur(carte, joueur)
                        broadcast(carte, "La partie commence, c'est au joueur %d de jouer" % carte.joueur_actif.numero())
                elif joueur is carte.joueur_actif:

                    valide, cible, contenu, instruction = execute_input(message, carte)

                    if valide:
                        if cible.fait_gagner():
                            joueur.gagnant = True
                            broadcast(carte, "Le joueur %d a gagné !" % joueur.numero())
                            continue

                        joueur.message("Mouvement valide, fin de votre tour")
                        if contenu:
                            cible.contenu = contenu
                        if instruction is Instruction.deplacer:
                            joueur.position = cible

                        carte.joueur_actif = passer_au_joueur(carte, next(carte.cycle_joueurs))
                    else:
                        joueur.message("Mouvement illégal, veuillez recommencer")
                        joueur.message(carte.afficher(joueur.position.index_))

        print("Merci d'avoir joué")
        return


def passer_au_joueur(carte, joueur):
    """Effectue quelques effets de bord lors du changement de joueur, comme l'envoi de notifications"""
    joueur.message("C'est à vous de jouer")
    joueur.message(carte.afficher(joueur.position.index_))
    return joueur


def broadcast(carte, message):
    """Envoye le même message à tous les joueurs connectés"""
    for joueur in carte.joueurs:
        joueur.message(message)