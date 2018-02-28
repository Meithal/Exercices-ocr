# -*- coding: utf-8 -*-

# Execute with "py -3 .\roboc.py"
# For OpenClass rooms

import os
import abc

SAVE_FILE = 'cur.txt'   # File that will be created for save the game
LEGAL_CHARS = ' O.XU'   # Characters absent from that string will be filtered out
BLOCKING_CHARS = 'O'    # Characters present in this string will block the path of the player
VICTORY_CHARS = 'U'     # Stepping on a character on this string triggers a win
PLAYER_CHAR = 'X'       # Character looked for to set initial position of player and as a sprite

VALID_INPUT_CHARS = 'QNSEO23456789'
MAX_LEN_INPUT = 100


class DisplayDriver:

    @staticmethod
    @abc.abstractmethod
    def draw(stream, break_line_when, player_index):
        """
        :param stream: un flux de caractères à afficher
        :param break_line_when: sauter une ligne a chaque fois
        qu'on a affiché ce nombre de caractères
        :param player_index: afficher le joueur à cette position
        :return: rien
        """
        pass


class ASCIIDisplay(DisplayDriver):
    """An ASCII display driver for the game"""
    @staticmethod
    def draw(stream, column_length, player_index):
        for (i, c) in enumerate(stream):
            if i == player_index:
                print(PLAYER_CHAR, end='')
            else:
                print(c, end='')
            if not (i + 1) % column_length:
                print()
        print()


class Game:

    display_driver = None
    levels = []
    current_map = None

    class Labyrinth:
        def __init__(self, stream, nom):

            self.id = len(Game.levels)

            self.steam = stream
            self.nom = nom

            self.column_length = len(self.steam.split("\n")[0].strip())

            for l in self.steam:
                if l not in LEGAL_CHARS:
                    self.steam = self.steam.replace(l, '')

            self.initial_player_position = self.steam.index(PLAYER_CHAR)

            self.steam = self.steam.replace(PLAYER_CHAR, ' ')

            self.player_position = self.initial_player_position

        def save(self):
            with open(SAVE_FILE, 'w') as f:
                f.write(self.nom + "\n" + str(self.player_position))

    @staticmethod
    def draw():
        Game.display_driver.draw(
            Game.current_map.stream,
            Game.current_map.column_length,
            Game.current_map.player_position
        )

    @staticmethod
    def execute_input(i):
        """
        This procedure changed the state of the game depending of the input.
        :param i: the characters stream that the player provided.
        :return: Boolean, if we return True, we ask an other input to the player, if False, the game stops.
        """
        i = i.strip().upper()
        i = i[:MAX_LEN_INPUT]
        for c in i:
            if c not in VALID_INPUT_CHARS:
                i = i.replace(c, '')
        if i == 'Q':
            return False
        if not i or i[0] not in 'NSEO':
            return True

        coord = i[0]  # N, S, E ou O
        how_many_repeats = 1
        if len(i) == 2 and i[1] in '23456789':
            how_many_repeats = int(i[1])

        for _ in range(how_many_repeats):
            destinations = {
                'N': Game.current_map.player_position - Game.current_map.column_length,
                'S': Game.current_map.player_position + Game.current_map.column_length,
                'E': Game.current_map.player_position + 1,
                'O': Game.current_map.player_position - 1
            }
            if destinations[coord] < 0 or destinations[coord] > len(Game.current_map.stream):
                return True
            if Game.current_map.flux[destinations[coord]] in BLOCKING_CHARS:
                return True
            elif Game.current_map.flux[destinations[coord]] in VICTORY_CHARS:
                print("Vous avez gagné !")
                os.unlink(SAVE_FILE)
                return False
            else:
                Game.current_map.player_position = destinations[coord]
                if _ < how_many_repeats - 1:
                    Game.draw()
                Game.current_map.save()
        return True

    @staticmethod
    def load_levels():
        """Instantiate every map into the game, so we can switch maps in the future, and pick one to play"""
        for f in os.listdir('maps'):
            with open('maps/' + f) as _:
                Game.levels.append(Game.Labyrinth(_.read(), f))

    @staticmethod
    def load_saved_game(file):
        with open(file) as _:
            try:
                name, place = _.read().split("\n")
                Game.current_map = next(_ for _ in Game.levels if _.nom == name)
                Game.current_map.player_position = int(place)
            except (IndexError, ValueError):
                print("Un problème est survenu en essayant de charger votre sauvegarde.")
                os.unlink(file)
                Game.current_map = None

    @staticmethod
    def start():
        Game.draw()
        while Game.execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n> ")):
            Game.draw()


if __name__ == "__main__":
    Game.display_driver = ASCIIDisplay()
    Game.load_levels()
    if not len(Game.levels):
        print("Aucune carte trouvée.")
        exit()
    if SAVE_FILE in os.listdir('.'):
        if input("Voulez-vous continuer la partie en cours ? (O/N)\n> ").strip().upper() == 'O':
            Game.load_saved_game(SAVE_FILE)
    if Game.current_map is None:
        print("Veuillez choisir une carte")
        for _ in Game.levels:
            print("[{}] {}".format(_.id + 1, _.nom.replace('.txt', '')))
        try:
            Game.current_map = Game.levels[int(input()) - 1]
        except (ValueError, IndexError):
            Game.current_map = Game.levels[0]

    Game.start()
