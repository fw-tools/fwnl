#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Models for FWUnify commands."""

from abc import ABC
import tempfile

from .rules import *
from .values import *
from .text import *

class Command(ABC):
  """FWUnify command base class."""
  
  def __init__(self, name: str=None, desc: str=None, values: Tuple[Value]=[]):
    """Initialize command.
    
    Args:
      name -- Name to be given to this command.
      desc -- Description of this command.
      values -- Tuple of possible values.
    """
    self.name = name
    self.desc = desc
    self.values = values
    self.value = 0
    self.hint = None
    for v in self.values:
      if self.hint is None:
        self.hint = v.name
      else:
        self.hint += '|' + v.name
      
  def generate(self) -> str:
    """Generate command.

    Returns:
      FWUnify compatible command string.
    """
    s = '{}{} {}\n'.format(self.name, IDENT_CHAR * IDENT_LEVEL, self.values[self.value].generate())
    return s

  def question(self) -> str:
    """Generate question.
    
    Returns:
      Question string used to ask user for values.
    """
    return ("Regarding the property {}. " + \
      "What do you want to use as its value? Hint: {}").format(self.name, self.hint)

  def verify(self, answer: str=None) -> Tuple[bool, str]:
    """Verify if command accepts this value.
    
    Args:
      answer -- User answer string.
    Returns:
      Tuple of (bool, str) where bool is True if answer
      is accepted and str is the response/reason for the result.
    """
    i = 0
    for value in self.values:
      if value.verify(answer):
        self.value = i
        return [True, 'I got it: {}'.format(self.values[i].generate())]
      i += 1
    return [False, "Sorry, I don't understand."]
  
  def default(self) -> bool:
    """Sets default value.
    
    Returns:
      True if default value was set, False otherwise (default value not available).
    """
    return False
    
class From(Command):
  """From derived command."""

  def __init__(self):
    super().__init__('From', 'Source address/machine', [Endpoint(), Range()])

class To(Command):
  """To derived command."""

  def __init__(self):
    super().__init__('To', 'Destination address/machine', [Endpoint(), Range()])

class Block(Command):
  """Block derived command."""

  def __init__(self):
    super().__init__('Block', 'Traffic protocol', [Protocol()])

class Name(Command):
  """Name derived command."""

  def __init__(self):
    super().__init__('Name', 'Name to be used', [Raw()])

  def default(self) -> bool:
    """Sets default value.
    Default value is a random tempfile name.
    See base class for details.
    """
    self.value = 0
    self.values[0].value = next(tempfile._get_candidate_names())
    return True

class With(Command):
  """With derived command."""

  def __init__(self):
    super().__init__('With', 'Metrics to be used', [Throughput()])

class Order(Command):
  """Order derived command."""

  def __init__(self):
    super().__init__('Order', 'Intent priority', [Before(), After()])

  def default(self) -> bool:
    """Set default value.
    Default value is 'After'.
    See base class for details.
    """
    self.value = 1
    return True

class For(Command):
  """For derived command."""

  def __init__(self):
    super().__init__('For', 'Intended traffic', [Protocol()])
