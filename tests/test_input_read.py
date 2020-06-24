"""Tests for read_input"""

import os

import pytest

import input_read


class TestDoesStringEqualAlmaID:
    set_of_alma_ids = {
        '9981093873903332', '22447985240003332', '23447985190003332',
        '61363367390003332', '62363367380003332', '53375846240003332',
        '81445078000003332'
    }
    not_an_alma_id = '813332'
    string_empty = ""
    not_a_string = 1234567

    @pytest.fixture
    def set_env_id_suffix(self):
        old_suffix = os.environ.get('ALMA_REST_ID_INSTITUTIONAL_SUFFIX', '')
        os.environ['ALMA_REST_ID_INSTITUTIONAL_SUFFIX'] = '3332'
        yield
        os.environ['ALMA_REST_ID_INSTITUTIONAL_SUFFIX'] = old_suffix

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
