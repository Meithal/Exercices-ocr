import os
import subprocess

import jeu.carte_  # on utilise deja le nom 'carte' pour stocker l'instance de Carte
import jeu.emplacement
import jeu.joueur
import jeu.reglages
import jeu.reseau


SELECT_SOCKET_INPUT = 0
SELECT_SOCKET_OUTPUT = 1
SELECT_SOCKET_EXCEPT = 2


def execute_input(i, carte):
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
            'N': carte.position_par_defaut.index_ - carte.taille_ligne,
            'S': carte.position_par_defaut.index_ + carte.taille_ligne,
            'E': carte.position_par_defaut.index_ + 1,
            'O': carte.position_par_defaut.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = jeu.emplacement.Emplacement(destination, carte.taille_ligne)

        if not cible.est_valide(depuis=carte.position_par_defaut):
            return True  # si l'emplacement cible ne permet pas de s'y trouver, on quitte la procédure ici

        if cible.fait_gagner():
            print("Vous avez gagné !")
            os.unlink(jeu.reglages.SAVE_FILE)
            return False

        carte.position_par_defaut = cible  # l'état du jeu est modifié ici

        if step < repetitions - 1:
            carte.afficher()  # on affiche les déplacements intermédiaires

    return True


def serveur():
    """La boucle principale du jeu"""

    # def connexionEntrante():

    cartes = []  # une liste de nom de cartes
    carte = jeu.carte_.Carte()  # l'instance de Carte où on joue

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

    print(carte.afficher())

    with jeu.reseau.ConnexionDepuisServeur(
            '',
            jeu.reglages.PORT_CONNEXION,
            carte,
            "Connexion principale") as connexion_ecoute:

        if not connexion_ecoute:
            print("Echec de connexion avec le serveur")
            return

        while True:

            if not carte.partie_commencee:

                nouveau = next(connexion_ecoute.nouvelles_connexions())

                if nouveau:
                    joueur = jeu.joueur.Joueur(nouveau)

                    if joueur.position:
                        print("Nouveau joueur ajouté à la carte sur port {}".format(joueur.port))
                        carte.joueurs.append(joueur)
                        for joueur_ in carte.joueurs:
                            joueur_.connexion.envoyer(
                                "Bienvenue au nouveau joueur sur le port {}\n{}".format(joueur.port, carte.afficher(joueur_.position.index_))
                            )

                    else:
                        print("impossible d'ajouter un nouveau joueur")
                        connexion_ecoute.kick_client(joueur.sock)

                if len(carte.joueurs):

                    connexion_ecoute.clients_a_lire()

                    for joueur_ in carte.joueurs:
                        if joueur_.buffer_clavier:
                            contenu = joueur_.pop_clavier_buffer()
                            print(contenu)
                            if contenu == reglages.CHAINE_COMMENCER:
                                carte.partie_commencee = True

            if carte.partie_commencee:
                break

        print(carte.afficher())

        while not carte.partie_gagnee:
            print("C'est au joueur {}  de jouer".format(carte.joueur_actif))
            connexion_ecoute.broadcast("C'est au joueur {}  de jouer".format(carte.joueur_actif))

    # while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n"), carte):
    #     carte.affiche_serveur()

    print("Merci d'avoir joué")


def client():

    import jeu.lib_client

    with jeu.reseau.ConnexionDepuisClient(
            jeu.reglages.HOTE_CONNEXION,
            jeu.reglages.PORT_CONNEXION,
            "Connection client sortante.") as connexion:

        if not connexion:
            print("Echec de connexion avec le serveur")
            return

        print("Connexion établie avec le serveur sur le port {}".format(jeu.reglages.PORT_CONNEXION))
        print("Notre port: {}".format(connexion.local_port))

        connexion.envoyer("bonjour")

        while True:
            next(connexion.ecoute())

            if connexion.contenu_a_afficher:
                print(connexion.pop_contenu_a_afficher())

            if connexion.attend_entree:

                connexion.attend_entree = False

                print("Vous avez 15 secondes pour entrer une instruction.\nvvv")
                try:
                    sortie = subprocess.check_output(
                        'py -3 ./ask_for_input.py', timeout=15.0, stderr=subprocess.STDOUT
                    ).decode("utf-8")
                except subprocess.TimeoutExpired:
                    print("\nTrop tard !")
                    sortie = ""
                print("Ce que vous avez ecrit: " + sortie)

            #
            #     thread_afficheur.show("env")
            #     thread_clavier.join(5.0)
            #     connexion.envoyer(thread_clavier.message_queue.pop())
