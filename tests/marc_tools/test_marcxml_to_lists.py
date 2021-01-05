"""
Tests for marc_tools.marcxml_to_lists
"""

from xml.etree.ElementTree import fromstring

from marc_tools import marcxml_to_lists


class TestExtractAll:
    marcxml_bib_string_1 = """
        <record>
            <leader>0101nam a2200373 c 4500</leader>
            <controlfield tag="001">1234567890</controlfield>
            <controlfield tag="007">tu</controlfield>
            <controlfield tag="009">prefix01234567</controlfield>
            <datafield tag="015" ind1=" " ind2=" ">
                <subfield code="a">ABCD</subfield>
                <subfield code="2">abcd</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">012345</subfield>
            </datafield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="a">(AB-ABC)prefix01234567</subfield>
            </datafield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="a">prefix012345</subfield>
            </datafield>
            <datafield tag="100" ind1="1" ind2=" ">
                <subfield code="a">Muster, Sasha</subfield>
                <subfield code="d">2000-</subfield>
                <subfield code="0">(AB-000)2345678</subfield>
                <subfield code="4">aut</subfield>
            </datafield>
            <datafield tag="245" ind1="1" ind2="0">
                <subfield code="a">Test title</subfield>
                <subfield code="b">Test subtitle</subfield>
                <subfield code="c">Sasha Muster</subfield>
            </datafield>
            <datafield tag="689" ind1="0" ind2="4">
                <subfield code="a">Test category 1</subfield>
                <subfield code="g">Category qualifier</subfield>
                <subfield code="D">s</subfield>
                <subfield code="0">(AB-000)7890</subfield>
            </datafield>
            <datafield tag="689" ind1="0" ind2="5">
                <subfield code="a">Test category 2</subfield>
                <subfield code="A">z</subfield>
            </datafield>
        </record>
    """
    marcxml_bib_string_2 = """
        <record>
            <controlfield tag="001">0131nam a2200373 c 4500</controlfield>
            <controlfield tag="007">tu</controlfield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="a">prefix56790</subfield>
            </datafield>
            <datafield tag="040" ind1=" " ind2=" ">
                <subfield code="a">BCD</subfield>
                <subfield code="b">esp</subfield>
                <subfield code="e">testfmt</subfield>
            </datafield>
        </record>
    """
    marcxml_bib_element_1 = fromstring(marcxml_bib_string_1)
    marcxml_bib_element_2 = fromstring(marcxml_bib_string_2)

    all_keys_bib_1 = marcxml_to_lists.extract_keys_for_single_record(marcxml_bib_element_1)
    all_keys_bib_2 = marcxml_to_lists.extract_keys_for_single_record(marcxml_bib_element_2)
    all_keys_bib_both = marcxml_to_lists.extract_keys_for_records(
        [marcxml_bib_element_1, marcxml_bib_element_2]
    )
    all_keys_bib_both_sorted = marcxml_to_lists.extract_all_keys_sorted(
        [marcxml_bib_element_1, marcxml_bib_element_2]
    )
    values_leader_and_001_bib_1 = marcxml_to_lists.extract_values_as_lists(
        [marcxml_bib_element_1], ['leader', '001']
    )
    values_035_bib_1 = marcxml_to_lists.extract_values_as_lists(
        [marcxml_bib_element_1], ['035  ', '035  ']
    )
    values_040_bib_1 = marcxml_to_lists.extract_values_as_lists(
        [marcxml_bib_element_1], ['040  ']
    )

    def test_bib_1_extracted_keys(self):
        assert list(self.all_keys_bib_1) == [
                'leader', '001', '007', '009', '015  ', '020  ', '035  ', '035  ', '1001 ', '24510', '68904', '68905'
            ]

    def test_bib_2_extracted_keys(self):
        assert list(self.all_keys_bib_2) == [
            '001', '007', '035  ', '040  '
        ]

    def test_bib_both_extracted_keys(self):
        assert self.all_keys_bib_both == [
            'leader', '001', '007', '009', '015  ', '020  ', '035  ', '035  ', '1001 ', '24510', '68904', '68905',
            '040  '
        ]

    def test_extract_keys_and_sort(self):
        assert self.all_keys_bib_both_sorted == [
            'leader', '001', '007', '009', '015  ', '020  ', '035  ', '035  ', '040  ', '1001 ', '24510', '68904',
            '68905'
        ]

    def test_extract_values_leader_and_001(self):
        assert list(self.values_leader_and_001_bib_1) == [['0101nam a2200373 c 4500', '1234567890']]

    def test_extract_repated(self):
        assert list(self.values_035_bib_1) == [['$$a(AB-ABC)prefix01234567', '$$aprefix012345']]

    def test_empty_if_not_given(self):
        assert list(self.values_040_bib_1) == [['']]
