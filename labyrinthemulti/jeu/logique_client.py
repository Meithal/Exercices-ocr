import os
import signal

import libs.lib_reseau as lib_reseau

import jeu.reglages as regles


def client():
    """
    Un terminal qui affiche et envoie des donnees, sans utiliser d'autres objets du jeu
    :return:
    """

    import threading

    with lib_reseau.ConnexionEnTantQueClient(
            regles.HOTE_CONNEXION,
            regles.PORT_CONNEXION,
            "Connection client sortante.") as connexion:

        if not connexion:
            print("Echec de connexion avec le serveur")
            return

        print("Connexion établie avec le serveur sur le port {}".format(regles.PORT_CONNEXION))
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
                    os.kill(os.getpid(), signal.SIGTERM)  # impossible de fermer le thread principal sans signal

                if connexion.contenu_a_afficher:
                    print(connexion.contenu_a_afficher.read(),
                          "\nLe serveur a envoyé le contenu ci dessus. Si vous etiez en train de taper",
                          "quelque chose veuillez recommencer.",
                          "\nvvv")

        cli_thread = threading.Thread(target=display, daemon=True)
        cli_thread.start()  # ce thread affiche le contenu que le serveur envoi

        while True:
            buffer = input("> ")
            if not cli_thread.is_alive():
                print("Liaison avec le serveur perdue.")
                return
            connexion.envoyer(buffer)
