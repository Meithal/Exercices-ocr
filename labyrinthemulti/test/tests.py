import unittest
import sys
import os
import libs.lib_reseau
import socket
import threading


class TestEnvironment(unittest.TestCase):

    def test_python_version(self):
        self.assertGreaterEqual(
            sys.version_info.major,
            3,
            "Python must be version 3, you currently run Python %d" % sys.version_info.major
        )

        self.assertGreaterEqual(
            sys.version_info.minor,
            5,
            "Python 3.5 minimum is required, you currently have Python 3.%d" % sys.version_info.minor
        )

    def test_platform(self):
        self.assertIn(
            'win',
            sys.platform,
            "This game has been made and tested on windows only, feel free to remove this test "
            "if the game actually works on linux/mac"
        )


def start_client(wait_lock: threading.Event):
    import libs.lib_reseau
    with libs.lib_reseau.ConnexionEnTantQueClient(
            'localhost',
            '12345',
            "Connection client sortante.") as connexion:

        wait_lock.wait()


def make_server():
    return libs.lib_reseau.ConnexionEnTantQueServeur(
        addresse_loc='', port_loc=12345, description='test'
    ).start()


class TestConnection(unittest.TestCase):

    _server = None

    @classmethod
    def setUpClass(cls):
        if os.getcwd().endswith("test"):  # When runing automatic testing, getcwd will not be at root
            os.chdir("..")
        cls._server = make_server()

    def setUp(self):
        self.server = type(self)._server

    def test_connexion_server(self):

        self.assertIsInstance(self.server, libs.lib_reseau.ConnexionEnTantQueServeur, "Mauvaise connexion")

    def test_socket(self):
        self.assertIsInstance(self.server.socket, socket.socket, "Mauvais socket")

    def test_socket_link(self):
        self.assertNotEqual(self.server.socket.fileno(), -1, "Le socket ne s'est pas créé")

        # block1 = threading.Event()
        # block2 = threading.Event()
        # threading.Thread(target=start_client, args=(block1,)).start()
        # threading.Thread(target=start_client, args=(block2,)).start()
        # block1.set()
        # block2.set()

    def tearDown(self):
        self.server = None

    @classmethod
    def tearDownClass(cls):
        cls._server.stop()


class TestCarte(TestConnection):

    laby = b"""OO.O 
  X U
OOOOO"""

    def setUp(self):
        super().setUp()
        with open(os.path.join("cartes", "test"), "wb") as carte:
            carte.write(type(self).laby)

    def test_create(self):
        import jeu.carte
        carte = jeu.carte.Carte("test", self.server)
        self.assertIsInstance(carte, jeu.carte.Carte)

    def tearDown(self):
        super().tearDown()
        os.unlink(os.path.join("cartes", "test"))


class TestLabyrinthe(TestCarte):
    def setUp(self):
        import jeu.carte
        super().setUp()
        self.carte = jeu.carte.Carte("test", self.server)

    def test_length(self):
        self.assertEqual(len(self.carte.emplacements), 15)

    def test_largeur(self):
        self.assertEqual(self.carte.taille_ligne, 5)

    def test_contenu(self):
        self.assertEqual(self.carte.emplacements[0].contenu, 'O', 'Un mur se trouve ici')

    def test_vide(self):
        self.assertEqual(self.carte.emplacements[6].contenu, ' ', "L'espace est vide")

    def test_joueur_enleve(self):
        self.assertEqual(self.carte.emplacements[7].contenu, ' ', "Le joueur doit etre enlevé")

    def test_joueur_victoire(self):
        self.assertEqual(self.carte.emplacements[9].contenu, 'U', "La case victoire")

    def test_victoire(self):
        self.assertTrue(self.carte.emplacements[9].fait_gagner(), "Cette case fait gagner")

    def test_non_victoire(self):
        self.assertFalse(self.carte.emplacements[8].fait_gagner(), "Cette case ne fait pas gagner")

    def test_bloque(self):
        self.assertTrue(self.carte.emplacements[0].bloque(), "Cette case bloque")

    def test_non_bloque(self):
        self.assertFalse(self.carte.emplacements[6].bloque(), "Cette case ne bloque pas")

    def test_porte_non_bloque(self):
        self.assertFalse(self.carte.emplacements[2].bloque(), "Une porte ne bloque pas")

    def test_valide(self):
        self.assertTrue(self.carte.emplacements[5].est_valide(), "Cette case est OK")

    def test_non_valide(self):
        self.assertFalse(self.carte.emplacements[0].est_valide(), "Cette case n'est pas OK")

    def test_non_valide_chevauche(self):
        self.assertFalse(
            self.carte.emplacements[5].est_valide(
                self.carte.emplacements[4]
            ), "Déplacement qui chevauche")


if __name__ == "__main__":

    unittest.main()
