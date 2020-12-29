## Welcome to the PythonWars 1996 release.
<br />
This Mud driver is a *C->Python* conversion of *God Wars 1996*.

I have largely tried to keep personal taste choices out of this conversion and tried to make the Python source as
close to the original C source.  Unfortunately that means not fixing bugs, typos and other instances for something
seemingly not being quite right.  That being said there have no doubt been some instances where I have elected to
deviate from the original code and change something.  Most times it has likely been an unconcious decision such
as encountering a misspelled word, wrong capitalization and/or misplaced punctation.<br />


I have also chosen not to include some aspects of the God Wars 1996 source within this release. Some features such as
"evil_eye" were non-functional and as such had little part within various class powers. [JINNOTE: Add more here.]<br />


Notable instances of changes:

    • str_cmp: Returns opposite of stock sources. This decision was made for improved
      readability. BSTR also allows for list comparisons.

    • ANSI Color: There is inline color code support available for PythonWars, this
      feature was not available within the original C source.

    • BodyParts class - ch->loc_hp[] changed for improved readability.
        ch.head
        ch.arm_left
        ch.arm_right
        ch.bleeding
        etc

## Installation and Usage ##

### Windows ###

1. Install a copy of the latest version of Python 3 (currently tested on 3.8.x)
1. Ensure that the Python directory is available on your PATH environment variable
1. Open a new command prompt window
1. Navigate to "~/pythonwars-1996/"
1. Run "python pywars.py"


If all went well, you should see initialization messages as the Mud boots.  By default, the Mud
uses port 4123. You can connect to localhost:4123 and login.
<br />

Additionally, PyCharm can be used as a development environment which can be obtained here [here](https://www.jetbrains.com/pycharm/download/#section=windows).

## Configuring an Immortal Characters ##

By default, the first character created has full Implementor rights. However, additional
Immortals can be created through various means such as the *mset*, *trust*, and *relevel* commands
in game or by editing the user's player file.

    Editing Player FIle

    *  Create a character
    *  Kill 5 mobiles
    *  Save and log out
    *  Locate your character file:
        "~/pythonwars-1996/data/players/<initial letter>/<player name>/player.json"
    *  Open and modify the "_trust" and "Level" variables to the desired level (7-12)
    *  Save the file
    *  Log back into your character

    The Relevel Command

    *  Edit the Relevel command file:
        "~/pythonwars-1996/commands/cmd_relevel.py
    *  Add the player's name to the desired level.
        if game_utils.str_cmp(ch.name, ["Jim", "Bob", "John"]):
    *  Reload the changed file in game with the 'reload' command.
    *  The new Immortal character can now type 'relevel' to set new trust/level.


This file is a work in progress and contains work done by Pyom author [Davion](http://www.mudbytes.net/).