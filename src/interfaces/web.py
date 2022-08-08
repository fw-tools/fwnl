#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Web interface."""

import asyncio
import json
import sys

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, render_template, request, send_from_directory

from .interface import *

class WebContext(Context):
  """Custom class for web context."""

  def __init__(self, nickname: str=None, user_data: UserData=None):
    self.nickname = nickname
    if user_data is None or type(user_data) is not UserData:
      self.user_data = UserData()
    else:
      self.user_data = user_data
    self.responses: List[str] = []

  async def say(self, message: str) -> None:
    """Say something to the user.
    See base class for more details."""
    self.responses.append(message)

  async def process(self, text: str) -> None:
    """Process user's text.
    See base class for more details."""
    await super().process(text, self.user_data)

  async def skip(self) -> None:
    """Skip user's current state.
    See base class for more details."""
    await super().skip(self.user_data)

class WebInterface(Interface):
  """Web interface."""

  def __init__(self, nickname: str='Web'):
    super().__init__(nickname)
    self.web = Flask(
      __name__,
      static_url_path='', 
      static_folder='web/static',
      template_folder='web/templates')

    @self.web.route('/')
    def index():
      return render_template('index.html')

    @self.web.route('/favicon.ico')
    def favicon():
      return send_from_directory(os.path.join(self.web.root_path, 'web/static'),
                                 'favicon.ico', mimetype='image/x-icon')

    @self.web.errorhandler(HTTPException)
    def handle_exception(e):
      return render_template('error.html', code=e.code, message=e.description), e.code

    @self.web.route('/bot', methods=['POST'])
    def bot():
      data: Dict[str, Any] = json.loads(json.dumps(request.json), object_hook=UserDataDecoder.default)
      context = WebContext(user_data=data['user_data'])
      asyncio.run(context.process(data['text'].lower()))
      return jsonify({
        'user_data': json.loads(json.dumps(context.user_data, cls=UserDataEncoder)),
        'responses': context.responses})
   
def create_interface():
  i = WebInterface()
  return i.web

def main():
  try: 
    create_interface().run(host='0.0.0.0')
  except KeyboardInterrupt:
    sys.exit()

if __name__ == '__main__':
  main()
