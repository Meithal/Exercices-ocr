DISPLAY_DRIVER = 'ASCIIDisplay'  # change that if we want to have different output driver for better graphics
LANGUAGE = 'fr'

SAVE_FILE_NAME = 'cur.txt'   # File that will be created for save the game
LEGAL_CHARS = ' O.XU'   # Characters absent from that string will be filtered out
BLOCKING_CHARS = 'O'    # Characters present in this string will block the path of the player
VICTORY_CHARS = 'U'     # Stepping on a character on this string triggers a win
PLAYER_CHAR = 'X'       # Character looked for to set initial position of player and as a sprite

VALID_INPUT_CHARS = 'QNSEO23456789'
MAX_LEN_INPUT = 100
