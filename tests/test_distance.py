#!/usr/bin/env python3
# MIT License
# Copyright (c) 2019-2022 Augusto Goulart

from fwnl.distance import *

class TestDistance(object):
  # strings exclusion cases
  def test_strings_exclusion(self):
    assert exclusion('top', 'toc') == ('p', 'c')
    assert exclusion('pop', 'pop') == ('', '')
    assert exclusion('nock', 'lock') == ('nock', 'lock')
    assert exclusion('café', 'cappuccino') == ('fé', 'ppuccino')

  # strings distance cases
  def test_strings_distance(self):
    assert distance('kitten', 'sitten') == 1
    assert distance('sittin', 'sitten') == 1
    assert distance('sittin', 'sitting') == 1
    assert distance('back', 'look') == 3
    assert distance('café', 'coffee') == 3
    assert distance('fries are made of potatos', 'potatos are made of fries') == 12
    assert distance('take the blue pill', 'take the red pill') == 4
    assert distance('slava', 'слава') == 0, 'unicode must have been converted to ascii!'
    assert distance('deg', '°', ascii_only=False) == 3, 'conversion to ascii must not occur!'
    assert distance('pÓPé', 'PópÉ') == 0, 'upper case letter must have been converted to lower case!'
    assert distance('pÓPé', 'PópÉ', case=True) == 4, 'conversion to lower case must not occur!'
    assert distance('smtih', 'smith', dl=True) == 1
    assert distance('snapple', 'apple', dl=True) == 2
    assert distance('testing', 'testtn', dl=True) == 2
    assert distance('typing', 'cycling', dl=True) == 3
    assert distance('hoover', 'verhoo', dl=True) == 6
    assert distance('the moon is made out of cheese', 'the cheese is made out of moon', dl=True) == 12
    assert distance('turn the tv on', 'turn on the tv', dl=True) == 6
    assert distance('opunsosu', 'オープンソース', dl=True) == 0, 'unicode must have been converted to ascii!'
    assert distance('opunsosu', 'オープンソース', dl=True, ascii_only=False) == 8, 'conversion to ascii must not occur!'
    assert distance('saturday', 'sunday', dl=True) == 3, 'upper case letter must have been converted to lower case!'
    assert distance('Saturday', 'saturday', dl=True, case=True) == 1, 'conversion to lower case must not occur!'
