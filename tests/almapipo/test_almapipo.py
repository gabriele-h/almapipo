"""Tests for almapipo.almapipo"""

from unittest import mock

import pytest
from sqlalchemy.orm import Session

from almapipo import (
    almapipo,
    db_write,
    rest_acq,
    rest_bibs,
    rest_electronic,
    rest_users,
    setup_rest
)


@pytest.fixture()
def db_session(monkeypatch):
    db_session = mock.Mock(spec_set=Session)
    return db_session


@pytest.fixture
def db_add_status_writer(monkeypatch):
    add_status_writer = mock.MagicMock()
    monkeypatch.setattr("almapipo.db_write.add_almaid_to_job_status_per_id", add_status_writer)
    return add_status_writer


@pytest.fixture
def db_update_status_writer(monkeypatch):
    update_status_writer = mock.MagicMock()
    monkeypatch.setattr("almapipo.db_write.update_job_status", update_status_writer)
    return update_status_writer


@pytest.fixture
def db_fetched_writer(monkeypatch):
    fetched_writer = mock.MagicMock()
    monkeypatch.setattr("almapipo.db_write.add_response_content_to_fetched_records", fetched_writer)
    return fetched_writer


@pytest.fixture
def db_put_post_response_writer(monkeypatch):
    response_writer = mock.MagicMock()
    monkeypatch.setattr("almapipo.db_write.add_put_post_response", response_writer)
    return response_writer


@pytest.fixture
def response_bib_record_created(monkeypatch):
    def mock_create(*args, **kwargs):
        return MockCreateBibResponse.record

    monkeypatch.setattr(setup_rest.GenericApi, "create", mock_create)


