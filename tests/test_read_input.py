"""Tests for read_input"""

import pytest

import read_input

set_of_alma_ids = {'9981093873903332', '22447985240003332', '23447985190003332', '61363367390003332', '62363367380003332', '53375846240003332', '81445078000003332'}

def test_does_list_contain_alma_ids_only():
   read_input.does_list_contain_alma_ids_only(set_of_alma_ids)
