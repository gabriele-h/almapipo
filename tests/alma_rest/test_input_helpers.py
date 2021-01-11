"""
Tests for alma_rest.input_helpers
"""

from unittest import mock

import pytest

from alma_rest import input_helpers


@pytest.fixture
def prevent_check_file_path(monkeypatch):
    monkeypatch.setattr('alma_rest.input_read.check_file_path', lambda _: True)


@pytest.fixture
def csv_with_contents(monkeypatch):
    contents = [
        {'MMS-ID': '9981093873901234', 'Consortium-ID': 'XY0001'},
        {'MMS-ID': '9981093873911234', 'Consortium-ID': 'XY0002'}
    ]

    monkeypatch.setattr('alma_rest.input_read.read_csv_contents', lambda *_: contents)


@pytest.fixture
def csv_without_contents(monkeypatch):
    monkeypatch.setattr('alma_rest.input_read.read_csv_contents', lambda*_: {})


@pytest.fixture(autouse=True)
def mock_db_session(monkeypatch):
    monkeypatch.setattr('alma_rest.db_setup.create_db_session', lambda: mock.MagicMock())


@pytest.fixture
def db_writer(monkeypatch):
    writer = mock.MagicMock()
    monkeypatch.setattr('alma_rest.db_read_write.add_csv_line_to_source_csv_table', writer)
    return writer


class TestCsvAlmaIdGenerator:
    """
    Tests for alma_rest.input_helpers.csv_almaid_generator
    """

    def test_file_check_negative(self, prevent_check_file_path):
        with pytest.raises(ValueError):
            g = input_helpers.csv_almaid_generator('/path/to/csv')
            next(g)   # advance generator to provoke the exception

    def test_file_check_positive(self, csv_without_contents):
        g = input_helpers.csv_almaid_generator('/path/to/csv')
        assert list(g) == []

    def test_func_yields_all_entries(self, prevent_check_file_path, csv_with_contents):
        g = input_helpers.csv_almaid_generator('/path/to/csv')
        result = list(g)
        assert result == ['9981093873901234', '9981093873911234']

    def test_process_empty_csv(self, prevent_check_file_path, csv_without_contents):
        g = input_helpers.csv_almaid_generator('/path/to/csv')
        result = list(g)
        assert not result


class TestAddCsvToSourceCsvTable:
    """
    Tests for alma_rest.input_helpers.add_csv_to_source_csv_table
    """

    def test_all_entries_added_to_db(self, prevent_check_file_path, csv_with_contents, db_writer):
        input_helpers.add_csv_to_source_csv_table('/path/to/csv', '1970-01-01 00:00:00+00:00')
        assert db_writer.call_count == 2

    def test_no_entries_added_to_db(self, prevent_check_file_path, csv_without_contents, db_writer):
        input_helpers.add_csv_to_source_csv_table('/path/to/csv', '1970-01-01 00:00:00+00:00')
        assert db_writer.call_count == 0
