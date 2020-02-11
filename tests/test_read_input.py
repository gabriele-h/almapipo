"""Tests for read_input"""

import pytest

import read_input


class TestDoesListContainAlmaIdsOnly:
   set_of_alma_ids = {
      '9981093873903332', '22447985240003332', '23447985190003332',
      '61363367390003332', '62363367380003332', '53375846240003332',
      '81445078000003332'
   }
   set_of_alma_ids_containing_other = {
      '9981093873903332', '22447985240003332', '23447985190003332',
      '61363367390003332', '62363367380003332', '53375846240003332',
      '81445078000003332', '813332'
   }
   set_empty = {}

   def test_alma_ids_only(self):
      bool = read_input.does_list_contain_alma_ids_only(self.set_of_alma_ids)
      assert bool == True
   
   def test_containing_other(self):
      bool = read_input.does_list_contain_alma_ids_only(self.set_of_alma_ids_containing_other)
      assert bool == False
   
   def test_empty(self):
      bool = read_input.does_list_contain_alma_ids_only(self.set_empty)
      assert bool == False
