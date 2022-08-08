#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Models for values"""

from abc import ABC, abstractmethod
from typing import Any

from .rules import *
 
class Value(ABC):
  """Value base class."""

  def __init__(self, name: str=None, desc: str=None,
               value: Any=None, hint: str=None):
    """Initialize value.

    Args:
      name -- Name of the value.
      desc -- Description of the value.
      value -- Value to be set.
      hint -- Hint to be given to the user.
    """
    self.name = name
    self.desc = desc
    self.value = value
    self.hint = hint
    self.patterns: List[str] = []

  @abstractmethod
  def generate(self) -> str:
    """Generate value.
    
    Returns:
      FWUnify compatible value string.
    """
    return self.value

  @abstractmethod
  def setup(self) -> None:
    """Setup value."""
    pass
    
  def question(self) -> str:
    """Generate question.
    
    Returns:
      Value question string.
    """
    return "What's the value for {} (hint: {}).".format(self.name, self.hint)
    
  def verify(self, answer: str=None) -> bool:
    """Verify answer.
    
    Args:
      answer -- Answer to be verified.
    
    Returns:
      True if answer is valid, False otherwise.
    """
    self.setup()
    rules = Rules()
    doc = rules.nlp(answer)
    matches = rules.matcher(doc)
    for id, start, end in matches:
      if rules.nlp.vocab.strings[id] in self.patterns:
        self.value = doc[start:end].text
        return True
    return False

class Endpoint(Value):
  """Endpoint derived value."""
  loaded = False

  def __init__(self, name: str='Endpoint',
               desc: str='Value of address property.', value: str=None):
    super().__init__(name, desc, value,
                     'IPv4|IPV6|laboratory|server|professor|secretary|classroom')
    self.patterns = ['IPV4', 'IPV6', 'HOSTNAME']

  def setup(self) -> None:
    """Setup address endpoint matching patterns."""
    if not Endpoint.loaded:
      Endpoint.loaded = True
      rules = Rules()

      octet_rx = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
      pattern = [{"TEXT": {"REGEX": r"^{0}(?:\.{0}){{3}}$".format(octet_rx)}}]
      rules.matcher.add('IPV4', [pattern])

      # TODO: review IPV6 pattern
      octet_rx = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
      pattern = [{"TEXT": {"REGEX": r"^{0}(?:\.{0}){{3}}$".format(octet_rx)}}]
      rules.matcher.add('IPV6', [pattern])

      pattern = [{"TEXT": {"REGEX": r"^(all|laboratory|server|professor|secretary|classroom)$"}}]
      rules.matcher.add('HOSTNAME', [pattern])

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "endpoint('{}')".format(self.value)

class Range(Value):
  """Range derived value."""
  loaded = False

  def __init__(self, name: str='Range',
               desc: str='Value of address property.', value: str=None):
    super().__init__(name, desc, value, 'IP range (v4 or v6)')
    self.patterns = ['IPV4_RANGE', 'IPV6_RANGE']

  def setup(self) -> None:
    """Setup address range matching patterns."""
    if not Range.loaded:
      Range.loaded = True
      rules = Rules()

      # TODO: add IPv6 range
      octet_rx = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
      # TODO: test IPv4 range
      pattern = [{"TEXT": {"REGEX": r"^{0}(?:\.{0}){{3}}\/([1-9]|[12][0-9]|3[01])$".format(octet_rx)}}]
      rules.matcher.add('IPV4_RANGE', [pattern])
 
  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "range('{}')".format(self.value)

class Protocol(Value):
  """Protocol derived value."""
  loaded = False

  def __init__(self, name: str='Protocol',
               desc: str='Value of Protocol property.', value: str=None):
    self.protocols = ['http', 'https', 'ftp', 'ssh', 'telnet', 'smtp']
    super().__init__(name, desc, value, '|'.join(self.protocols))
    self.patterns = ['PROTOCOL']

  def setup(self) -> None:
    """Setup protocol matching patterns."""
    if not Protocol.loaded:
      Protocol.loaded = True
      rules = Rules()

      pattern = [{"LOWER": {"IN": self.protocols}}]
      rules.matcher.add('PROTOCOL', [pattern])

  def generate(self) -> str:
    """Generate value string.
    See base class for more details.
    """
    return "traffic('{}')".format(self.value)

