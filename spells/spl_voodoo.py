#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
#
#  GodWars improvements copyright © 1995, 1996 by Richard Woolcock.
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

import const
import game_utils
import handler_game
import handler_magic
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_voodoo(sn, level, ch, victim, target):
    handler_magic.target_name, arg = game_utils.read_word(handler_magic.target_name)

    if ch.practice < 5:
        ch.send("It costs 5 points of primal energy to create a voodoo doll.\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    item = ch.get_eq("right_hand")
    if not item:
        item = ch.get_eq("left_hand")
        if not item:
            ch.send("You are not holding any body parts.\n")
            return

    part_list = [(12, "head"), (13, "heart"), (14, "arm"), (15, "leg"), (30004, "entrails"), (30005, "brain"), (30006, "eye eyeball"),
                 (30012, "face"), (30013, "windpipe"), (30014, "cracked head"), (30025, "ear"), (30026, "nose"), (30027, "tooth"),
                 (30028, "tongue"), (30029, "hand"), (30030, "foot"), (30031, "thumb"), (30032, "index finger"), (30033, "middle finger"),
                 (30034, "ring finger"), (30035, "little finger"), (30036, "toe")]
    for (aa, bb) in part_list:
        if item.value[2] == aa:
            part1 = aa + " " + victim.name
            break
    else:
        ch.send(f"{item.name} isn't a part of {victim.name}!\n")
        return

    part2 = item.name
    if not game_utils.str_cmp(part1, part2):
        ch.send(f"But you are holding {item.short_descr}, not {victim.name}!\n")
        return

    handler_game.act("$p vanishes from your hand in a puff of smoke.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p vanishes from $n's hand in a puff of smoke.", ch, item, None, merc.TO_ROOM)
    ch.get(item)
    item.extract()

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_VOODOO_DOLL], 0)
    item.name = f"{victim.name} voodoo doll"
    item.short_descr = f"a voodoo doll of {victim.name}"
    item.description = f"A voodoo doll of {victim.name} lies here."
    ch.put(item)
    ch.equip(item, replace=False, verbose=False)
    handler_game.act("$p appears in your hand.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p appears in $n's hand.", ch, item, None, merc.TO_ROOM)
    ch.practice -= 5


const.register_spell(
    const.skill_type(
        name="voodoo",
        skill_level=1,
        spell_fun=spl_voodoo,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(606),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Voodoo!"
    )
)
