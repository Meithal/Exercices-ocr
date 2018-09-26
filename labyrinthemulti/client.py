# Pour Openclass rooms
# Commande : "py -3 .\serveur.py"


import sys

if "pygame" in sys.argv:
    import jeu.logique_pygame as jeu
else:
    import jeu.logique_client as jeu

if __name__ == '__main__':
    jeu.client()
