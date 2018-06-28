import os

import jeu.carte_  # on utilise deja le nom 'carte' pour stocker l'instance de Carte
import jeu.emplacement
import jeu.joueur
import jeu.reglages
import jeu.reseau

cartes = []  # une liste de nom de cartes
carte = jeu.carte_.Carte()  # l'instance de Carte où on joue


SELECT_SOCKET_INPUT = 0
SELECT_SOCKET_OUTPUT = 1
SELECT_SOCKET_EXCEPT = 2


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

    carte.afficher()

    with jeu.reseau.ConnexionServeur('', jeu.reglages.PORT_CONNEXION, "Connexion principale") as connexion_principale:

        while True:

            if not carte.partie_commencee:
                next(connexion_principale.requetes())

            for client in connexion_principale.clients_a_lire()[SELECT_SOCKET_INPUT]:
                msg_recu = client.recv(1024).decode()
                print("Recu {!r} depuis {}".format(msg_recu, connexion_principale.clients_connectes[client]))
                if msg_recu == "bonjour":
                    if carte.ajoute_joueur(connexion_principale.clients_connectes[client]["port"]) >= 0:
                        client.send(b"Bienvenue dans le jeu")
                    else:
                        client.send(b"Nous n'avons pas reussi a vous placer dans le jeu, vous pouvez reessayer.")
                        connexion_principale.clients_connectes[client].close()
                if msg_recu == "fin":
                    raise jeu.reseau.ConnexionServeur.ArretServeur
            if carte.partie_commencee:
                carte.afficher()


    # while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n")):
    #     carte.affiche_serveur()

    print("Merci d'avoir joué")


def client():

    with jeu.reseau.ConnexionClient(
            jeu.reglages.HOTE_CONNEXION,
            jeu.reglages.PORT_CONNEXION,
            "Connection client sortante.") as connexion_avec_serveur:

        print("Connexion établie avec le serveur sur le port {}".format(jeu.reglages.PORT_CONNEXION))

        connexion_avec_serveur.socket.send(b"bonjour")

        msg_a_envoyer = b""
        while msg_a_envoyer != b"fin":
            msg_a_envoyer = input("> ")

            msg_a_envoyer = msg_a_envoyer.encode()
            try:
                connexion_avec_serveur.socket.send(msg_a_envoyer)
                msg_recu = connexion_avec_serveur.socket.recv(1024)
            except Exception as e:
                print(e)
                return
            print(msg_recu.decode())

