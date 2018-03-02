# Execute with "py -3 .\roboc.py"
# For OpenClass rooms

import os

import game
from game import Game

class ASCIIDisplay:
    """An ASCII display driver for the game,
    since we have only one display output, no need to make a folder for those"""
    @staticmethod
    def draw(stream, column_length, player_index):
        for (i, c) in enumerate(stream):
            if i == player_index:
                print(game.settings.PLAYER_CHAR, end='')
            else:
                print(c, end='')
            if not (i + 1) % column_length:
                print(end='\n')
        print(end='\n')

    @staticmethod
    def send_notification(text):
        print(text)


def main():
    """We declare some variables here that we want to hide from the global scope"""
    if not len(Game.levels):
        game.notification(t_.NO_MAP_FOUND)
        exit()

    if game.settings.SAVE_FILE_NAME in os.listdir('.'):
        if input(t_.CONTINUE_GAME).strip().upper() == t_.YES_SHORT:
            level_name, position = game.saved_game_data(game.settings.SAVE_FILE_NAME)
            Game.set_level(level_name)
            Game.level().player_position = position
        else:
            os.unlink(game.settings.SAVE_FILE_NAME)

    if not Game.level():
        game.notification(t_.CHOOSE_MAP)
        for i, _ in enumerate(Game.levels):
            game.notification("[{}] {}".format(i + 1, _.name.replace('.txt', '')))
        Game.set_level(input())

    Game.level().draw()
    while Game.execute_input(input(t_.GAME_INPUT_PROMPT)):
        Game.level().draw()


if __name__ == "__main__":
    game.languages.set_language(game.settings.LANGUAGE)
    from game.languages import t_  # we need it in this file too
    Game.set_language(t_)
    Game.display_driver = globals()[game.settings.DISPLAY_DRIVER]()
    Game.levels = list(game.load_levels())

    main()
