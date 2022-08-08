#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Base interface."""

import argparse
from collections import defaultdict
from json import JSONEncoder
import logging
import os
from threading import Lock
from typing import Any, DefaultDict, Dict
 
from .singleton import *
from fwnl.text import *
from fwnl.values import *
from fwnl.intent import *

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d_%H:%M:%S'

class Interface(object, metaclass=SingletonABCMeta):
  """Base class for all interfaces."""

  def __init__(self, nickname: str=None):
    """Initialize the interface.
    
    Args:
      nickname -- Nickname of the interface.
    """
    self.nickname = 'FwBot'
    if nickname is not None:
      self.nickname += ' ' + nickname

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='file with all configurations')
    help_msg = "verbosity logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
    parser.add_argument("--verbosity", "-v", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)
    parser.add_argument('-t', '--token', help='token for interface', default=os.environ.get('FWNL_TOKEN'))
    self.args, unknown = parser.parse_known_args()

    if self.args.verbosity == logging.DEBUG:
      logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                          datefmt=TIME_FORMAT, level=self.args.verbosity)
    else:
      logging.basicConfig(format='%(message)s',
                          datefmt=TIME_FORMAT, level=self.args.verbosity)
    logging.info("Bot %s interface has initialized!", self.nickname)

class UserDataEncoder(JSONEncoder):
  """Custom JSON encoder for UserData class."""
  def default(self, obj: Any) -> Any:
    """Default method for encoding."""
    return {k: v for k, v in obj.__dict__.items() if not (
      'lock' in k or 'rules' in k or 'intents' in k)}

class UserDataDecoder(object):
  """Custom JSON decoder for UserData class."""
  def default(d: Dict[str, Any]) -> Any:
    """Default method for decoding."""
    #decode intents
    if d.get('name') is None:
      if d.get('label') is not None:
        intent = Intent()
        if d['label'] == 'ACL':
          intent = ACL()
        elif d['label'] == 'TS':
          intent = TrafficShaping()
        intent.commands = d['commands']
        return intent
      else:
        if d.get('_data') is not None:
          ud = UserData()
          ud.state = d['_data'].get('0')
          ud.intent = d['_data'].get('1')
          ud.command = d['_data'].get('2')
          ud.counter = d['_data'].get('3')
          return ud
        else:
          return d

    # decode values
    if d.get('special') is not None:
      if d['special'] == 'Confirm':
        return Confirm(value=d['value'])

    if d['name'] == 'Text':
      return Raw(value=d['value'])
    if d['name'] == 'Endpoint':
      return Endpoint(value=d['value'])
    if d['name'] == 'Range':
      return Range(value=d['value'])
    if d['name'] == 'Protocol':
      return Protocol(value=d['value'])
    if d['name'] == 'Throughput':
      return Throughput(value=d['value'])
    if d['name'] == 'Before':
      return Before(value=d['value'])
    if d['name'] == 'After':
      return After(value=d['value'])

    # decode commands
    cmd = Command()
    if d['name'] == 'Name':
      cmd = Name()
    elif d['name'] == 'From':
      cmd = From()
    elif d['name'] == 'To':
      cmd = To()
    elif d['name'] == 'Block':
      cmd = Block()
    elif d['name'] == 'Order':
      cmd = Order()
    elif d['name'] == 'With':
      cmd = With()
    elif d['name'] == 'For':
      cmd = For()
    cmd.value = d['value']
    cmd.values = d['values']
    return cmd

