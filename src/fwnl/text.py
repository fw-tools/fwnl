#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Text processing."""

from typing import List

from .distance import *
from .rules import *

class Text(object):
  """Text processing class."""

  def __init__(self, text: str):
    """Initialize text.
    
    Args:
      text -- Text string to be processed.
    """
    rules = Rules()
    self.doc = rules.nlp(text.lower())
    processed = ""
    for token in self.doc:
      if (token.text in rules.nlp.Defaults.stop_words or
          token.is_punct or
          token.lemma_ == '-PRON-'):
        continue
      processed += ' ' + token.lemma_
    self.docp = rules.nlp(processed)

  def similarity(self, compare: 'Text') -> float:
    """Find similarity between two texts.
    
    Args:
      compare -- Text object to compare with.
    
    Returns:
      Similarity score between 0 and 1.
    """
    return self.doc.similarity(compare.doc)

  def match(self, compare: List[str], margin: int=1) -> int:
    """Calculate mathing score from given list.
    
    Args:
      compare -- List of strings to compare with.
      margin -- Maximum edit distance for comparison. (default: 1)
    
    Returns:
      Number of matched keywords.
    """
    score = 0
    for token in self.docp:
      for key in compare:
        if distance(key, token.text, dl=True) <= margin:
          score += 1
          compare.remove(key)
          break
    return score
