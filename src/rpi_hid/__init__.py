"""
rpi-hid-keyboard: A sovereign hardware bridge for other applications.
This package provides the logic to convert transcribed text into 
USB HID keyboard reports.
"""

# Promoting key classes to the top-level package namespace
from .layout import USBKeyboardLayout
from .daemon import HIDDaemon

# Version tracking for your "series story"
__version__ = "0.1.0"

# Defining what is available for "from rpi4_hid import *"
__all__ = ["USBKeyboardLayout", "HIDDaemon"]
