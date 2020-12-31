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

from collections import OrderedDict, namedtuple


position_type = namedtuple('position_type', 'name, short_name')
position_table = OrderedDict()

sex_table = OrderedDict()

# various flag tables
flag_type = namedtuple('flag_type', 'name, bit, settable')
act_flags = OrderedDict()
affect_flags = OrderedDict()
blocarm_flags = OrderedDict()
blocbleed_flags = OrderedDict()
blocbody_flags = OrderedDict()
blochead_flags = OrderedDict()
blocleg_flags = OrderedDict()
channel_flags = OrderedDict()
charextra_flags = OrderedDict()
demon_flags = OrderedDict()
exit_flags = OrderedDict()
immune_flags = OrderedDict()
itemaff_flags = OrderedDict()
plr_flags = OrderedDict()
polyaff_flags = OrderedDict()
quest_flags = OrderedDict()
room_flags = OrderedDict()
sentance_flags = OrderedDict()
special_flags = OrderedDict()
spectype_flags = OrderedDict()
vampaff_flags = OrderedDict()

bit_flags = OrderedDict()
bit_flags["act_flags"] = act_flags
bit_flags["affect_flags"] = affect_flags
bit_flags["blocarm_flags"] = blocarm_flags
bit_flags["blocbleed_flags"] = blocbleed_flags
bit_flags["blocbody_flags"] = blocbleed_flags
bit_flags["blochead_flags"] = blochead_flags
bit_flags["blocleg_flags"] = blocleg_flags
bit_flags["channel_flags"] = channel_flags
bit_flags["charextra_flags"] = charextra_flags
bit_flags["demon_flags"] = demon_flags
bit_flags["exit_flags"] = exit_flags
bit_flags["immune_flags"] = immune_flags
bit_flags["itemaff_flags"] = itemaff_flags
bit_flags["plr_flags"] = plr_flags
bit_flags["polyaff_flags"] = polyaff_flags
bit_flags["quest_flags"] = quest_flags
bit_flags["room_flags"] = room_flags
bit_flags["sentance_flags"] = sentance_flags
bit_flags["special_flags"] = special_flags
bit_flags["spectype_flags"] = spectype_flags
bit_flags["vampaff_flags"] = vampaff_flags
