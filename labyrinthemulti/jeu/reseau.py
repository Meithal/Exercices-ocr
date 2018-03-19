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

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ConnexionServeur.ArretServeur:
            print("Fermeture du serveur demandée")
        else:
            print("Exception inhabituelle : %s" % exc_val)

        for cli in self.clients_connectes:
            cli.close()

        return True

    def traite_requetes(self):
        connexions_demandees, wlist, xlist = select.select([self.socket], [], [], 0.05)

        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()

            print("Client connecté", infos_connexion)

            self.clients_connectes[connexion_avec_client] = {"port": infos_connexion[1]}

        return True

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