class Confirm(Value):
  """Confirm derived value."""
  loaded = False

  def __init__(self, name: str='Confirm',
               desc: str='Value of Confirm property.', value: bool=False):
    super().__init__(name, desc, value=value)
    self.special = 'Confirm'
    self.patterns = ['CONFIRM', 'CANCEL']

  def setup(self) -> None:
    """Setup confirm matching patterns."""
    if not Confirm.loaded:
      Confirm.loaded = True
      rules = Rules()

      pattern = [{"LOWER": {"IN": ["yes", "confirm", "ok", "sure", "yep", "y"]}}]
      rules.matcher.add('CONFIRM', [pattern])

      pattern = [{"LOWER": {"IN": ["no", "cancel", "nope", "n"]}}]
      rules.matcher.add('CANCEL', [pattern])

  def question(self) -> str:
    """Return question.
    See base class for more details.
    """
    return 'Do you want to make {} (i.e., {})?'.format(self.name, self.desc)

  def verify(self, answer: str=None) -> bool:
    """Verify confirm value is valid.
    See base class for more details.
    """
    self.setup()
    rules = Rules()
    doc = rules.nlp(answer)
    matches = rules.matcher(doc)

    self.value = False
    for id, _, _ in matches:
      label = rules.nlp.vocab.strings[id]
      if label in self.patterns:
        if label == 'CONFIRM':
          self.value = True
        elif label == 'CANCEL':
          self.value = False
        break
    return self.value

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return 'Confirmed <{}>'.format(self.value)

class Raw(Value):
  """Raw text derived value."""
  loaded = False

  def __init__(self, name: str='Text',
               desc: str='Value of Text property.', value: str=None):
    super().__init__(name, desc, value)
    self.patterns = ['RAW']

  def setup(self) -> None:
    """Setup text matching patterns."""
    if not Raw.loaded:
      Raw.loaded = True
      rules = Rules()

      pattern = [{"TEXT": {"REGEX": r"([\w\-]+)"}}]
      rules.matcher.add('RAW', [pattern])

  def verify(self, answer: str=None) -> bool:
    """Verify raw value.
    See base class for more details.
    """
    self.setup()
    rules = Rules()
    doc = rules.nlp(answer)
    matches = rules.matcher(doc)

    self.value = ''
    for id, start, end in matches:
      if rules.nlp.vocab.strings[id] in self.patterns:
        self.value += doc[start:end].text
    return True if self.value != '' else False

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "text('{}')".format(self.value)

class Throughput(Value):
  """Throughput derived value."""
  loaded = False

  def __init__(self, name: str='Throughput',
               desc: str='Value of Throughput property.', value: str=None):
    super().__init__(name, desc, value, 'bits per second')
    self.patterns = ['THROUGHPUT']

  def setup(self) -> None:
    """Setup throughput matching patterns."""
    if not Throughput.loaded:
      Throughput.loaded = True
      rules = Rules()

      pattern = [{"TEXT": {"REGEX": r"^([0-9]+[tgmk]?bps)$"}}]
      rules.matcher.add('THROUGHPUT', [pattern])

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "throughput('{}')".format(self.value)

class Before(Value):
  """Before derived value."""
  loaded = False

  def __init__(self, name: str='Before',
               desc: str='Value of Before property.', value: str=None):
    super().__init__(name, desc, value)
    self.patterns = ['BEFORE', 'BEFORE_TARGET']

  def setup(self) -> None:
    """Setup before matching patterns."""
    if not Before.loaded:
      Before.loaded = True
      rules = Rules()

      pattern = [{"LOWER": "before"}]
      rules.matcher.add('BEFORE', [pattern])

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "before('all')"

class After(Value):
  """After derived value."""
  loaded = False

  def __init__(self, name: str='After',
               desc: str='Value of After property.', value: str=None):
    super().__init__(name, desc, value)
    self.patterns = ['AFTER']

  def setup(self) -> None:
    """Setup after matching patterns."""
    if not After.loaded:
      After.loaded = True
      rules = Rules()

      pattern = [{"LOWER": "after"}]
      rules.matcher.add('AFTER', [pattern])

  def generate(self) -> str:
    """Generate value.
    See base class for more details.
    """
    return "after('all')"