class UserData(object):
  """User data for interface."""

  def __init__(self):
    """Initialize the user data."""
    self._lock: RLock = RLock()
    self._data: DefaultDict[int, Any] = defaultdict(int)

    self._rules = Rules()
    self._intents = [ACL(), TrafficShaping()]
    self._rules.setup()

  def __getitem__(self, key: int) -> Any:
    """Get user data item.
    
    Args:
      key -- Key number of the item.
      
    Returns:
      User data item.
    """
    with self._lock:
      return self._data.get(key, None)
  
  def __setitem__(self, key: int, value: Any) -> None:
    """Set user data item.
    
    Args:
      key -- Key number of the item.
      value -- New value for the item.
    """
    with self._lock:
      self._data[key] = value

  def __delitem__(self, key: int) -> None:
    """Delete user data item.
    
    Args:
      key -- Key number of the item.
    """
    with self._lock:
      del self._data[key]
  
  @property
  def state(self) -> str:
    """Get the current state of the user."""
    return self[0]

  @state.setter
  def state(self, value: str) -> None:
    """Set the current state of the user."""
    self[0] = value

  @state.deleter
  def state(self) -> None:
    """Delete the current state of the user."""
    del self[0]

  @property
  def intents(self) -> List[Intent]:
    """Get all available intents."""
    with self._lock:
      return self._intents
  
  @property
  def intent(self) -> Intent:
    """Get the current intent of the user."""
    return self[1]

  @intent.setter
  def intent(self, value: Intent) -> None:
    """Set the current intent of the user."""
    self[1] = value
  
  @intent.deleter
  def intent(self) -> None:
    """Delete the current intent of the user."""
    del self[1]

  @property
  def command(self) -> str:
    """Get the current command of the user."""
    return self[2]
  
  @command.setter
  def command(self, value: str) -> None:
    """Set the current command of the user."""
    self[2] = value

  @command.deleter
  def command(self) -> None:
    """Delete the current command of the user."""
    del self[2]

  @property
  def counter(self) -> int:
    """Get the current counter of the user."""
    return self[3]
  
  @counter.setter
  def counter(self, value: int) -> None:
    """Set the current counter of the user."""
    self[3] = value
  
  @counter.deleter
  def counter(self) -> None:
    """Delete the current counter of the user."""
    del self[3]
  
  def closest(self, text: str) -> Tuple[Intent, float]:
    """Get the closest intent.
    
    Args:
      text -- Text to be analyzed.
    
    Returns:
      The closest intent and its score.
    """
    text = Text(text)
    closest = None
    closest_sim = -1
    for intent in self.intents:
      kw = self._rules.patterns[intent.label]
      similarity = text.similarity(Text(intent.desc)) + text.match(kw)
      for ent in text.docp.ents:
        if ent.label_ == intent.label:
          similarity += 1
      if similarity > closest_sim:
        closest = intent
        closest_sim = similarity
    return closest, closest_sim
  
  def clear(self) -> None:
    """Clear the user data."""
    del self.state
    del self.intent
    del self.command
    del self.counter

class Context(object, metaclass=ABCMeta):
  """Context model for each user instance."""

  @abstractmethod
  async def say(self, text: str) -> None:
    """Send a message to the user.
    
    Args:
      text -- Text to be sent.
    """
    pass

  @abstractmethod
  async def process(self, text: str, user_data: UserData) -> None:
    """Process user's text.
    
    Args:
      text -- Text to be processed.
      user_data -- User data class with current states.
    """
    if user_data.state is None:
      user_data.intent, _ = user_data.closest(text)
      user_data.command = Confirm(user_data.intent.label, user_data.intent.desc)
      await self.say(user_data.command.question())
      user_data.state = 'confirm_intent'
      return
    if user_data.state == 'confirm_intent':
      if user_data.command.verify(text):
        await self.say(user_data.intent.question())
        user_data.state = 'questions'
        user_data.counter = 0
        user_data.command = user_data.intent.commands[user_data.counter]
        await self.say(user_data.command.question())
      else:
        await self.say("Ok, we will not do that.")
        user_data.state = None
      return
    if user_data.state == 'questions':
      success, msg = user_data.command.verify(text)
      await self.say(msg)
      if success:
        user_data.state = 'next_command'
        user_data.intent.commands[user_data.counter] = user_data.command
      else:
        return
    if user_data.state == 'next_command':
      user_data.counter += 1
      if user_data.counter < len(user_data.intent.commands):
        user_data.command = user_data.intent.commands[user_data.counter]
        await self.say(user_data.command.question())
        user_data.state = 'questions'
      else:
        await self.say("Here's your final configuration:")
        await self.say(user_data.intent.generate())
        user_data.state = None
  
  @abstractmethod
  async def skip(self, user_data: UserData) -> None:
    """Skip user's current state.
    
    Args:
      user_data -- User data class with current states.
    """
    if user_data.state == 'questions':
      if user_data.command.default():
        user_data.state = 'next_command'
        await self.process('') # NOTE: calling derived class method
      else:
        await self.say("You can't skip this question.")
