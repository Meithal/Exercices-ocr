HOTE_CONNEXION = 'localhost'
PORT_CONNEXION = 12800

CARACTERE_PORTE = '.'
CARACTERE_MUR = 'O'
BLOCKING_CHARS = CARACTERE_MUR  # tous les caracteres de cette chaine bloqueront la progression du joueur
VICTORY_CHARS = 'U'  # marcher sur un des caracteres presents dans cette chaine fait gagner la partie
IMPOSSIBLE_STARTING_CHARS = BLOCKING_CHARS + VICTORY_CHARS
CARACTERE_JOUEUR = 'X'  # ce caractere sera recherche dans le flux de la carte pour determiner
#  la position initiale du joueur, il sera affiché comme sprite du joueur
LONGUEUR_MAX_INPUT = 100

CHAINE_COMMENCER = "c"
