"""Tests for read_input"""

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

   def test_alma_ids_only(self):
      bool = all(input_read.is_this_an_alma_id(id) for id in self.set_of_alma_ids)
      assert bool == True
   
   def test_containing_other(self):
      bool = input_read.is_this_an_alma_id(self.not_an_alma_id)
      assert bool == False
   
   def test_empty(self):
      bool = input_read.is_this_an_alma_id(self.string_empty)
      assert bool == False

   def test_number_not_string(self):
      bool = input_read.is_this_an_alma_id(self.not_a_string)
      assert bool == False

   def test_set_not_string_either(self):
      bool = input_read.is_this_an_alma_id(self.set_of_alma_ids)
