# pylint: disable=no-self-use

from unittest import mock

import pytest

from scrapper.utils.spelling.checker import (
    _load_json_data, load_ru_ua_location_names, load_ua_ru_location_names, load_locations_frequencies,
    create_misspelled_words_list, validate_location, check_known_location_second_name
)
from scrapper.utils.spelling.constants import Languages


class TestChecker:

    def test_load_json_data(self):
        with mock.patch('builtins.open', mock.mock_open(read_data='{"foo": "bar"}'), create=True) as _:
            result = _load_json_data('')

        assert result == {'foo': 'bar'}

    def test_load_ru_ua_location_names(self):
        locations_data = '[{"name": {"ru": "Киев", "uk": "Київ"}}]'
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            load_ru_ua_location_names.cache_clear()
            data = load_ru_ua_location_names()

        assert data == {'киев': 'київ'}

    def test_load_ua_ru_location_names(self):
        locations_data = '[{"name": {"ru": "Киев", "uk": "Київ"}}]'
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            load_ua_ru_location_names.cache_clear()
            data = load_ua_ru_location_names()

        assert data == {'київ': 'киев'}

    def test_load_locations_frequencies(self):
        locations_data = '{"киев": 1}'
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            load_locations_frequencies.cache_clear()
            data = load_locations_frequencies()

        assert data == {"киев": 1}

    def test_create_misspelled_words_list(self):
        location = 'киев'
        misspelled_words = create_misspelled_words_list(location, Languages.RUSSIAN.value)
        assert len(misspelled_words) == 297

        assert location in misspelled_words

        # len(word) -+ 1 for deletes & inserts
        assert len(min(misspelled_words, key=len)) == 3
        assert len(max(misspelled_words, key=len)) == 5

        # replaced chars in word
        assert 'кеив' in misspelled_words

        # transpose chars in word
        assert 'икев' in misspelled_words

    def test_create_misspelled_words_list_other_lang(self):
        with pytest.raises(NotImplementedError) as err:
            create_misspelled_words_list('kyiv', 'eng')

        assert str(err.value) == 'Unsupported language: eng'

    def test_check_known_location_second_name(self):
        assert check_known_location_second_name('днепр') == 'днипро'

    def test_validate_location_matched_dict_ua(self):
        locations_data = '[{"name": {"ru": "Днипро", "uk": "Дніпро"}}]'
        load_ua_ru_location_names.cache_clear()
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            result = validate_location('дніпро')
        assert result == 'днипро'

    def test_validate_location_misspelled_ua(self):
        locations_data = '[{"name": {"ru": "Днипро", "uk": "Дніпро"}}]'
        load_ua_ru_location_names.cache_clear()
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            result = validate_location('дінпро')
        assert result == 'днипро'

    def test_validate_location_no_match_ua(self):
        locations_data = '[{"name": {"ru": "Днипро", "uk": "Дніпро"}}]'
        load_ua_ru_location_names.cache_clear()
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            result = validate_location('йцукен')
        assert result is None

    def test_validate_location_matched_dict_ru(self):
        locations_data = '[{"name": {"ru": "Днипро", "uk": "Дніпро"}}]'
        load_ru_ua_location_names.cache_clear()
        with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
            result = validate_location('днипро')
        assert result == 'днипро'

    def test_validate_location_misspelled_ru(self):
        locations_data = '[{"name": {"ru": "Днипро", "uk": "Дніпро"}}]'
        load_ru_ua_location_names.cache_clear()
        load_ua_ru_location_names.cache_clear()
        load_locations_frequencies.cache_clear()
        with mock.patch('builtins.open', mock.mock_open(read_data='{}'), create=True) as _:
            with mock.patch('builtins.open', mock.mock_open(read_data=locations_data), create=True) as _:
                with mock.patch('scrapper.utils.spelling.checker.load_locations_frequencies') as freq_mock:
                    freq_mock.return_value = {}
                    result = validate_location('днепро')

        assert result == 'днипро'
