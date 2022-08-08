#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Terminal interface."""

import asyncio
import datetime
import logging
import sys

from .interface import *

class TerminalContext(Context):
  """Custom class for context."""

  def __init__(self, nickname: str=None, user: str='User'):
    self.nickname = nickname
    self.user = user
    self.user_data = UserData()

  async def say(self, message: str) -> None:
    """Say something to the user.
    See base class for more details."""
    logging.info('{}:{} {}'.format(self.nickname, IDENT_CHAR * IDENT_LEVEL, message))
  
  async def listen(self) -> str:
    """Listen for a message from the user.
    
    Returns:
      The message from the user.
    """
    return input('{}:{} '.format(self.user, IDENT_CHAR * IDENT_LEVEL))

  async def process(self, text: str) -> None:
    """Process user's text.
    See base class for more details."""
    await super().process(text, self.user_data)

  async def skip(self) -> None:
    """Skip user's current state.
    See base class for more details."""
    await super().skip(self.user_data)

class TerminalInterface(Interface):
  """Terminal interface."""

  def __init__(self, nickname: str='Terminal'):
    super().__init__(nickname)
  
  @property
  def greetings(self) -> str:
    """Format greetings message.
    
    Returns:
      The greetings message.
    """
    # time of day
    tod = datetime.datetime.now().hour / 6
    time = 'evening'
    if tod == 1:
      time = 'morning'
    elif tod == 2:
      time= 'afternoon'

    return 'Good {}! '.format(time) + \
          "I'm here to help you in setting up firewalls."
  
  def run(self) -> None:
    """Run the interface."""
    asyncio.run(self.handler())

  async def handler(self) -> None:
    """Handle all possible cases."""
    context = TerminalContext(self.nickname)
    await context.say(self.greetings)

    try:
      while True:
        text = await context.listen()
        await context.process(text)
        # TODO: add cancel command
        # TODO: add skip command
    except KeyboardInterrupt:
      sys.exit()

def main():
  """Main function."""
  i = TerminalInterface()
  i.run()

if __name__ == '__main__':
  main()