@pytest.fixture
def response_bib_record_retrieved(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockRetrieveBibResponse.record

    monkeypatch.setattr(setup_rest.GenericApi, "retrieve", mock_get)


@pytest.fixture
def response_bib_record_deleted(monkeypatch):
    def mock_delete(*args, **kwargs):
        return MockDeleteBibResponse

    monkeypatch.setattr(setup_rest.GenericApi, "delete", mock_delete)


@pytest.fixture
def response_bib_record_updated(monkeypatch):
    def mock_update(*args, **kwargs):
        return MockRetrieveBibResponse.record

    monkeypatch.setattr(setup_rest.GenericApi, 'update', mock_update)


class MockCreateBibResponse:
    record = b"""<bib link="string">
        <mms_id>991129830000541</mms_id>
        <record_format>marc21</record_format>
        <linked_record_id type="string">
            <xml_value></xml_value>
        </linked_record_id>
        <title>Mythology /</title>
        <author>Harrison, Jane Ellen,</author>
        <issn></issn>
        <isbn></isbn>
        <complete_edition></complete_edition>
        <network_numbers>
            <network_number></network_number>
        </network_numbers>
        <place_of_publication>Boston :</place_of_publication>
        <date_of_publication>1924</date_of_publication>
        <publisher_const>Marshall Jones</publisher_const>
        <holdings link="string">
            <xml_value>/almaws/v1/bibs/991129830000541/holdings</xml_value>
        </holdings>
        <created_by>exl_impl</created_by>
        <created_date>2013-11-05Z</created_date>
        <last_modified_by>exl_impl</last_modified_by>
        <last_modified_date>2014-01-20Z</last_modified_date>
        <suppress_from_publishing>false</suppress_from_publishing>
        <suppress_from_external_search>false</suppress_from_external_search>
        <sync_with_oclc>BIBS</sync_with_oclc>
        <sync_with_libraries_australia>NONE</sync_with_libraries_australia>
        <originating_system>ILS</originating_system>
        <originating_system_id>120033845110</originating_system_id>
        <cataloging_level desc="string">
            <xml_value>00</xml_value>
        </cataloging_level>
        <warnings>
            <warning>
                <message></message>
            </warning>
        </warnings>
        <requests link="string">
            <xml_value>100</xml_value>
        </requests>
    </bib>"""

    @staticmethod
    def create(self):
        return self.record


class MockRetrieveBibResponse:
    record = b"""<bib>
        <mms_id>991430610000121</mms_id>
        <record_format>marc21</record_format>
        <record>
            <leader>00260nam a2200109 u 4500</leader>
            <controlfield tag="001">991122800000121</controlfield>
            <controlfield tag="005">20140120122820.0</controlfield>
            <controlfield tag="008">131105s2013 xx r 000 0 gsw d</controlfield>
            <datafield ind1="1" ind2=" " tag="100">
                <subfield code="a">Smith, John</subfield>
            </datafield>
            <datafield ind1="1" ind2="0" tag="245">
                <subfield code="a">Book of books</subfield>
            </datafield>
        </record>
    </bib>"""

    @staticmethod
    def retrieve(self):
        return self.record


class MockDeleteBibResponse:
    @staticmethod
    def delete():
        return None


class TestCallApi:
    """
    Tests for all the call_api* functions in the module.
    """

    class TestCallApiForRecord:

        def test_call_api_for_record_get_bib(
                self,
                db_add_status_writer,
                db_fetched_writer,
                db_put_post_response_writer,
                db_session,
                db_update_status_writer,
                response_bib_record_retrieved
        ):
            almapipo.call_api_for_record('991430610000121', 'bibs', 'bibs', 'GET', db_session)
            assert db_add_status_writer.call_count == 1 \
                   and db_fetched_writer.call_count == 1 \
                   and db_put_post_response_writer.call_count == 0 \
                   and db_update_status_writer.call_count == 1

        def test_call_api_for_record_delete_bib(
                self,
                db_add_status_writer,
                db_fetched_writer,
                db_put_post_response_writer,
                db_session,
                db_update_status_writer,
                response_bib_record_retrieved,
                response_bib_record_deleted
        ):
            almapipo.call_api_for_record('991430610000121', 'bibs', 'bibs', 'DELETE', db_session)
            assert db_add_status_writer.call_count == 2 \
                   and db_fetched_writer.call_count == 1 \
                   and db_put_post_response_writer.call_count == 0 \
                   and db_update_status_writer.call_count == 2

        def test_call_api_for_record_update_bib(
                self,
                db_add_status_writer,
                db_fetched_writer,
                db_put_post_response_writer,
                db_session,
                db_update_status_writer,
                response_bib_record_retrieved,
                response_bib_record_updated
        ):
            def dont_manipulate(id_list, input):
                return input

            almapipo.call_api_for_record('991430610000121', 'bibs', 'bibs', 'PUT', db_session, dont_manipulate)
            assert db_add_status_writer.call_count == 2 \
                   and db_fetched_writer.call_count == 1 \
                   and db_put_post_response_writer.call_count == 1 \
                   and db_update_status_writer.call_count == 2

        def test_call_api_for_record_create_bib(
                self,
                db_add_status_writer,
                db_fetched_writer,
                db_put_post_response_writer,
                db_session,
                db_update_status_writer,
                response_bib_record_created
        ):
            record_data = MockCreateBibResponse().record
            almapipo.call_api_for_record('', 'bibs', 'bibs', 'POST', db_session, None, record_data)
            assert db_add_status_writer.call_count == 1 \
                   and db_fetched_writer.call_count == 0 \
                   and db_put_post_response_writer.call_count == 1 \
                   and db_update_status_writer.call_count == 1


class TestInstantiateApiClass:
    """
    Tests for almapipo.almapipo.instantiate_api_class
    Tests for specific kinds of APIs will be listed in their own inner classes,
        e. g. TestInstantiateApiClassBibs
    Tests for NotImplementedErrors are indicated by the string "nonexistent"
    """

    def test_instantiate_api_class_nonexistent(self):
        with pytest.raises(NotImplementedError):
            almapipo.instantiate_api_class("123", "nonexistent", "bibs")

    class TestInstantiateApiClassAcq:

        def test_instantiate_api_class_acq_vendors(self):
            current_api = almapipo.instantiate_api_class(
                "TEST", "acq", "vendors"
            )
            assert isinstance(current_api, rest_acq.VendorsApi) \
                   and current_api.base_path == "/acq/vendors/"

        def test_instantiate_api_class_acq_nonexistent(self):
            with pytest.raises(NotImplementedError):
                almapipo.instantiate_api_class(
                    "TEST", "acq", "nonexistent"
                )

    class TestInstantiateApiClassBibs:

        def test_instantiate_api_class_bibs_bibs(self):
            current_api = almapipo.instantiate_api_class(
                "9981093873901234", "bibs", "bibs"
            )
            assert isinstance(current_api, rest_bibs.BibsApi) \
                and current_api.base_path == "/bibs/"

        def test_instantiate_api_class_bibs_holdings(self):
            current_api = almapipo.instantiate_api_class(
                "9981093873901234,22447985240001234", "bibs", "holdings"
            )
            assert isinstance(current_api, rest_bibs.HoldingsApi) \
                and current_api.base_path == "/bibs/9981093873901234/holdings/"

        def test_instantiate_api_class_bibs_items(self):
            current_api = almapipo.instantiate_api_class(
                "9981093873901234,22447985240001234,23447985190001234",
                "bibs",
                "items"
            )
            assert isinstance(current_api, rest_bibs.ItemsApi) \
                and current_api.base_path == "/bibs/9981093873901234/" \
                                             "holdings/22447985240001234/items/"

        def test_instantiate_api_class_bibs_portfolios(self):
            current_api = almapipo.instantiate_api_class(
                "9981093873901234", "bibs", "portfolios"
            )
            assert isinstance(current_api, rest_bibs.PortfoliosApi) \
                and current_api.base_path == "/bibs/9981093873901234/" \
                                             "portfolios/"

        def test_instantiate_api_class_bibs_nonexistent(self):
            with pytest.raises(NotImplementedError):
                almapipo.instantiate_api_class(
                    "9981093873901234", "bibs", "nonexistent"
                )

    class TestInstantiateApiClassElectronic:

        def test_instantiate_api_class_electronic_ecollections(self):
            current_api = almapipo.instantiate_api_class(
                "6181093873901234", "electronic", "e-collections"
            )
            assert isinstance(current_api, rest_electronic.EcollectionsApi) \
                and current_api.base_path == "/electronic/e-collections/"

        def test_instantiate_api_class_electronic_eservices(self):
            current_api = almapipo.instantiate_api_class(
                "6181093873901234,6281093873901234", "electronic", "e-services"
            )
            assert isinstance(current_api, rest_electronic.EservicesApi) \
                and current_api.base_path == "/electronic/e-collections/" \
                                             "6181093873901234/"

        def test_instantiate_api_class_electronic_portfolios(self):
            current_api = almapipo.instantiate_api_class(
                "6181093873901234,6281093873901234,5381093873901234",
                "electronic",
                "portfolios"
            )
            assert isinstance(current_api, rest_electronic.PortfoliosApi) \
                and current_api.base_path == "/electronic/e-collections/" \
                                             "6181093873901234/e-services/" \
                                             "6281093873901234/"

        def test_instantiate_api_class_electronic_nonexistent(self):
            with pytest.raises(NotImplementedError):
                almapipo.instantiate_api_class(
                    "6181093873901234", "electronic", "nonexistent"
                )

    class TestInstantiateApiClassUsers:

        def test_instantiate_api_class_users_users(self):
            current_api = almapipo.instantiate_api_class(
                "test1234", "users", "users"
            )
            assert isinstance(current_api, rest_users.UsersApi) and \
                current_api.base_path == "/users/"

        def test_instantiate_api_class_users_nonexistent(self):
            with pytest.raises(NotImplementedError):
                almapipo.instantiate_api_class(
                    "test1234", "users", "nonexistent"
                )
