# Cette librairie encapsule le module socket pour pouvoir envoyer des donnees sans devoir les convertir
# vers et depuis des bytes, et fournit un context manager pour facilement ouvrir et fermer une connexion.
# (c) https://github.com/Meithal 2018

import socket
import select
import traceback


class Connexion:

    def __init__(self, addresse_loc, port_loc, description='', sock=None):
        self.addresse = addresse_loc
        self.port = port_loc
        self.description = description if description else (addresse_loc, port_loc)
        self.socket = sock
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        """Lorsque cette connexion vient d'un select, on ne peut pas lui associer un context manager.
           Donc on capture notre fermeture lorsque le garbage collector nous supprime. Mais une connexion
           crée via un context manager finira aussi dans le garbage collector donc on appelle self.__bool__
           pour vérifier que le socket n'est pas déjà fermé"""
        if self:
            self.socket.close()
        print("%s supprimée par le ramasse-miettes" % self.description)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Concerne les socket qu'on créé nous même, avec 'with'."""
        if exc_type:
            print("Exception inhabituelle : %s" % exc_val)
            traceback.print_tb(exc_tb)

        # plutot que d'attendre que la variable associée au bloc 'with' soit récupérée par le garbage collector
        # ou explicitement 'del', on ferme la connexion dès la sortie du bloc 'with'
        self.socket.close()

    def __bool__(self):
        """On est "Truthy" lorsque notre connexion est active"""
        return self.socket.fileno() != -1

    def envoyer(self, message):
        try:
            self.socket.send(bytes(message, encoding='utf-8'))
        except Exception as e:
            print(e)
            self.socket.close() # on devient "Falsy"


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

        def coro():
            while True:
                _connexions_demandees = yield
                for connexion in _connexions_demandees:
                    connexion_avec_client, infos_connexion = connexion.accept()
                    connexion_obj = ConnexionDepuisClient(
                        self.addresse,
                        self.port,
                        description="Connexion sortante vers {}".format(connexion_avec_client.getpeername()[1]),
                        sock=connexion_avec_client
                    )
                    yield connexion_obj

        accueille_nouveaux_coro = coro()
        accueille_nouveaux_coro.send(None)
        while True:
            connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)
            if len(connexions_demandees):
                yield accueille_nouveaux_coro.send(connexions_demandees)
            else:
                yield None

    def clients_a_lire(self, clients):
        try:
            clients_a_lire = select.select((_ for _ in clients), [], [], 0.05)[0]
        except Exception as e:
            print("Erreur inhabituelle", type(e), e)
            raise e
        else:
            rv = {}
            for cli in clients_a_lire:
                try:
                    rv[cli] = cli.recv(1024)
                except Exception as e:
                    print("Erreur lors du recv", type(e), e)

            return rv

    @staticmethod
    def broadcast(message, cibles):
        for connexion in cibles:
            connexion.envoyer(message + "\n")


class ConnexionDepuisClient(Connexion):

    buffer_clavier = ""


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