import os
import languages
import settings

t_ = languages.get_language(settings.LANGUAGE)


def load_levels():
    for f in os.listdir('maps'):
        with open('maps/' + f) as _:
            yield Game.Level(_.read(), f)


def saved_game_data(file):
    with open(file) as _:
        level_name, place = _.read().split("\n")
    return level_name, int(place)


class Game:

    _currently_playing = -1
    levels = []

    def __enter__(self):
        # load levels in memory only once
        if not len(Game.levels):
            Game.levels = list(load_levels())

        return self

    class NoMapsFound(Exception):
        pass

    class Victory(Exception):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is Game.NoMapsFound:
            self.notification(t_.NO_MAPS_FOUND)
        if exc_type is Game.Victory:
            os.unlink(settings.SAVE_FILE_NAME)
            self.notification(t_.YOU_WIN)

        self.notification(t_.THANKS_FOR_PLAYING)

        return exc_type is Game.Victory

    @staticmethod
    def notification(text):
        print(text)

    @property
    def level(self):
        if self._currently_playing >= 0:
            return Game.levels[self._currently_playing]

    @level.setter
    def level(self, requested_level):
        """Accepts either a level name provided by a save file, or a number input that we sanitize"""
        level_names = [_.name for _ in Game.levels]
        if requested_level in level_names:
            level_index = level_names.index(requested_level)
        else:
            level_index = requested_level.isdigit() and int(requested_level) - 1 or 0
            if level_index not in range(len(Game.levels)):
                level_index = 0
        self._currently_playing = level_index

    class Level:
        def __init__(self, stream, name):
            self.stream = stream
            self.name = name
            self.column_length = len(self.stream.splitlines()[0])
            self.stream = ''.join(self.stream.splitlines())
            self.player_position = self.stream.index(settings.PLAYER_CHAR)
            self.stream = self.stream.replace(settings.PLAYER_CHAR, ' ')

        def save(self):
            with open(settings.SAVE_FILE_NAME, 'w') as f:
                f.write(self.name + "\n" + str(self.player_position))

        def draw(self):
            for (i, c) in enumerate(self.stream):
                if i == self.player_position:
                    print(settings.PLAYER_CHAR, end='')
                else:
                    print(c, end='')
                if not (i + 1) % self.column_length:
                    print(end='\n')
            print(end='\n')

    def execute_input(self, i):
        """
        This procedure changes the state of the game depending of the input.
        :param i: the input string that the player provided.
        :return: As long as we return True, the game asks for an input.
        """
        i = i[:settings.MAX_LEN_INPUT].strip().upper()
        level = self.level

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
                t_.INPUT_NOR: level.player_position - level.column_length,
                t_.INPUT_STH: level.player_position + level.column_length,
                t_.INPUT_EST: level.player_position + 1,
                t_.INPUT_WST: level.player_position - 1
            }.get(direction, level.player_position)

            if destination < 0 or destination > len(self.level.stream):
                return True  # OOB check

            if self.level.stream[destination] in settings.BLOCKING_CHARS:
                return True

            if self.level.stream[destination] in settings.VICTORY_CHARS:
                raise Game.Victory

            self.level.player_position = destination

            if _ < how_many_repeats - 1:
                self.level.draw()

            self.level.save()

        return True
