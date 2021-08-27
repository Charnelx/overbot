import enum


class Languages(enum.Enum):

    UKRAINIAN = 'ua'
    RUSSIAN = 'ru'


class LettersSet(enum.Enum):

    UKRAINIAN_LETTERS = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
    RUSSIAN_LETTERS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
