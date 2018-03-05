import languages.fr
import languages.en

language_map = {
    'fr': fr,
    'en': en
}

def get_language(val):
    return language_map[val]