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

import game_utils
import interp
import merc


def cmd_totems(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_werewolf():
        ch.huh()
        return

    if not arg1 and not arg2:
        ch.send("Totems: Bear ({}), Lynx ({}), Boar ({}), Owl ({}), Spider ({}), Wolf ({}),\n"
                "        Hawk ({}), Mantis ({}).\n".format(ch.powers[merc.WPOWER_BEAR], ch.powers[merc.WPOWER_LYNX], ch.powers[merc.WPOWER_BOAR],
                                                           ch.powers[merc.WPOWER_OWL], ch.powers[merc.WPOWER_SPIDER], ch.powers[merc.WPOWER_WOLF],
                                                           ch.powers[merc.WPOWER_HAWK], ch.powers[merc.WPOWER_MANTIS]))
        return

    if not arg2:
        if game_utils.str_cmp(arg1, "bear"):
            buf = ["Bear: The totem of strength and aggression.\n"]
            if ch.powers[merc.WPOWER_BEAR] < 1:
                buf += "You have none of the Bear totem powers.\n"
            else:
                totem_list = [(1, "FLEX: You strength is so great that no ropes can hold you."),
                              (2, "RAGE: You are able to build yourself up a rage at will."),
                              (3, "Steel claws: Your claws are so tough that they can parry weapons."),
                              (4, "Hibernation: Your wounds heal at amazing speeds when you sleep.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_BEAR] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "boar"):
            buf = ["Boar: The totem of toughness and perserverance.\n"]

            if ch.powers[merc.WPOWER_BOAR] < 1:
                buf += "You have none of the Boar totem powers.\n"
            else:
                totem_list = [(1, "Shatter: No door is sturdy enough to resist you."),
                              (2, "CHARGE: Your first blow in combat has a +50 damage bonus."),
                              (3, "Toughness: Your skin is extremely tough. You take half damage in combat."),
                              (4, "Immovability: You are able to shrug off blows that would knock out most people.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_BOAR] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "lynx"):
            buf = ["Lynx: The totem of speed and agility."]

            if ch.powers[merc.WPOWER_LYNX] < 1:
                buf += "You have none of the Lynx totem powers."
            else:
                totem_list = [(1, "Light footed: You move so lightly that you leave no tracks behind you."),
                              (2, "Stalker: You are able hunt people with much greater speed than normal."),
                              (3, "Combat speed: You have an extra attack in combat."),
                              (4, "Lightning Claws: Yours claws parry blows with lightning fast speed.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_LYNX] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "owl"):
            buf = ["Owl: The totem of thought and spiritualism.\n"]

            if ch.powers[merc.WPOWER_OWL] < 1:
                buf += "You have none of the Owl totem powers.\n"
            else:
                totem_list = [(1, "VANISH: You are able to conceal yourself from all but the most perceptive."),
                              (2, "SHIELD: You are able to shield your mind from scrying and aura-reading."),
                              (3, "SHADOWPLANE: You are able to enter the shadow plane."),
                              (4, "Magical Control: You are able to fully control your magic in crinos form.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_OWL] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "spider"):
            buf = ["Spider: The totem of ambush and cunning.\n"]

            if ch.powers[merc.WPOWER_SPIDER] < 1:
                buf += "You have none of the Spider totem powers.\n"
            else:
                totem_list = [(1, "Poisonous bite: Your bite injects your opponents with a deadly venom."),
                              (2, "WEB: You are able to shoot a web at your opponents to entrap them."),
                              (3, "Immunity to poison: Poisons have no affect upon you.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_SPIDER] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "wolf"):
            buf = ["Wolf: Controlling your innate wolf powers.\n"]

            if ch.powers[merc.WPOWER_WOLF] < 1:
                buf += "You have none of the Wolf totem powers.\n"
            else:
                totem_list = [(1, "CLAWS: You can extend or retract your claws at will."),
                              (2, "FANGS: You can extend or retract your fangs at will."),
                              (3, "CALM: You are able to repress your inner beast at will."),
                              (4, "Spirit of Fenris: You are able to enter rage faster than normal.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_WOLF] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "hawk"):
            buf = ["Hawk: The totem of vision and perception.\n"]

            if ch.powers[merc.WPOWER_HAWK] < 1:
                buf += "You have none of the Wolf totem powers.\n"
            else:
                totem_list = [(1, "NIGHTSIGHT: You can see perfectly well in the dark."),
                              (2, "SHADOWSIGHT: You can see into the plane of shadows."),
                              (3, "TRUESIGHT: You have perfect vision.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_HAWK] >= aa:
                        buf += bb + "\n"
            ch.send("".join(buf))
        elif game_utils.str_cmp(arg1, "mantis"):
            buf = ["Mantis: The totem of dexterity and reflexes.\n"]

            if ch.powers[merc.WPOWER_MANTIS] < 1:
                buf += "You have none of the Mantis totem powers.\n"
            else:
                totem_list = [(4, "Incredibly fast attacks: Your opponents get -20 to parry and -40 to dodge."),
                              (3, "Extremely fast attacks: Your opponents get -15 to parry and -30 to dodge."),
                              (2, "Very fast attacks: Your opponents get -10 to parry and -20 to dodge."),
                              (1, "Fast attacks: Your opponents get -5 to parry and -10 to dodge.")]
                for (aa, bb) in totem_list:
                    if ch.powers[merc.WPOWER_MANTIS] == aa:
                        buf += bb + "\n"
                        break
            ch.send("".join(buf))
        else:
            ch.send("Totems: Bear ({}), Lynx ({}), Boar ({}), Owl ({}), Spider ({}), Wolf ({}),\n"
                    "        Hawk ({}), Mantis ({}).\n".format(ch.powers[merc.WPOWER_BEAR], ch.powers[merc.WPOWER_LYNX], ch.powers[merc.WPOWER_BOAR],
                                                               ch.powers[merc.WPOWER_OWL], ch.powers[merc.WPOWER_SPIDER], ch.powers[merc.WPOWER_WOLF],
                                                               ch.powers[merc.WPOWER_HAWK], ch.powers[merc.WPOWER_MANTIS]))
        return

    if game_utils.str_cmp(arg2, "improve"):
        totem_list = [("bear", merc.WPOWER_BEAR, 4), ("boar", merc.WPOWER_BOAR, 4), ("lynx", merc.WPOWER_LYNX, 4),
                      ("owl", merc.WPOWER_OWL, 4), ("spider", merc.WPOWER_SPIDER, 3), ("wolf", merc.WPOWER_WOLF, 4),
                      ("hawk", merc.WPOWER_HAWK, 3), ("mantis", merc.WPOWER_MANTIS, 3)]
        for (aa, bb, cc) in totem_list:
            if game_utils.str_cmp(arg1, aa):
                improve = bb
                tmax = cc
                break
        else:
            ch.send("You can improve: Bear, Boar, Lynx, Owl, Spider, Wolf, Hawk or Mantis.\n")
            return

        cost = (ch.powers[improve] + 1) * 10
        arg1 = arg1[0].upper() + arg1[1:].lower()

        if ch.powers[improve] >= tmax:
            ch.send("You have already gained all the powers of the {} totem.\n".format(arg1))
            return

        if ch.practice < cost:
            ch.send("It costs you {} primal to improve your {} totem.\n".format(cost, arg1))
            return

        ch.powers[improve] += 1
        ch.practice -= cost
        ch.send("You improve your ability in the {} totem.\n".format(arg1))
    else:
        ch.send("To improve a totem, type: Totem <totem type> improve.\n")


interp.register_command(
    interp.CmdType(
        name="totems",
        cmd_fun=cmd_totems,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
