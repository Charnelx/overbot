import re
from functools import lru_cache
import json
import os

import nltk

from .constants import Languages, LettersSet


def _load_location_names() -> dict:
    working_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(working_dir, './resources/locations.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return json.loads(content)


@lru_cache(maxsize=None)
def load_ru_ua_location_names() -> dict:
    data = _load_location_names()
    locations = {item['name']['ru'].lower(): item['name']['uk'].lower() for item in data}
    return locations


@lru_cache(maxsize=None)
def load_ua_ru_location_names() -> dict:
    data = _load_location_names()
    locations = {item['name']['uk'].lower(): item['name']['ru'].lower() for item in data}
    return locations


def check_known_location_second_name(location):
    hardcoded_locations = {
        'днепр': 'днипро',
        'днепропетровск': 'днипро',
        'дніпропетровськ': 'днипро',
        'дніпропетрівськ': 'днипро',
        'днепродзержинск': 'каменское',
        'виница': 'винница',
        'волынь': 'волынь',
        'рівне': 'ровно'
    }
    return hardcoded_locations.get(location)


def create_misspelled_words_list(word: str, language: str) -> set:
    if language == Languages.RUSSIAN.value:
        letters = LettersSet.RUSSIAN_LETTERS.value
    elif language == Languages.UKRAINIAN.value:
        letters = LettersSet.UKRAINIAN_LETTERS.value
    else:
        raise NotImplementedError(f'Unsupported language: {language}')

    word = word.lower()

    # Peter Norvig's Spell Correction Algorithm - https://norvig.com/spell-correct.html
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def validate_location(location: str):
    """
    This method used to correct misspelled location names by creating a 1-Levenshtein distance
    words set from provided location name and searching for closest (appropriate) name from dictionary.
    Examples:
        validate_location('виница') -> винница
        validate_location('днепр') -> днипро
        validate_location('харьсков') -> харьков
    """
    def calculate_levenshtein_distance(locations_pair: tuple):
        # TODO: need to use coefficients based on words frequencies
        return nltk.edit_distance(locations_pair[0], locations_pair[1], transpositions=True)

    location_pattern = r'[іїє]'

    location = location.lower()

    # cove case when same location have different name
    # example: Днепр -> Днепропетровск -> Днипро
    location_second_name = check_known_location_second_name(location)
    if location_second_name:
        return location_second_name

    possible_locations = []
    # naive and straightforward hack to determine language
    if re.search(location_pattern, location):
        locations_dict = load_ua_ru_location_names()
        matched_location = locations_dict.get(location)
        if matched_location:
            return matched_location

        misspelled_location_name_variants = create_misspelled_words_list(location, Languages.UKRAINIAN.value)
        for misspelled_location in misspelled_location_name_variants:
            location_from_dict = locations_dict.get(misspelled_location)
            if location_from_dict:
                # this return tuple of (provided location, rus location name from dict)
                return misspelled_location
    else:
        locations_dict = load_ru_ua_location_names()
        matched_location = locations_dict.get(location)
        if matched_location:
            return location

        # will have to search in both dicts
        misspelled_location_name_variants_ru = create_misspelled_words_list(location, Languages.RUSSIAN.value)
        misspelled_location_name_variants_ukr = create_misspelled_words_list(location, Languages.UKRAINIAN.value)

        for misspelled_location in misspelled_location_name_variants_ru:
            location_from_dict = locations_dict.get(misspelled_location)
            if location_from_dict:
                # this adds tuple of (provided location, provided location in rus)
                possible_locations.append((location, misspelled_location))

        locations_dict = load_ua_ru_location_names()
        for misspelled_location in misspelled_location_name_variants_ukr:
            location_from_dict = locations_dict.get(misspelled_location)
            if location_from_dict:
                # this adds tuple of (provided location, rus location)
                possible_locations.append((location, location_from_dict))
        locations_pair = None
        if possible_locations:
            locations_pair = min(possible_locations, key=calculate_levenshtein_distance)
        if locations_pair:
            return locations_pair[1]
    return None
