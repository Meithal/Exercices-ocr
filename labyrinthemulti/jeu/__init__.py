import os

from jeu.carte import Carte
from jeu.emplacement import Emplacement
from jeu.joueur import Joueur
import jeu.reglages
from libs import lib_reseau

SELECT_SOCKET_INPUT = 0
SELECT_SOCKET_OUTPUT = 1
SELECT_SOCKET_EXCEPT = 2


def execute_input(i, carte_):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param carte_: La carte
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
            'N': carte_.position_par_defaut.index_ - carte_.taille_ligne,
            'S': carte_.position_par_defaut.index_ + carte_.taille_ligne,
            'E': carte_.position_par_defaut.index_ + 1,
            'O': carte_.position_par_defaut.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = jeu.emplacement.Emplacement(destination, carte_.taille_ligne)

        if not cible.est_valide(depuis=carte_.position_par_defaut):
            return True  # si l'emplacement cible ne permet pas de s'y trouver, on quitte la procédure ici

        if cible.fait_gagner():
            print("Vous avez gagné !")
            os.unlink(jeu.reglages.SAVE_FILE)
            return False

        carte_.position_par_defaut = cible  # l'état du jeu est modifié ici

        if step < repetitions - 1:
            carte_.afficher()  # on affiche les déplacements intermédiaires

    return True


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

    carte_ = jeu.Carte(cartes[selected_carte])  # l'instance de Carte où on joue

    print(carte_.afficher())

    with lib_reseau.ConnexionEnTantQueServeur(
        '',
        jeu.reglages.PORT_CONNEXION,
        carte_,
        "Connexion principale"
    ) as connexion_ecoute:

        if not connexion_ecoute:
            print("Echec de connexion avec le serveur")
            return

        ecouteur_nouvelles_connexions = connexion_ecoute.nouvelles_connexions()

        while True:

            if not carte_.partie_commencee():

                nouvelle_connexion = next(ecouteur_nouvelles_connexions)

                if nouvelle_connexion:
                    joueur_ = jeu.Joueur(carte_)

                    if joueur_.position:
                        print("Nouveau joueur ajouté à la carte sur port {}".format(joueur_.port))

                        joueur_.connecter(nouvelle_connexion)
                        carte_.joueurs.append(joueur_)

                        connexion_ecoute.broadcast(
                            "Bienvenue au nouveau joueur sur le port {}\n{}".format(
                                 joueur_.port, carte_.afficher(joueur_.position.index_)
                            ),
                            carte_.connexions_des_clients()
                        )

                    else:
                        print("impossible d'ajouter un nouveau joueur")

                if carte_.joueurs:

                    connexion_ecoute.clients_a_lire(carte_.sockets_des_clients())

                    for joueur_ in carte_.joueurs:
                        if joueur_.buffer_clavier:
                            contenu = joueur_.pop_clavier_buffer()
                            if contenu == reglages.CHAINE_COMMENCER:
                                joueur_.est_pret = True

            if carte_.partie_commencee():
                break

        print(carte_.afficher())

        while not carte_.partie_gagnee:
            print("C'est au joueur {}  de jouer".format(carte_.joueur_actif))

            connexion_ecoute.broadcast(
                "C'est au joueur {}  de jouer".format(carte_.joueur_actif),
                carte_.connexions_des_clients()
            )


    # while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n"), carte):
    #     carte.affiche_serveur()

    print("Merci d'avoir joué")


def client():
    """
    Pour l'instant il s'agit d'un simple telex qui affiche et envoie des donnees, et n'initialise pas d'objet carte
    :return:
    """

    import threading

    with lib_reseau.ConnexionEnTantQueClient(
            jeu.reglages.HOTE_CONNEXION,
            jeu.reglages.PORT_CONNEXION,
            "Connection client sortante.") as connexion:

        if not connexion:
            print("Echec de connexion avec le serveur")
            return

        print("Connexion établie avec le serveur sur le port {}".format(jeu.reglages.PORT_CONNEXION))
        print("Notre port: {}".format(connexion.local_port))

        connexion.envoyer("bonjour")

        def display():
            import time
            while True:
                time.sleep(1)
                next(connexion.ecoute())
                if connexion.contenu_a_afficher:
                    print(connexion.pop_contenu_a_afficher(),
                          "\nLe serveur a envoyé le contenu ci dessus. Si vous etiez en train de taper",
                          "quelque chose veuillez recommencer.",
                          "\nvvv")

        threading.Thread(target=display).start()  # ce thread affiche le contenu que le serveur envoi

        while True:

            buffer = input("> ")
            print("Ce que vous avez ecrit: " + buffer)
            connexion.envoyer(buffer)
