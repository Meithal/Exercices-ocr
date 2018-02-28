# Execute with "py -3 .\roboc.py"
# For OpenClass rooms

import os

import settings
import languages


class ASCIIDisplay:
    """An ASCII display driver for the game"""
    @staticmethod
    def draw(stream, column_length, player_index):
        for (i, c) in enumerate(stream):
            if i == player_index:
                print(settings.PLAYER_CHAR, end='')
            else:
                print(c, end='')
            if not (i + 1) % column_length:
                print(end="\n")
        print(end="\n")

    @staticmethod
    def send_notification(text):
        print(text)


class Game:

    display_driver = None
    levels = []
    _currently_playing = -1

    class Labyrinth:
        def __init__(self, stream, name):

            self.stream = stream
            self.name = name
            self.column_length = len(self.stream.split("\n")[0].strip())

            ob = ""
            for _ in self.stream:
                if _ in settings.LEGAL_CHARS:
                    ob += _
            self.stream = ob

            self.initial_player_position = self.stream.index(settings.PLAYER_CHAR)

            self.stream = self.stream.replace(settings.PLAYER_CHAR, ' ')

            self.player_position = self.initial_player_position

        def save(self):
            level_index = [_.name for _ in Game.levels].index(self.name)
            with open(settings.SAVE_FILE, 'w') as f:
                f.write(str(level_index) + "\n" + str(self.player_position))

    @staticmethod
    def draw():
        Game.display_driver.draw(
            Game.level().stream,
            Game.level().column_length,
            Game.level().player_position
        )

    @classmethod
    def notification(cls, text):
        Game.display_driver.send_notification(text)

    @classmethod
    def execute_input(cls, i):
        """
        This procedure changes the state of the game depending of the input.
        :param i: the input string that the player provided.
        :return: Boolean, if we return True, we ask an other input to the player, if False, the game stops.
        """
        i = i[:settings.MAX_LEN_INPUT].strip().upper()
        if not i:
            return True
        if i == _t.LEAVE:
            return False

        direction = i[0]
        how_many_repeats = 1
        if len(i) == 2 and i[1] in '23456789':
            how_many_repeats = int(i[1])

        for _ in range(how_many_repeats):
            destination = {
                _t.NORTH: Game.level().player_position - Game.level().column_length,
                _t.SOUTH: Game.level().player_position + Game.level().column_length,
                _t.EAST: Game.level().player_position + 1,
                _t.WEST: Game.level().player_position - 1
            }.get(direction, Game.level().player_position)
            if destination < 0 or destination > len(Game.level().stream):
                return True
            if Game.level().stream[destination] in settings.BLOCKING_CHARS:
                return True
            elif Game.level().stream[destination] in settings.VICTORY_CHARS:
                Game.notification(_t.YOU_WIN)
                os.unlink(settings.SAVE_FILE)
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

    @classmethod
    def level(cls):
        if not cls._currently_playing == -1:
            return cls.levels[cls._currently_playing]

    @staticmethod
    def saved_game_data(file):
        with open(file) as _:
            level_index, place = _.read().split("\n")
        return int(level_index), int(place)

    @staticmethod
    def set_language(code):
        languages.set_language(code)

    @staticmethod
    def start():
        Game.draw()
        while Game.execute_input(input(_t.GAME_INPUT_PROMPT)):
            Game.draw()


def main():
    """Hide some variable declarations from global scope here"""
    Game.display_driver = globals()[settings.DISPLAY_DRIVER]()
    Game.levels = list(Game.load_levels())
    if not len(Game.levels):
        Game.notification(_t.NO_MAP_FOUND)
        exit()

    if settings.SAVE_FILE in os.listdir('.'):
        if input(_t.CONTINUE_GAME).strip().upper() == _t.YES_SHORT:
            level_index, position = Game.saved_game_data(settings.SAVE_FILE)
            Game.set_level(level_index)
            Game.level().player_position = position
        else:
            os.unlink(settings.SAVE_FILE)

    if not Game.level():
        Game.notification(_t.CHOOSE_MAP)
        for i, _ in enumerate(Game.levels):
            Game.notification("[{}] {}".format(i + 1, _.name.replace('.txt', '')))
        Game.set_level(int(input()) - 1)

    Game.start()


if __name__ == "__main__":
    Game.set_language(settings.LANGUAGE)
    from languages import translate as _t  # 't' is for 'translate', make it global, not local to main()
    main()
