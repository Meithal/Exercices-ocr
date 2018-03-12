import os
import asyncio
import socket
import select

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
            carte.affiche_serveur()  # on affiche les déplacements intermédiaires

    return True


def serveur():
    """La boucle principale du jeu"""
    def connexion_etablie():
        print("un client est connecté")

    def attente_de_connexion():
        pass

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

    carte.affiche_serveur()

    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind(('', jeu.reglages.PORT_CONNEXION))
    connexion_principale.listen(5)
    print("Le serveur écoute sur le port {}".format(jeu.reglages.PORT_CONNEXION))


    serveur_lance = True
    clients_connectes = []

    while serveur_lance:

        connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)

        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            print("Client connecté", infos_connexion)
            clients_connectes.append(connexion_avec_client)

        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
        except select.error as e:
            # print("Probleme avec client", e)
            pass
        else:
            for client in clients_a_lire:
                msg_recu = client.recv(1024)
                msg_recu = msg_recu.decode()
                print("Recu {}".format(msg_recu))
                client.send(b"Recu 5/5")
                if msg_recu == "fin":
                    serveur_lance = False

    print("Fermeture de connexion")
    for client in clients_connectes:
        client.close()

    connexion_principale.close()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.ensure_future(attente_de_connexion)
    future.add_done_callback(connexion_etablie)
    try:
        loop.run_forever()
    finally:
        loop.stop()

    while execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n")):
        carte.affiche_serveur()

    print("Merci d'avoir joué")

def client():
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_avec_serveur.connect((jeu.reglages.HOTE_CONNEXION, jeu.reglages.PORT_CONNEXION))
    print("Connexion établie avec le serveur sur le port {}".format(jeu.reglages.PORT_CONNEXION))

    msg_a_envoyer = b""
    while msg_a_envoyer != b"fin":
        msg_a_envoyer = input("> ")

        msg_a_envoyer = msg_a_envoyer.encode()
        connexion_avec_serveur.send(msg_a_envoyer)
        msg_recu = connexion_avec_serveur.recv(1024)
        print(msg_recu.decode())

    print("Fermeture de la connexion.")
    connexion_avec_serveur.close()