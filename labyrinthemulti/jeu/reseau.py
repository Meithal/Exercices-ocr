import socket
import select
import traceback

import jeu

VERBOSE_ALL = 2
VERBOSE_PORT_ONLY = 1
VERBOSE_NO = 0


class Connexion:

    def __init__(self, addresse_loc, port_loc, description='', sock=None):
        self.addresse = addresse_loc
        self.port = port_loc
        self.description = description if description else (addresse_loc, port_loc)
        self.socket = sock

    def __enter__(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()

    def envoyer(self, message, verbose=VERBOSE_ALL):
        if verbose == VERBOSE_ALL:
            print("envoi: {}, {}".format(self.description, message))
        if verbose == VERBOSE_PORT_ONLY:
            print("envoi sur socket: {}".format(self.description))
        self.socket.send(bytes(message, encoding='utf-8'))


class ConnexionDepuisServeur(Connexion):

    class ArretServeur(Exception):
        pass

    def __init__(self, addresse_loc, port_loc, carte, description=''):
        super().__init__(addresse_loc, port_loc, description)
        self.clients_connectes = {}
        self.lance = True

        self.ecouteurs_nouvelles_connexions = []

        self.carte = carte

    def __enter__(self):
        super().__enter__()

        self.socket.bind((self.addresse, self.port))
        self.socket.listen(5)

        print("Le serveur écoute sur le port {}".format(self.port))

        return self

    def __exit__(self, type_exception, valeur_exception, traceback_exception):
        if type_exception is ConnexionDepuisServeur.ArretServeur:
            print("Fermeture du serveur demandée")
        elif type_exception:
            print("Exception inhabituelle : %s" % valeur_exception)
            traceback.print_tb(traceback_exception)
        else:
            print("Sortie de la connexion serveur")

        for cli in self.clients_connectes:
            cli.close()

        return True

    def nouvelles_connexions(self):

        def coro():
            while True:
                _connexions_demandees = yield
                for connexion in _connexions_demandees:
                    connexion_avec_client, infos_connexion = connexion.accept()
                    connexion_obj = ConnexionVersClient(
                        jeu.reglages.HOTE_CONNEXION,
                        jeu.reglages.PORT_CONNEXION,
                        description="Connexion sortante vers {}".format(connexion_avec_client.getpeername()[1]),
                        sock=connexion_avec_client
                    )
                    self.clients_connectes[connexion_avec_client] = connexion_obj
                    yield connexion_obj

        accueille_nouveaux_coro = coro()
        accueille_nouveaux_coro.send(None)
        while True:
            connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)
            if len(connexions_demandees):
                yield accueille_nouveaux_coro.send(connexions_demandees)
            yield None

    def clients_a_lire(self):
        try:
            clients_a_lire = select.select(self.clients_connectes.keys(), [], [], 0.05)[0]
        except select.error as e:
            print("Erreur lors du select", type(e), e)
            return []
        except Exception as e:
            print("Erreur inhabituelle", type(e), e)
        else:
            for cli in clients_a_lire:
                try:
                    self.carte.joueurs[self.carte.joueurs.index(cli)].buffer_clavier = cli.recv(1024)
                except Exception as e:
                    print("Erreur lors du recv", type(e), e)
                    self.kick_client(cli)

    def kick_client(self, client):
        print("On enleve le client de la carte")
        del self.carte.joueurs[self.carte.joueurs.index(client)]
        client.close()
        del self.clients_connectes[client]

    def broadcast(self, message):
        for connexion in self.clients_connectes:
            connexion.envoyer(message)

class ConnexionVersClient(Connexion):
    pass


class ConnexionDepuisClient(Connexion):

    def __init__(self, addresse_loc, port_loc, description=""):
        super().__init__(addresse_loc, port_loc, description)
        self.contenu_a_afficher = []
        self.attend_entree = True

    def __enter__(self):
        super().__enter__()
        try:
            self.socket.connect((self.addresse, self.port))
            self.local_port = self.socket.getsockname()[1]
            self.remote_port = self.port
            return self
        except Exception as e:
            print(e)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Fermeture de la connexion cliente")

    def ecoute(self):
        while True:
            entrees = select.select([self.socket], [], [], 0.05)[0]
            if entrees:
                print("Entree recue")
                self.contenu_a_afficher.append(entrees[0].recv(1024))
            yield self.contenu_a_afficher

    def pop_contenu_a_afficher(self):
        ct = self.contenu_a_afficher.pop()
        return ct.decode("utf-8")