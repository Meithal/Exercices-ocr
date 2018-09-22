import os
import enum

import jeu.reglages as regles
from jeu.carte import Carte
from jeu.joueur import Joueur
from libs import lib_reseau


class InstructionCheck(enum.Enum):
    OK = 1
    NOT_OK = 2
    END_GAME = 3


def execute_input(i, ct):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param ct: La carte
    :param i: une chaine de caractères demandée par le joueur
    :return: True, le jeu continue, False, le jeu s'arrête
    """

    i = i[:regles.LONGUEUR_MAX_INPUT].strip().lower()

    if not i:
        return InstructionCheck.NOT_OK

    deplacement = False

    if len(i) == 2 and i[0] in {'p', 'm'}:
        instruction, direction = i
    else:
        direction = i[0]
        deplacement = True

    if direction not in 'nseo':
        return InstructionCheck.NOT_OK


    if not deplacement:

        destination = {
            'n': ct.joueur_actif.position.index_ - ct.taille_ligne,
            's': ct.joueur_actif.position.index_ + ct.taille_ligne,
            'e': ct.joueur_actif.position.index_ + 1,
            'o': ct.joueur_actif.position.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = ct.emplacements[destination]

        if cible.contenu not in {regles.CARACTERE_MUR, regles.CARACTERE_PORTE}:
            return InstructionCheck.NOT_OK

        if instruction == 'm':
            cible.contenu = regles.CARACTERE_MUR
        elif instruction == 'p':
            cible.contenu = regles.CARACTERE_PORTE

        return InstructionCheck.OK

    elif deplacement:
        repetitions = 1
        if len(i) == 2 and i[1] in '23456789':
            repetitions = int(i[1])

        print(repetitions)

        for step in range(repetitions):  # on répete le deplacement autant de fois que demande

            destination = {
                'n': ct.joueur_actif.position.index_ - ct.taille_ligne,
                's': ct.joueur_actif.position.index_ + ct.taille_ligne,
                'e': ct.joueur_actif.position.index_ + 1,
                'o': ct.joueur_actif.position.index_ - 1
            }[direction]  # en fonction de la direction demandée, la destination sera differente

            cible = ct.emplacements[destination]

            if not cible.est_valide(depuis=ct.joueur_actif.position):
                return InstructionCheck.OK  # si on cogne contre un mur, le tour se finit

            if cible.fait_gagner():
                print("Vous avez gagné !")
                os.unlink(regles.SAVE_FILE)
                return InstructionCheck.END_GAME

            ct.joueur_actif.position = cible  # l'état du jeu est modifié ici

            if step < repetitions - 1:
                ct.afficher()  # on affiche les déplacements intermédiaires

    return InstructionCheck.OK


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

    ct = Carte(cartes[selected_carte])  # l'instance de Carte où on joue

    print(ct.afficher())

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
        ct,
        "Connexion principale"
    ) as connexion_ecoute:

        if not connexion_ecoute:
            print("Echec de connexion avec le serveur")
            return

        ecouteur_nouvelles_connexions = connexion_ecoute.nouvelles_connexions()

        while True:

            if not ct.partie_commencee():
                nouvelle_connexion = next(ecouteur_nouvelles_connexions)
                if nouvelle_connexion:
                    jr = Joueur(ct)
                    if jr.position:
                        jr.connecter(nouvelle_connexion)
                        print("Nouveau joueur ajouté à la carte sur port {}".format(jr.port))
                        ct.joueurs.append(jr)
                        ct.joueur_actif = jr
                        connexion_ecoute.broadcast(
                            "Bienvenue au nouveau joueur sur le port {}".format(
                                 jr.port
                            ),
                            ct.connexions_des_clients()
                        )
                        jr.connexion.envoyer(ct.afficher(jr.position.index_))
                    else:
                        print("impossible d'ajouter un nouveau joueur")

            if ct.joueurs:
                messages_clients = connexion_ecoute.clients_a_lire(ct.sockets_des_clients())
                if messages_clients:
                    for sock, message in messages_clients.items():
                        ct.joueurs[ct.joueurs.index(sock)].buffer.write(message)

                    for _jr in ct.joueurs_bavards():
                        buffer = _jr.buffer.read()
                        print(_jr.port, ": ", buffer)
                        if not ct.partie_commencee():
                            if buffer == regles.CHAINE_COMMENCER:
                                _jr.est_pret = True
                                ct.debut_du_jeu = time.time()
                        elif _jr is ct.joueur_actif:
                            status_instruction = execute_input(buffer, ct)
                            if status_instruction == InstructionCheck.OK:
                                for __jr in ct.joueurs:
                                    __jr.connexion.envoyer(
                                        "Le joueur {} s'est déplacé.\n{}".format(
                                            ct.joueurs.index(ct.joueur_actif) + 1,
                                            ct.afficher(__jr.position.index_)
                                        )
                                    )
                                passer_au_prochain_joueur(ct)
                            elif status_instruction == InstructionCheck.NOT_OK:
                                _jr.connexion.envoyer("Mouvement illégal, veuillez recommencer")
                            elif status_instruction == InstructionCheck.END_GAME:
                                connexion_ecoute.broadcast(
                                    "Le joueur {} a gagné !".format(
                                        ct.joueurs.index(ct.joueur_actif) + 1
                                    ),
                                    ct.connexions_des_clients()
                                )
                                print("Merci d'avoir joué")
                                return

            if ct.partie_commencee():

                if time.time() > ct.debut_du_tour + regles.SECONDES_PAR_TOUR:
                    passer_au_prochain_joueur(ct)
