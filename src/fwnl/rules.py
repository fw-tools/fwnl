#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Rule-based matching."""

import spacy
from spacy.matcher import Matcher
from rita.shortcuts import setup_spacy

import logging
from typing import List

from interfaces.singleton import *

IDENT_CHAR = '\t'
IDENT_LEVEL = 2

class Rules(object, metaclass=SingletonMeta):
  """Class to load Rita DSL rules and add them to spaCy pipeline."""
  rules = ''
  loaded = False

  def add(self, rules: str=None) -> None:
    """Add rules to pipeline.

    Args:
      rules -- Rule string to be added to spaCy pipeline.
    """
    if rules is not None:
      self.rules += rules
  
  def setup(self) -> None:
    """Setup matcher with patterns."""
    if not self.loaded:
      self.loaded = True
      self.nlp = spacy.load('en_core_web_md')
      setup_spacy(self.nlp, rules_string=self.rules)
      self.matcher = Matcher(self.nlp.vocab)
      self.ruler = self.nlp.pipeline[-1]
      self.patterns = dict([])
      for label in self.ruler[1].labels:
        self.patterns[label] = self.__keywords(label)

  def __keywords(self, label: str) -> List[str]:
    """Parse list of keywords for given label.

    Args:
      label -- Label string to search patters from.

    Returns:
      List of all keywords found in given label.
    """
    kw = []
    for l, patterns in self.ruler[1].token_patterns.items():
      if l == label.upper():
        for ls in patterns:
          for d in ls:
            if type(d.get('LOWER')) is str:
              kw.append(d.get('LOWER'))
            elif type(d.get('LOWER')) is dict:
              if d.get('LOWER').get('IN') is not None:
                kw.extend(d.get('LOWER').get('IN'))
        break
    return kw
