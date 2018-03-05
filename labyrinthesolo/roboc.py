# Execute with "py -3 .\roboc.py"
# For OpenClass rooms

import os

import settings
import languages
import game


def main():
    """This function is only useful to not pollute global namespace with variables"""
    if settings.SAVE_FILE_NAME in os.listdir('.'):
        if input(t_.CONTINUE_GAME).strip().upper() == t_.SHORT_YES:
            level_name, position = game.saved_game_data(settings.SAVE_FILE_NAME)
            Game.level = level_name
            Game.level.player_position = position
        else:
            os.unlink(settings.SAVE_FILE_NAME)

    if not Game.level:
        Game.notification(t_.CHOOSE_MAP)
        for i, _ in enumerate(Game.levels):
            Game.notification("[{}] {}".format(i + 1, _.name.replace('.txt', '')))
        Game.level = input("> ")


if __name__ == "__main__":

    t_ = languages.get_language(settings.LANGUAGE)

    with game.Game() as Game:

        if not len(Game.levels):
            raise Game.NoMapsFound

        main()

        Game.level.draw()
        while Game.execute_input(input(t_.GAME_INPUT_PROMPT)):
            Game.level.draw()
