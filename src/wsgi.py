#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Web Server Gateway Interface"""

from interfaces.web import create_interface

web = create_interface()

if __name__ == '__main__':
  web.run()
