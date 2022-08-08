#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""User intent manager."""

from abc import ABC

from .text import *
from .rules import *
from .command import *

class Intent(ABC):
  """User intent base class."""
  
  def __init__(self, label: str=None, desc: str=None,
               rules: str=None, commands: List[Command]=[]):
    """Initialize intent.

    Args:
      label -- Label to be given to this intent.
      desc -- Description of this intent.
      rules -- Rita DSL rules to be used to match this intent.
      commands -- List of commands to be executed.
    """
    self.label = label
    self.desc = desc
    self.commands = commands
    r = Rules()
    r.add(rules)

  def generate(self) -> str:
    """Generate intent.
    
    Returns:
      FWUnify compatible intent string.
    """
    s = '\n\ndefine intent {}:\n'.format(self.label)
    for c in self.commands:
      s += c.generate()
    return s.lower()

  def question(self) -> str:
    """Generate question.
    
    Returns:
      Intent question string.
    """
    msg = 'Great. So, let me help you with {}. '.format(self.label)
    msg += "Let me ask you some questions..."
    return msg

class ACL(Intent):
  """ACL derived intent."""

  def __init__(self):
    super().__init__(
      label='ACL',
      desc='Access Control List',
      rules='''
        acl = {"filter", "block", "manage"}
        {WORD("want")?, WORD("access"), IN_LIST(acl)}->MARK("ACL")
      '''.strip(),
      commands=[Name(), From(), To(), Block(), Order()])

class TrafficShaping(Intent):
  """Traffic Shaping derived intent."""

  def __init__(self):
    super().__init__(
      label='TS',
      desc='Traffic Shaping',
      rules='''
        ts = {"shape", "limit", "reduce", "cap"}
        {WORD("want")?, WORD("traffic"), IN_LIST(ts)}->MARK("TS")
      '''.strip(),
      commands=[Name(), From(), To(), Order(), For(), With()])
