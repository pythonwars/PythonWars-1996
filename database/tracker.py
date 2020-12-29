#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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

from const import liq_table, attack_table, con_app, dex_app, wis_app, int_app, str_app, class_table, skill_table, \
    liq_type, attack_type, dex_app_type, wis_app_type, int_app_type, str_app_type, class_type, skill_type, \
    con_app_type, social_type, social_table
from tables import room_flags, affect_flags, plr_flags, act_flags, sex_table, position_table, position_type, \
    flag_type, exit_flags, charextra_flags, spectype_flags, special_flags, vampaff_flags, demon_flags, blocarm_flags, \
    blocbleed_flags, blocbody_flags, blochead_flags, blocleg_flags, channel_flags, itemaff_flags, sentance_flags, \
    immune_flags, polyaff_flags, quest_flags


def skill_filter(table):
    return {k: v for k, v in table.items() if not v.spell_fun}


class SaveToken:
    def __init__(self, name, table, tupletype, sfilter=None):
        self.name = name
        self.table = table
        self.tupletype = tupletype
        self.filter = sfilter


tables = [SaveToken("act_flags", act_flags, flag_type),
          SaveToken("affect_flags", affect_flags, flag_type),
          SaveToken("blocarm_flags", blocarm_flags, flag_type),
          SaveToken("blocbleed_flags", blocbleed_flags, flag_type),
          SaveToken("blocbody_flags", blocbody_flags, flag_type),
          SaveToken("blochead_flags", blochead_flags, flag_type),
          SaveToken("blocleg_flags", blocleg_flags, flag_type),
          SaveToken("channel_flags", channel_flags, flag_type),
          SaveToken("charextra_flags", charextra_flags, flag_type),
          SaveToken("demon_flags", demon_flags, flag_type),
          SaveToken("exit_flags", exit_flags, flag_type),
          SaveToken("immune_flags", immune_flags, flag_type),
          SaveToken("itemaff_flags", itemaff_flags, flag_type),
          SaveToken("plr_flags", plr_flags, flag_type),
          SaveToken("polyaff_flags", polyaff_flags, flag_type),
          SaveToken("quest_flags", quest_flags, flag_type),
          SaveToken("room_flags", room_flags, flag_type),
          SaveToken("sentance_flags", sentance_flags, flag_type),
          SaveToken("special_flags", special_flags, flag_type),
          SaveToken("spectype_flags", spectype_flags, flag_type),
          SaveToken("vampaff_flags", vampaff_flags, flag_type),

          SaveToken("attack_table", attack_table, attack_type),
          SaveToken("class_table", class_table, class_type),

          SaveToken("liq_table", liq_table, liq_type),
          SaveToken("position_table", position_table, position_type),
          SaveToken("sex_table", sex_table, None),
          SaveToken("skill_table", skill_table, skill_type, skill_filter),
          SaveToken("social_table", social_table, social_type),

          SaveToken("str_app", str_app, str_app_type),
          SaveToken("int_app", int_app, int_app_type),
          SaveToken("wis_app", wis_app, wis_app_type),
          SaveToken("dex_app", dex_app, dex_app_type),
          SaveToken("con_app", con_app, con_app_type)]
