#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Telegram interface."""

import sys
from telegram import Update
from telegram.ext import (
  Application,
  ApplicationBuilder,
  CallbackContext,
  CommandHandler,
  ContextTypes,
  ExtBot,
  filters,
  MessageHandler,
)

from .interface import *

class TelegramContext(CallbackContext[ExtBot, UserData, dict, dict], Context):
  """Custom class for context."""

  def __init__(self, application: Application, chat_id: int=None, user_id: int=None):
    super().__init__(application=application, chat_id=chat_id, user_id=user_id)
    self._chat_id = chat_id
    self._user_id = user_id

  async def say(self, message: str) -> None:
    """Say something to the user.
    See `Context.say` for more details."""
    await self.bot.send_message(chat_id=self._chat_id, text=message)

  async def process(self, text: str) -> None:
    """Process user's text.
    See `Context.process` for more details."""
    await super().process(text, self.user_data)

  async def skip(self) -> None:
    """Skip user's current state.
    See `Context.skip` for more details."""
    await super().skip(self.user_data)

async def handler(update: Update, context: TelegramContext) -> None:
  """Handle all non-command messages."""
  await context.process(update.message.text.lower())

async def start(update: Update, context: TelegramContext) -> None:
  """Start the bot."""
  await context.bot.send_message(chat_id=update.effective_chat.id, text='''
    Welcome to the FWNL chat bot!\n
    Please, say what you want to do, or '/help' to see the commands list.
  '''.strip())

async def help(update: Update, context: TelegramContext) -> None:
  """Help command."""
  msg = 'These are the available commands:\n' 
  msg += '/help - show the command list\n'
  for intent in context.user_data.intents:
    msg += '/{} - create {}\n'.format(intent.label.lower(), intent.desc)
  await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

async def cancel(_: Update, context: TelegramContext) -> None:
  """Cancel the current intent."""
  context.user_data.clear()

async def commands(update: Update, context: TelegramContext) -> None:
  """Handle all intent commands."""
  for intent in context.user_data.intents:
    if update.message.text == '/{}'.format(intent.label.lower()):
      await context.process(intent.desc)

async def skip(_: Update, context: TelegramContext) -> None:
  """Skip the current state."""
  await context.skip()

class TelegramInterface(Interface):
  """Telegram interface."""

  def __init__(self):
    super().__init__('Telegram')
    context_types = ContextTypes(context=TelegramContext, user_data=UserData)

    try:
      self.app = ApplicationBuilder().token(self.args.token).context_types(context_types).build()
    except AttributeError:
      logging.error('No token provided. Exiting.')
      sys.exit(1)

    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handler)
    self.app.add_handler(msg_handler)
    self.app.add_handler(CommandHandler('start', start))
    self.app.add_handler(CommandHandler('help', help))
    self.app.add_handler(CommandHandler('cancel', cancel))
    self.app.add_handler(CommandHandler('skip', skip))
    
    temp_data = UserData()
    for intent in temp_data.intents:
      self.app.add_handler(CommandHandler(intent.label.lower(), commands))

  def start(self) -> None:
    """Start the interface."""
    self.app.run_polling()

def main():
  """Main function."""
  interface = TelegramInterface()
  interface.start()

if __name__ == '__main__':
  main()
