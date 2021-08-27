"""Tests for read_input"""

from os import environ

import pytest

from almapipo import input_read


class TestDoesStringEqualAlmaID:
    set_of_almaids = {
        "9981093873901234", "22447985240001234", "23447985190001234",
        "61363367390001234", "62363367380001234", "53375846240001234",
        "81445078000001234"
    }

    @pytest.fixture
    def set_env_id_suffix(self):
        old_suffix = environ.get("ALMA_REST_ID_INSTITUTIONAL_SUFFIX", "234")
        environ["ALMA_REST_ID_INSTITUTIONAL_SUFFIX"] = "234"
        yield
        environ["ALMA_REST_ID_INSTITUTIONAL_SUFFIX"] = old_suffix

    def test_almaids_only(self, set_env_id_suffix):
        assert all(input_read.is_almaid(id_)
                   for id_ in self.set_of_almaids)

    def test_minimum_length(self):
        assert not input_read.is_almaid("811234")

    def test_empty(self):
        assert not input_read.is_almaid("")

    def test_number_not_string(self):
        assert not input_read.is_almaid(8156789234)

    def test_set_not_string_either(self):
        assert not input_read.is_almaid(self.set_of_almaids)
