# -*- coding: utf-8 -*- line endings: unix -*-

#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
#
#  ROM 2.4 is copyright 1993-1998 Russ Taylor.  ROM has been brought to
#  you by the ROM consortium:  Russ Taylor (rtaylor@hypercube.org),
#  Gabrielle Taylor (gtaylor@hypercube.org), and Brian Moore (zump@rom.org).
#
#  Ported to Python by Davion of MudBytes.net using Miniboa
#  (https://code.google.com/p/miniboa/).
#
#  In order to use any part of this Merc Diku Mud, you must comply with
#  both the original Diku license in 'license.doc' as well the Merc
#  license in 'license.txt'.  In particular, you may not remove either of
#  these copyright notices.
#
#  Much time and thought has gone into this software, and you are
#  benefiting.  We hope that you share your changes too.  What goes
#  around, comes around.

#
# Report any bugs in this implementation to me (email above)
# ------------------------------------------------------------------------------
# Additional changes by Quixadhal on 2014.06.16
# -Re-split code into multiple files, for ease of maintenance
# -Rewrote terminal system
#
# Pinkfish style color codes are now available, as used in various
# LPMUD systems, as well as the I3 intermud network.
#
# Briefly, a color token is surrounded by the special symbol %^, which
# acts as a seperator for multiple tokens in a row.  So, an example like
#
# A %^RED%^red apple%^RESET%^ and a %^BOLD%^BLUE%^blue ball%^RESET%^.
#
# Would result in "red apple" and "blue ball" being colored, and
# "blue ball" would also be in bold.
#
# Some terminals will amke that actual bold, others will make it a
# brighter blue color.
#
# The replacement is dependent on the terminal type passed in, which
# defaults to ANSI, but can be "unknown" to strip colors, or
# "i3" or "imc2" for the intermud networks, or "mxp" for that.
# ------------------------------------------------------------------------------

"""
Support for color and formatting for various terminals or
terminal-like systems
"""

import re

import miniboa.colors

_PARA_BREAK = re.compile(r"(\n\s*\n)", re.MULTILINE)


def word_wrap(text: str, columns=80, indent=4, padding=2):
    """
    Given a block of text, breaks into a list of lines wrapped to
    length.
    :param padding:
    :param indent:
    :param columns:
    :param text:
    """
    paragraphs = _PARA_BREAK.split(text)
    lines = []
    columns -= padding
    for para in paragraphs:
        if para.isspace():
            continue
        line = ' ' * indent
        linelen = len(line)
        words = para.split()
        for word in words:
            bareword = color_convert(word, 'ANSI')
            if (linelen + 1 + len(bareword)) > columns:
                lines.append(line)
                line = ' ' * padding
                linelen = len(line)
                line += word
                linelen += len(bareword)
            else:
                line += ' ' + word
                linelen += len(bareword) + 1
        if not line.isspace():
            lines.append(line)
    return lines


def color_convert(text: str or None, output_type="ANSI"):
    if text is None or len(text) < 1:
        return ""

    if not output_type:
        output_type = "ANSI"

    if output_type is None:
        output_type = 'unknown'

    return miniboa.colors.colorize(text, True if output_type == "ANSI" else False)


def escape(text: str, input_type="ANSI"):
    """
    Escape all the color tokens in the given text chunk, so they
    can be safely printed through the color parser
    :param input_type:
    :param text:
    """
    if text is None or text == "":
        return text

    if input_type == "ANSI":
        text = text.replace('#', '##')
        text = text.replace('^', '^^')
        text = text.replace('}', '}}')

    return text
