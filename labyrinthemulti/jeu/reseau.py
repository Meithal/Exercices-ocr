import socket
import select


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


class ConnexionServeur(Connexion):

    class ArretServeur(Exception):
        pass

    def __init__(self, addresse, port, description=''):
        super().__init__(addresse, port, description)
        self.clients_connectes = {}
        self.lance = True

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

        for cli in self.clients_connectes:
            cli.close()

        return True

    def requetes(self):
        accueille_nouveaux = self.nouveaux_clients()
        accueille_nouveaux.send(None)
        while True:
            connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)
            if len(connexions_demandees):
                accueille_nouveaux.send(connexions_demandees)
                yield connexions_demandees

    def nouveaux_clients(self):
        while True:
            connexions_demandees = yield

            for connexion in connexions_demandees:
                connexion_avec_client, infos_connexion = connexion.accept()

                print("Client connecté", infos_connexion)

                self.clients_connectes[connexion_avec_client] = {"port": infos_connexion[1]}

    def clients_a_lire(self):
        try:
            clients_a_lire = select.select(self.clients_connectes.keys(), [], [], 0.05)
        except select.error:
            return [], [], []
        else:
            return clients_a_lire


class ConnexionClient(Connexion):

    def __enter__(self):
        super().__enter__()
        self.socket.connect((self.addresse, self.port))

        return self
