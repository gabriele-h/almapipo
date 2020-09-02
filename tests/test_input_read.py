"""Tests for read_input"""

from os import environ

import pytest

from alma_rest import input_read


class TestDoesStringEqualAlmaID:
    set_of_alma_ids = {
        '9981093873901234', '22447985240001234', '23447985190001234',
        '61363367390001234', '62363367380001234', '53375846240001234',
        '81445078000001234'
    }
    not_an_alma_id = '811234'
    string_empty = ""
    not_a_string = 1234567

    @pytest.fixture
    def set_env_id_suffix(self):
        old_suffix = environ.get('ALMA_REST_ID_INSTITUTIONAL_SUFFIX', '234')
        environ['ALMA_REST_ID_INSTITUTIONAL_SUFFIX'] = '234'
        yield
        environ['ALMA_REST_ID_INSTITUTIONAL_SUFFIX'] = old_suffix

    def test_alma_ids_only(self, set_env_id_suffix):
        assert all(input_read.is_this_an_alma_id(id_) for id_ in self.set_of_alma_ids)

    def test_containing_other(self):
        assert not input_read.is_this_an_alma_id(self.not_an_alma_id)

    def test_empty(self):
        assert not input_read.is_this_an_alma_id(self.string_empty)

    def test_number_not_string(self):
        assert not input_read.is_this_an_alma_id(self.not_a_string)

    def test_set_not_string_either(self):
        assert not input_read.is_this_an_alma_id(self.set_of_alma_ids)
