#!/usr/bin/env python
"""
This is a NodeServer for Airscape Fans for Polyglot v2 written in Python2/3
"""
from udi_interface import Interface,LOGGER
from nodes import Controller
import sys

if __name__ == "__main__":
    try:
        polyglot = Interface([Controller])
        polyglot.start()
        control = Controller(polyglot, 'controller', 'controller', 'Airscape')
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
