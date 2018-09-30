import os
import enum
import random

import jeu.reglages as regles
from jeu.carte import Carte
from jeu.joueur import Joueur
from libs import lib_reseau


class InstructionCheck(enum.Enum):
    ACTION_VALIDE = 1
    DOIT_RECOMMENCER = 2
    A_GAGNE = 3


def execute_input(i, ct):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param ct: La carte
    :param i: une chaine de caractères demandée par le joueur
    :return: True, le jeu continue, False, le jeu s'arrête
    """

    i = i[:regles.LONGUEUR_MAX_INPUT].strip().lower()

    if not i:
        return InstructionCheck.DOIT_RECOMMENCER

    deplacement = False

    if len(i) == 2 and i[0] in {'p', 'm'}:
        instruction, direction = i
    else:
        direction = i[0]
        deplacement = True

    if direction not in 'nseo':
        return InstructionCheck.DOIT_RECOMMENCER

    repetitions = 1
    if len(i) == 2 and i[1] in '23456789':
        repetitions = int(i[1])

    for step in range(repetitions):  # on répete le deplacement autant de fois que demande

        destination = {
            'n': ct.joueur_actif.position.index_ - ct.taille_ligne,
            's': ct.joueur_actif.position.index_ + ct.taille_ligne,
            'e': ct.joueur_actif.position.index_ + 1,
            'o': ct.joueur_actif.position.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = ct.emplacements[destination]

        if not deplacement:

            if cible.contenu not in {regles.CARACTERE_MUR, regles.CARACTERE_PORTE}:
                return InstructionCheck.DOIT_RECOMMENCER

            if instruction == 'm':
                cible.contenu = regles.CARACTERE_MUR
            elif instruction == 'p':
                cible.contenu = regles.CARACTERE_PORTE

            return InstructionCheck.ACTION_VALIDE

        if not cible.est_valide(depuis=ct.joueur_actif.position):
            return InstructionCheck.ACTION_VALIDE  # si on cogne contre un mur, le tour se finit

        if cible.fait_gagner():
            return InstructionCheck.A_GAGNE

        ct.joueur_actif.position = cible  # l'état du jeu est modifié ici

        if step < repetitions - 1:
            ct.afficher()  # on affiche les déplacements intermédiaires

    return InstructionCheck.ACTION_VALIDE

def faire_gagner(joueur):
    joueur.gagnant = True

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

    def passer_au_prochain_joueur(ct):
        ct.joueur_actif = ct.prochain_joueur()
        if ct.joueur_actif is None:
            ct.joueur_actif = random.choice(ct.joueurs)
        for conn in ct.connexions_des_clients():
            conn.envoyer("C'est au joueur {} de jouer".format(ct.joueurs.index(ct.joueur_actif) + 1))
            conn.envoyer(ct.afficher(ct.joueur_actif.position.index_))

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
                    if not carte.partie_commencee():
                        if message == regles.CHAINE_COMMENCER:
                            joueur.est_pret = True
                            passer_au_prochain_joueur(carte)
                    else:
                        if joueur is carte.joueur_actif:
                            status_instruction = execute_input(message, carte)
                            if status_instruction == InstructionCheck.ACTION_VALIDE:
                                for __joueur in carte.joueurs:
                                    __joueur.message(
                                        "Le joueur %d s'est déplacé.\n%s" % (
                                            carte.joueurs.index(carte.joueur_actif) + 1,
                                            carte.afficher(__joueur.position.index_)
                                        )
                                    )
                                passer_au_prochain_joueur(carte)
                            elif status_instruction == InstructionCheck.DOIT_RECOMMENCER:
                                joueur.message("Mouvement illégal, veuillez recommencer")
                            elif status_instruction == InstructionCheck.A_GAGNE:
                                carte.joueur_actif.gagnant = True

        for c in carte.connexions_des_clients():
            c.envoyer("Le joueur %d a gagné !" % (carte.joueurs.index(carte.joueur_actif) + 1))

    print("Merci d'avoir joué")