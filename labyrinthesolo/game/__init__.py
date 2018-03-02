import os
import game.settings
import game.languages

t_ = game.languages.t_

def load_levels():
    """Instantiate every map into the game, so we can switch maps in the future, and pick one to play now"""
    for f in os.listdir('maps'):
        with open('maps/' + f) as _:
            yield Game.Level(_.read(), f)


def saved_game_data(file):
    """Reads a save file and return the name of the level and the position of the player"""
    with open(file) as _:
        level_name, place = _.read().split("\n")
    return level_name, int(place)


def notification(text):
    Game.display_driver.send_notification(text)


class Game:

    display_driver = None
    levels = []
    _currently_playing = -1

    class Level:
        def __init__(self, stream, name):

            self.stream = stream
            self.name = name
            self.column_length = len(self.stream.splitlines()[0])
            self.stream = ''.join(self.stream.splitlines())
            self.initial_player_position = self.stream.index(settings.PLAYER_CHAR)
            self.stream = self.stream.replace(settings.PLAYER_CHAR, ' ')
            self.player_position = self.initial_player_position

        def save(self):
            with open(settings.SAVE_FILE_NAME, 'w') as f:
                f.write(self.name + "\n" + str(self.player_position))

        def draw(self):
            Game.display_driver.draw(
                self.stream,
                self.column_length,
                self.player_position
            )

    class Language:
        language = game.languages.t_
        def __get__(self, instance, owner):
            return self.language

        def __set__(self, instance, value):
    language = Language()

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

        if i == t_.INPUT_LEAVE:
            return False

        direction = i[0]
        how_many_repeats = 1
        if len(i) == 2 and i[1] in '23456789':
            how_many_repeats = int(i[1])

        for _ in range(how_many_repeats):

            destination = {
                t_.INPUT_NORTH: Game.level().player_position - Game.level().column_length,
                t_.INPUT_SOUTH: Game.level().player_position + Game.level().column_length,
                t_.INPUT_EAST: Game.level().player_position + 1,
                t_.INPUT_WEST: Game.level().player_position - 1
            }.get(direction, Game.level().player_position)

            if destination < 0 or destination > len(Game.level().stream):
                return True

            if Game.level().stream[destination] in settings.BLOCKING_CHARS:
                return True

            if Game.level().stream[destination] in settings.VICTORY_CHARS:
                notification(t_.YOU_WIN)
                os.unlink(settings.SAVE_FILE_NAME)
                return False

            Game.level().player_position = destination

            if _ < how_many_repeats - 1:
                Game.level().draw()

            Game.level().save()

        return True

    @classmethod
    def set_level(cls, requested_level):
        """Accepts either a level name provided by a save file, or a number input that we sanitize"""
        level_names = [_.name for _ in cls.levels]
        if requested_level in level_names:
            level_index = level_names.index(requested_level)
        else:
            level_index = requested_level.isdigit() and int(requested_level) - 1 or 0
            if level_index not in range(len(cls.levels)):
                level_index = 0
        cls._currently_playing = level_index

    @classmethod
    def level(cls):
        if not cls._currently_playing == -1:
            return cls.levels[cls._currently_playing]

    @staticmethod
    def set_language(lang):
        game.t_ = lang
