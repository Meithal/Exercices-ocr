from typing import Iterator

import jeu.reglages as regles
import jeu.emplacement as emplacement

from libs import lib_reseau


class Carte:
    """
    L'aire de jeu.

    Pour changer de niveau ou simplement commencer le jeu, il faut appeller load_level().
    """

    def __init__(self, nom, serveur):
        """Charge la carte donnée depuis un nom de fichier, positionne le joueur.

        Calcule la longueur d'une ligne, enlève tous les saut des lignes pour avoir un flux d'octets continu.
        Trouve les coordonnées du joueur et les sauvegarde.
        Enlève le sprite du jouer du flux
        Une fois l'index numérique du joueur trouvé, le remplace par un objet Emplacement

        :param nom: nom de la carte qu'on utilisera dans la fichier de sauvegarde.
        :param place_joueur: si supérieur à 0, force à celà l'emplacement du joueur, sinon
        la position du joueur sera celle par défaut. Permet de reprendre une partie en cours.
        """

        with open('cartes/' + nom) as texte:
            self.flux = texte.read()
        self.nom = nom
        self.taille_ligne = len(self.flux.splitlines()[0].strip())
        self.flux = self.flux.replace('\n', '').replace('\r', '').strip()
        self.position_par_defaut = self.flux.index(regles.CARACTERE_JOUEUR)
        self.flux = self.flux.replace(regles.CARACTERE_JOUEUR, ' ')

        self.emplacements = [
            emplacement.Emplacement(index, value, self) for index, value in enumerate(self.flux)
        ]

        self.position_par_defaut = self.emplacements[self.position_par_defaut]

        self.serveur = serveur
        self.joueurs = []
        self.joueur_actif = None

    def partie_commencee(self):
        return any([joueur.est_pret for joueur in self.joueurs])

    def afficher(self, pos_joueur = -1):
        """
        Affiche la carte, saute une ligne quand on a affiché un nombre de caractères équivalent  une ligne
        :return: string
        """
        idx_joueur = 1
        string = ""
        for e in self.emplacements:
            if e.index_ in [joueur.position.index_ for joueur in self.joueurs]:
                if pos_joueur == -1:
                    string += str(idx_joueur)
                    idx_joueur += 1
                else:
                    if pos_joueur == e.index_:
                        string += "X"
                    else:
                        string += "x"
            else:
                string += e.contenu
            if (e.index_ + 1) % self.taille_ligne == 0:
                string += '\n'
        string += '\n'
        return string

    def positions_occupees(self):
        for joueur in self.joueurs:
            yield joueur.position

    def departs_valides(self):
        for emplacement in self.emplacements:
            if emplacement.est_valide() and emplacement not in self.positions_occupees():
                yield emplacement

    def kick_deconnectes(self):
        """Kick de la carte les joueurs ayant perdu la connexion"""
        for joueur in (j for j in self.joueurs if not j.est_connecte()):
            print("Perdu la liaison avec %s" % joueur.port)
            self.joueurs.remove(joueur)

    def connexions_des_clients(self) -> Iterator[lib_reseau.Connexion]:
        self.kick_deconnectes()
        return (j.connexion for j in self.joueurs if j.connexion.est_connecte())

    def prochain_joueur(self):
        return self.joueurs[(self.joueurs.index(self.joueur_actif) + 1) % len(self.joueurs)]

    def joueurs_bavards(self):
        messages_clients = lib_reseau.clients_a_lire(self.connexions_des_clients())
        if messages_clients:
            for sock, message in messages_clients.items():
                yield self.joueurs[self.joueurs.index(sock)], message

    def gagnant(self):
        return any(joueur.gagnant for joueur in self.joueurs)