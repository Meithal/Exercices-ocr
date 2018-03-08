import game.languages.en
import game.languages.fr

t_ = en  # import that variable whenever you need translated text, set the current language


def set_language(lang_code):
    game.languages.t_ = {
        'fr': fr,
        'en': en
    }.get(lang_code, en)

