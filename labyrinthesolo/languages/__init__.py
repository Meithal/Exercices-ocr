import languages.fr
import languages.en

translate = languages.en


def set_language(lang_code):
    languages.translate = {
        'fr': languages.fr,
        'en': languages.en
    }.get(lang_code, languages.en)
