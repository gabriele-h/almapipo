"""Tests for alma_rest.alma_rest"""

import pytest

from alma_rest import alma_rest, rest_bibs, rest_electronic, rest_users


class TestInstantiateApiClass:

    def test_instantiate_api_class_faulty(self):
        with pytest.raises(NotImplementedError):
            alma_rest.instantiate_api_class('somestring', 'faulty', 'bibs')

    class TestInstantiateApiClassBibs:

        def test_instantiate_api_class_bibs_bibs(self):
            CurrentApi = alma_rest.instantiate_api_class('9981093873901234', 'bibs', 'bibs')
            assert isinstance(CurrentApi, rest_bibs.BibsApi) and \
                CurrentApi.base_path == "/bibs/"

        def test_instantiate_api_class_bibs_hols(self):
            CurrentApi = alma_rest.instantiate_api_class('9981093873901234,22447985240001234', 'bibs', 'holdings')
            assert isinstance(CurrentApi, rest_bibs.HoldingsApi) and \
                CurrentApi.base_path == "/bibs/9981093873901234/holdings/"

        def test_instantiate_api_class_bibs_items(self):
            CurrentApi = alma_rest.instantiate_api_class(
                '9981093873901234,22447985240001234,23447985190001234',
                'bibs',
                'items'
            )
            assert isinstance(CurrentApi, rest_bibs.ItemsApi) and \
                CurrentApi.base_path == "/bibs/9981093873901234/holdings/22447985240001234/items/"

        def test_instantiate_api_class_bibs_portfolios(self):
            CurrentApi = alma_rest.instantiate_api_class('9981093873901234', 'bibs', 'portfolios')
            assert isinstance(CurrentApi, rest_bibs.PortfoliosApi) and \
                CurrentApi.base_path == "/bibs/9981093873901234/portfolios/"

        def test_instantiate_api_class_bibs_faulty(self):
            with pytest.raises(NotImplementedError):
                alma_rest.instantiate_api_class('9981093873901234', 'bibs', 'faulty')

    class TestInstantiateApiClassElectronic:

        def test_instantiate_api_class_electronic_ecollections(self):
            CurrentApi = alma_rest.instantiate_api_class('6181093873901234', 'electronic', 'e-collections')
            assert isinstance(CurrentApi, rest_electronic.EcollectionsApi) and \
                CurrentApi.base_path == "/electronic/e-collections/"

        def test_instantiate_api_class_electronic_eservices(self):
            CurrentApi = alma_rest.instantiate_api_class('6181093873901234,6281093873901234', 'electronic', 'e-services')
            assert isinstance(CurrentApi, rest_electronic.EservicesApi) and \
                   CurrentApi.base_path == "/electronic/e-collections/6181093873901234/"

        def test_instantiate_api_class_electronic_portfolios(self):
            CurrentApi = alma_rest.instantiate_api_class(
                '6181093873901234,6281093873901234,5381093873901234',
                'electronic',
                'portfolios'
            )
            assert isinstance(CurrentApi, rest_electronic.PortfoliosApi) and \
                   CurrentApi.base_path == "/electronic/e-collections/6181093873901234/e-services/6281093873901234/"

        def test_instantiate_api_class_electronic_faulty(self):
            with pytest.raises(NotImplementedError):
                alma_rest.instantiate_api_class('6181093873901234', 'electronic', 'faulty')

    class TestInstantiateApiClassUsers:

        def test_instantiate_api_class_users_users(self):
            CurrentApi = alma_rest.instantiate_api_class('test1234', 'users', 'users')
            assert isinstance (CurrentApi, rest_users.UsersApi) and \
                CurrentApi.base_path == "/users/"

        def test_instantiate_api_class_users_faulty(self):
            with pytest.raises(NotImplementedError):
                alma_rest.instantiate_api_class('test1234', 'users', 'faulty')
