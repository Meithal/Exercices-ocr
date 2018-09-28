# Cette librairie encapsule le module socket pour pouvoir envoyer des donnees sans devoir les convertir
# vers et depuis des bytes, et fournit un context manager pour facilement ouvrir et fermer une connexion.
# Ainsi qu'une fonction qui facilite l'usage de select.select
# (c) https://github.com/Meithal 2018

import socket
import select
import traceback
from typing import List


class Connexion:

    def __init__(self, addresse_loc, port_loc, description='', sock=None):
        self.addresse = addresse_loc
        self.port = port_loc
        self.description = description if description else (addresse_loc, port_loc)
        self.socket = sock
        if not sock:  # si la connexion vient d'un select.select, le socket existe deja, sinon le créer
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        """Les sockets renvoyés par select.select n'utilisent pas de context manager, donc seul le ramasse-miette
           fonctionne ici."""
        self.socket.close()
        print("%s supprimée par le ramasse-miettes" % self.description)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print("Exception inhabituelle : %s" % exc_val)
            traceback.print_tb(exc_tb)

        # plutot que d'attendre que la variable associée au bloc 'with' soit récupérée par le garbage collector
        # ou explicitement 'del', on ferme nous même la connexion dès la sortie du bloc 'with'
        self.socket.close()

    def envoyer(self, message):
        try:
            self.socket.send(bytes(message, encoding='utf-8'))
        except Exception as e:
            print(e)
            self.socket.close()

    def est_connecte(self):
        return self.socket.fileno() != -1


def clients_a_lire(clients):
    clients = (_.socket for _ in clients)
    try:
        clients_a_lire = select.select((_ for _ in clients), [], [], 0.05)[0]
    except Exception as e:
        print("Erreur inhabituelle", type(e), e)
        raise e
    else:
        rv = {}
        for cli in clients_a_lire:
            try:
                rv[cli] = cli.recv(1024).decode("utf-8")
            except Exception as e:
                print("Erreur lors du recv", type(e), e)

        return rv


class ConnexionEnTantQueServeur(Connexion):

    def __init__(self, addresse_loc, port_loc, description=''):
        super().__init__(addresse_loc, port_loc, description)

    def __enter__(self):
        self.socket.bind((self.addresse, self.port))
        self.socket.listen(5)

        print("Le serveur écoute sur le port {}".format(self.port))

        return self

    def __exit__(self, type_exception, valeur_exception, traceback_exception):
        print("Fermeture de la connexion serveur")

        super().__exit__(type_exception, valeur_exception, traceback_exception)

    def nouvelles_connexions(self):

        def generateur_connexions(connexions):
            for _connexion in connexions:
                socket_vers_client, infos_connexion = _connexion.accept()
                connexion_obj = Connexion(
                    self.addresse,
                    self.port,
                    description="Connexion sortante vers {}".format(socket_vers_client.getpeername()[1]),
                    sock=socket_vers_client
                )
                yield connexion_obj

        while True:
            connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)
            for connexion in generateur_connexions(connexions_demandees):
                yield connexion
            else:
                yield None


class ConnexionEnTantQueClient(Connexion):

    def __init__(self, addresse_loc, port_loc, description=""):
        super().__init__(addresse_loc, port_loc, description)
        self.contenu_a_afficher = Buffer()
        self.attend_entree = True

    def __enter__(self):

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

        super().__exit__(exc_type, exc_val, exc_tb)

    def ecoute(self):
        while True:
            entrees = select.select([self.socket], [], [], 0.05)[0]
            if entrees:
                print("Entree recue")
                try:
                    ct = entrees[0].recv(1024)
                    if not ct:
                        raise Exception("Le serveur distant ne répond plus.")
                    self.contenu_a_afficher.write(ct)
                except Exception as e:
                    raise e
            yield self.contenu_a_afficher


class Buffer:

    def __len__(self):
        return len(self.buffer)

    def __init__(self):
        self.buffer = bytearray()

    # groupe le message au buffer
    def write(self, message):
        self.buffer += message

    # lis le buffer et le vide
    def read(self):
        rt = self.buffer.decode("utf-8")
        self.buffer.clear()
        return rt