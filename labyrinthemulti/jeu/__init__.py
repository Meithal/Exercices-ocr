import os

from jeu.carte import Carte
from jeu.emplacement import Emplacement
from jeu.joueur import Joueur
import jeu.reglages
from libs import lib_reseau

SELECT_SOCKET_INPUT = 0
SELECT_SOCKET_OUTPUT = 1
SELECT_SOCKET_EXCEPT = 2


def execute_input(i, ct):
    """
    Modifie l'état du jeu en fonction de l'input demandé
    :param ct: La carte
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
            'N': ct.joueur_actif.position.index_ - ct.taille_ligne,
            'S': ct.joueur_actif.position.index_ + ct.taille_ligne,
            'E': ct.joueur_actif.position.index_ + 1,
            'O': ct.joueur_actif.position.index_ - 1
        }[direction]  # en fonction de la direction demandée, la destination sera differente

        cible = ct.emplacements[destination]
            # jeu.emplacement.Emplacement(destination, ct.taille_ligne, ct)

        if not cible.est_valide(depuis=ct.joueur_actif.position):
            return True  # si l'emplacement cible ne permet pas de s'y trouver, on quitte la procédure ici

        if cible.fait_gagner():
            print("Vous avez gagné !")
            os.unlink(jeu.reglages.SAVE_FILE)
            return False

        ct.joueur_actif.position = cible  # l'état du jeu est modifié ici

        if step < repetitions - 1:
            ct.afficher()  # on affiche les déplacements intermédiaires

    return True


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

    ct = jeu.Carte(cartes[selected_carte])  # l'instance de Carte où on joue

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
        jeu.reglages.PORT_CONNEXION,
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
                    jr = jeu.Joueur(ct)
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

                    joueurs_bavards = [_ for _ in ct.joueurs if _.buffer]
                    for _jr in joueurs_bavards:
                        buffer = _jr.buffer.read()
                        print(_jr.port, ": ", buffer)
                        if not ct.partie_commencee():
                            if buffer == reglages.CHAINE_COMMENCER:
                                _jr.est_pret = True
                                ct.debut_du_jeu = time.time()
                        elif _jr is ct.joueur_actif:
                            if execute_input(buffer, ct):
                                for __jr in ct.joueurs:
                                    __jr.connexion.envoyer(
                                        "Le joueur {} s'est déplacé.\n{}".format(
                                            ct.joueurs.index(ct.joueur_actif) + 1,
                                            ct.afficher(__jr.position.index_)
                                        )
                                    )
                                passer_au_prochain_joueur(ct)
                            else:
                                connexion_ecoute.broadcast(
                                    "Le joueur {} a gagné !".format(
                                        ct.joueurs.index(ct.joueur_actif) + 1
                                    ),
                                    ct.connexions_des_clients()
                                )
                                return

            if ct.partie_commencee():

                if time.time() > ct.debut_du_tour + jeu.reglages.SECONDES_PAR_TOUR:
                    passer_au_prochain_joueur(ct)

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
                try:
                    next(connexion.ecoute())
                except Exception as e:
                    print(e)
                    return
                if connexion.contenu_a_afficher:
                    print(connexion.pop_contenu_a_afficher(),
                          "\nLe serveur a envoyé le contenu ci dessus. Si vous etiez en train de taper",
                          "quelque chose veuillez recommencer.",
                          "\nvvv")

        cli_thread = threading.Thread(target=display)
        cli_thread.start()  # ce thread affiche le contenu que le serveur envoi

        while True:
            buffer = input("> ")
            if not cli_thread.is_alive():
                print("Liaison avec le serveur perdue.")
                return
            print("Ce que vous avez ecrit: " + buffer)
            connexion.envoyer(buffer)
