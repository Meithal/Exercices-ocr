import socket
import select
import traceback
import collections

Info_connexion = collections.namedtuple("Info_connexion", "addresse, port")


class Connexion:

    def __init__(self, addresse, port, description=''):
        self.addresse = addresse
        self.port = port
        self.description = description if description else (addresse, port)

    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()

    def envoyer(self, message):
        self.socket.send(bytes(message, encoding='utf-8'))


class ConnexionServeur(Connexion):

    class ArretServeur(Exception):
        pass

    def __init__(self, addresse, port, description=''):
        super().__init__(addresse, port, description)
        self.clients_connectes = {}
        self.lance = True

        self.ecouteurs_nouvelles_connexions = []

    def __enter__(self):
        super().__enter__()

        self.socket.bind((self.addresse, self.port))
        self.socket.listen(5)

        print("Le serveur écoute sur le port {}".format(self.port), id(self.socket))

        return self

    def __exit__(self, type_exception, valeur_exception, traceback_exception):
        if type_exception is ConnexionServeur.ArretServeur:
            print("Fermeture du serveur demandée")
        else:
            print("Exception inhabituelle : %s" % valeur_exception)
            traceback.print_tb(traceback_exception)

        for cli in self.clients_connectes:
            cli.close()

        return True


    def requetes(self):

        def nouvelles_connexions():
            while True:
                connexions_demandees = yield
                for connexion in connexions_demandees:
                    connexion_avec_client, infos_connexion = connexion.accept()
                    self.clients_connectes[connexion_avec_client] = Info_connexion(*infos_connexion)
                    yield connexion_avec_client

        accueille_nouveaux = nouvelles_connexions()
        accueille_nouveaux.send(None)
        while True:
            connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)
            if len(connexions_demandees):
                nouveau = accueille_nouveaux.send(connexions_demandees)
                yield nouveau
            yield None


    def clients_a_lire(self):
        try:
            clients_a_lire = select.select(self.clients_connectes.keys(), [], [], 0.05)
        except select.error:
            return [], [], []
        else:
            return clients_a_lire

    def kick_client(self, client):
        self.clients_connectes[client].close()


class ConnexionClient(Connexion):

    def __enter__(self):
        super().__enter__()
        try:
            self.socket.connect((self.addresse, self.port))
            return self
        except Exception as e:
            print(e)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        print ("Fermeture de la connexion cliente")
        pass