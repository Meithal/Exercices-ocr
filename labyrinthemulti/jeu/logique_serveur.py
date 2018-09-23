import os
import enum

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


def serveur():
    """La boucle principale du jeu"""

    import time

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

    carte = Carte(cartes[selected_carte])  # l'instance de Carte où on joue

    print(carte.afficher())

    def passer_au_prochain_joueur(ct):
        ct.joueur_actif = ct.prochain_joueur()
        ct.debut_du_tour = time.time()
        connexion_ecoute.broadcast(
            "C'est au joueur {}  de jouer".format(ct.joueurs.index(ct.joueur_actif) + 1),
            ct.connexions_des_clients()
        )
        for jr in ct.joueurs:
            jr.connexion.envoyer(ct.afficher(ct.joueur_actif.position.index_))

    with lib_reseau.ConnexionEnTantQueServeur(
        '',
        regles.PORT_CONNEXION,
        "Connexion principale"
    ) as connexion_ecoute:

        if not connexion_ecoute:
            print("Echec de connexion avec le serveur")
            return

        ecouteur_nouvelles_connexions = connexion_ecoute.nouvelles_connexions()

        while True:

            if not carte.partie_commencee():
                nouvelle_connexion = next(ecouteur_nouvelles_connexions)
                if nouvelle_connexion:
                    _joueur = Joueur(carte)
                    if _joueur.position:
                        _joueur.connecter(nouvelle_connexion)
                        print("Nouveau joueur ajouté à la carte sur port {}".format(_joueur.port))
                        carte.joueurs.append(_joueur)
                        carte.joueur_actif = _joueur
                        connexion_ecoute.broadcast(
                            "Bienvenue au nouveau joueur sur le port {}".format(
                                 _joueur.port
                            ),
                            carte.connexions_des_clients()
                        )
                        _joueur.connexion.envoyer(carte.afficher(_joueur.position.index_))
                    else:
                        print("impossible d'ajouter un nouveau joueur")

            if carte.joueurs:
                messages_clients = connexion_ecoute.clients_a_lire(carte.sockets_des_clients())
                if messages_clients:
                    for sock, message in messages_clients.items():
                        carte.joueurs[carte.joueurs.index(sock)].buffer.write(message)

                    for _joueur in carte.joueurs_bavards():
                        buffer = _joueur.buffer.read()
                        print(_joueur.port, ": ", buffer)
                        if not carte.partie_commencee():
                            if buffer == regles.CHAINE_COMMENCER:
                                _joueur.est_pret = True
                                carte.debut_du_jeu = time.time()
                                passer_au_prochain_joueur(carte)
                        elif _joueur is carte.joueur_actif:
                            status_instruction = execute_input(buffer, carte)
                            if status_instruction == InstructionCheck.ACTION_VALIDE:
                                for __joueur in carte.joueurs:
                                    __joueur.connexion.envoyer(
                                        "Le joueur {} s'est déplacé.\n{}".format(
                                            carte.joueurs.index(carte.joueur_actif) + 1,
                                            carte.afficher(__joueur.position.index_)
                                        )
                                    )
                                passer_au_prochain_joueur(carte)
                            elif status_instruction == InstructionCheck.DOIT_RECOMMENCER:
                                _joueur.connexion.envoyer("Mouvement illégal, veuillez recommencer")
                            elif status_instruction == InstructionCheck.A_GAGNE:
                                connexion_ecoute.broadcast(
                                    "Le joueur {} a gagné !".format(
                                        carte.joueurs.index(carte.joueur_actif) + 1
                                    ),
                                    carte.connexions_des_clients()
                                )
                                print("Merci d'avoir joué")
                                return