#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2019-2022 Augusto Goulart

"""Strings edit distance."""

import unidecode as ud
from typing import Tuple

def exclusion(a: str, b: str) -> Tuple[str, str]:
  """Exclusion operation on two strings initial letters.
  
  Args:
    a -- First string.
    b -- Second string.
  
  Returns:
    Tuple of (str, str) with both remaining slices from operation result.
  """
  if a == b: return ("", "")
  for count in range(min(len(a), len(b))):
    if not a[count] == b[count]: break
  return (a[count:], b[count:])

def distance(source: str, target: str,
             dl: bool=False, ascii_only: bool=True,
             case: bool=False) -> int:
  """Calculate the distance between two strings.
  
  Args:
    source -- Source string.
    target -- Target string.
    dl -- Use damerau-levenshtein instead of levenshtein? (default: False)
    ascii_only -- Convert non-ascii characters to ascii? (default: True)
    case -- Case comparison? (default: False)
  
  Returns:
    The distance between source and target.
  """
  if ascii_only:
    source = ud.unidecode(source)
    target = ud.unidecode(target)
  if not case:
    source = source.casefold()
    target = target.casefold()
    
  source, target = exclusion(source, target)
  n, m = len(source), len(target)

  if n == 0: return m
  if m == 0: return n
  if n < m:
    source, target = target, source
    n, m = m, n

  one_ago = range(m + 1)
  two_ago = [0] * (m + 1) if dl else [None]

  for i in range(n):
    curr_row = [i + 1]
    for j in range(m):
      if source[i] == target[j]:
        if dl and i and j and source[i] == target[j - 1] and source[i - 1] == target[j]:
          curr_row.append(min(one_ago[j], two_ago[j - 1]))
        else:
          curr_row.append(one_ago[j])
      else:
        if dl and i and j and source[i] == target[j - 1] and source[i - 1] == target[j]:
          curr_row.append(1 + min(one_ago[j], one_ago[j + 1], curr_row[-1], two_ago[j - 1]))
        else:
          curr_row.append(1 + min(one_ago[j], one_ago[j + 1], curr_row[-1]))
    two_ago = one_ago if dl else [None]
    one_ago = curr_row

  return one_ago[-1]
