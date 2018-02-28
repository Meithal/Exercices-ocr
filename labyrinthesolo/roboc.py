# -*- coding: utf-8 -*-

# Execute with "py -3 .\roboc.py"
# For OpenClass rooms

import os

SAVE_FILE = 'cur.txt'   # File that will be created for save the game
LEGAL_CHARS = ' O.XU'   # Characters absent from that string will be filtered out
BLOCKING_CHARS = 'O'    # Characters present in this string will block the path of the player
VICTORY_CHARS = 'U'     # Stepping on a character on this string triggers a win
PLAYER_CHAR = 'X'       # Character looked for to set initial position of player and as a sprite

VALID_INPUT_CHARS = 'QNSEO23456789'
MAX_LEN_INPUT = 100


class ASCIIDisplay:
    """An ASCII display driver for the game"""
    @staticmethod
    def draw(stream, column_length, player_index):
        for (i, c) in enumerate(stream):
            if i == player_index:
                print(PLAYER_CHAR, end='')
            else:
                print(c, end='')
            if not (i + 1) % column_length:
                print(end="\n")
        print(end="\n")


class Game:

    display_driver = None
    levels = []
    _currently_playing = -1

    @classmethod
    def level(cls):
        if not cls._currently_playing == -1:
            return cls.levels[cls._currently_playing]

    class Labyrinth:
        def __init__(self, stream, name):

            self.stream = stream
            self.name = name
            self.column_length = len(self.stream.split("\n")[0].strip())

            ob = ""
            for _ in self.stream:
                if _ in LEGAL_CHARS:
                    ob += _
            self.stream = ob

            self.initial_player_position = self.stream.index(PLAYER_CHAR)

            self.stream = self.stream.replace(PLAYER_CHAR, ' ')

            self.player_position = self.initial_player_position

        def save(self):
            level_index = [_.name for _ in Game.levels].index(self.name)
            with open(SAVE_FILE, 'w') as f:
                f.write(str(level_index) + "\n" + str(self.player_position))

    @staticmethod
    def draw():
        Game.display_driver.draw(
            Game.level().stream,
            Game.level().column_length,
            Game.level().player_position
        )

    @classmethod
    def execute_input(cls, i):
        """
        This procedure changed the state of the game depending of the input.
        :param i: the input string that the player provided.
        :return: Boolean, if we return True, we ask an other input to the player, if False, the game stops.
        """
        i = i[:MAX_LEN_INPUT].strip().upper()
        if not i:
            return True
        if i == 'Q':
            return False

        how_many_repeats = 1
        if len(i) == 2 and i[1] in '23456789':
            how_many_repeats = int(i[1])

        for _ in range(how_many_repeats):
            destination = {
                'N': Game.level().player_position - Game.level().column_length,
                'S': Game.level().player_position + Game.level().column_length,
                'E': Game.level().player_position + 1,
                'O': Game.level().player_position - 1
            }.get(i[0], Game.level().player_position)
            if destination < 0 or destination > len(Game.level().stream):
                return True
            if Game.level().stream[destination] in BLOCKING_CHARS:
                return True
            elif Game.level().stream[destination] in VICTORY_CHARS:
                print("Vous avez gagné !")
                os.unlink(SAVE_FILE)
                return False
            else:
                Game.level().player_position = destination
                if _ < how_many_repeats - 1:
                    Game.draw()
                Game.level().save()
        return True

    @staticmethod
    def load_levels():
        """Instantiate every map into the game, so we can switch maps in the future, and pick one to play now"""
        for f in os.listdir('maps'):
            with open('maps/' + f) as _:
                yield Game.Labyrinth(_.read(), f)

    @classmethod
    def set_level(cls, level_index):
        if level_index not in range(len(cls.levels)):
            level_index = 0
        cls._currently_playing = level_index

    @staticmethod
    def saved_game_data(file):
        with open(file) as _:
            level_index, place = _.read().split("\n")
        return level_index, place

    @staticmethod
    def start():
        Game.draw()
        while Game.execute_input(input("Veuillez entrer une commande (Q: Quitter, N/S/E/O(2-9) : Se diriger\n> ")):
            Game.draw()


def main():
    Game.display_driver = ASCIIDisplay()
    Game.levels = list(Game.load_levels())
    if not len(Game.levels):
        print("Aucune carte trouvée.")
        exit()
    if SAVE_FILE in os.listdir('.'):
        if input("Voulez-vous continuer la partie en cours ? (O/N)\n> ").strip().upper() == 'O':
            level_index, position = Game.saved_game_data(SAVE_FILE)
            Game.set_level(level_index)
            Game.level().player_position = position
        else:
            os.unlink(SAVE_FILE)

    if not Game.level():
        print("Veuillez choisir une carte")
        for i, _ in enumerate(Game.levels):
            print("[{}] {}".format(i + 1, _.name.replace('.txt', '')))
        Game.set_level(int(input()) - 1)

    Game.start()


if __name__ == "__main__":
    main()
