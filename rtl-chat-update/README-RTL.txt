RTL/Persian chat update
=======================

Replace these files in your laptop_guard package:
  laptop_guard/text_direction.py
  laptop_guard/chat_surface.py
  laptop_guard/chat_window.py

Recommended dependencies:
  python -m pip install python-bidi arabic-reshaper

Important design rule:
- JSON, inbox/outbox, mirror files, callbacks and copied text stay in normal/logical Unicode order.
- Only Tkinter labels/message bubbles use visual BiDi conversion.
- The composer keeps logical text so sending/copying Persian text is not corrupted.
- AUTO direction uses the first strong Unicode character, so mixed Persian/English text works better.
