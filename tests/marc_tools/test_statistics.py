"""
Tests for marc_helpers.statistics
"""

from marc_tools import statistics


class TestCountForTagAndInds:

    first_record = {
        'leader': '00000nam#a2200000#c#4500',
        '001': ['990060201234'],
        '020  ': [{'a': ['5776']}],
        '650 4': [{'a': ['Frans'], 'g': ['gtt']},
                  {'a': ['Fulani (taal)'], 'g': ['gtt']}],
        '650 0': [{'a': ['Agriculture'], 'v': ['Dictionaries'], 'x': ['Fula']},
                  {'a': ['Country life'], 'z': ['Cameroon'], 'v': ['Dictionaries'], 'x': ['Fula']},
                  {'a': ['French language'], 'v': ['Dictionaries'], 'x': ['Fula']},
                  {'a': ['Fula language'], 'v': ['Dictionaries'], 'x': ['French']},
                  {'a': ['Fula language'], 'z': ['Cameroon'], 'v': ['Dictionaries']},
                  {'a': ['Nature'], 'v': ['Dictionaries'], 'x': ['Fula']}],
    }

    second_record = {
        'leader': '04299cam a22003852c 4500',
        '001': ['9927701234'],
        '020  ': [{'a': ['9804784'], 'q': ['(electronic book)']},
                  {'z': ['9804771']}],
        '035  ': [{'a': ['  2018033239'], '6': ['ORIG']},
                  {'a': ['(DLC)BRILL005960 ']}],
    }

    record_list = [first_record, second_record]

    def test_statistics_with_single_record(self):
        assert statistics.count_for_tag_and_inds([self.first_record], ['001']) == {'001': 1}
        assert statistics.count_for_tag_and_inds([self.first_record], ['650 0']) == {'650 0': 6}
        assert statistics.count_for_tag_and_inds([self.first_record], ['650 4']) == {'650 4': 2}
        assert statistics.count_for_tag_and_inds([self.second_record], ['035  ']) == {'035  ': 2}
        assert statistics.count_for_tag_and_inds([self.first_record], ['020  ']) == {'020  ': 1}
        assert statistics.count_for_tag_and_inds([self.second_record], ['020  ']) == {'020  ': 2}

    def test_statistics_with_record_list(self):
        assert statistics.count_for_tag_and_inds(self.record_list, ['001']) == {'001': 1}
        assert statistics.count_for_tag_and_inds(self.record_list, ['035  ']) == {'035  ': 2}
        assert statistics.count_for_tag_and_inds(self.record_list, ['020  ']) == {'020  ': 2}
