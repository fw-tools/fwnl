#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import RLock
from abc import ABCMeta

"""Singleton meta-classes."""

class SingletonMeta(type):
  """Thread-safe implementation of Singleton."""
  _lock: RLock = RLock()

  def __call__(cls, *args, **kwargs) -> object:
    try:
      return cls.__instance
    except AttributeError:
      with cls._lock:
        cls.__instance = super().__call__(*args, **kwargs)
      return cls.__instance

class SingletonABCMeta(SingletonMeta, ABCMeta):
  """ABC-based implementation of Singleton."""
  pass
