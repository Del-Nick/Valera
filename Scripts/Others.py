import pymorphy3

morph = pymorphy3.MorphAnalyzer()


def get_sex_of_person_by_name(name: str) -> str:
    parsed_word = morph.parse(name)
    if parsed_word[0].tag.gender:
        return parsed_word[0].tag.gender[0]
    else:
        return '0'
