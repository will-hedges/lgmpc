#!/usr/bin/env python3
# lgmpm.py - Logitech G Mouse Profile Manager
#   a script to manage and cycle profiles for Logitech G mice with ratbagctl

import argparse

from mouse import Mouse
from mouseprofile import MouseProfile


def main():
    parser = argparse.ArgumentParser(
        description="Manages profiles for Logitech G mice using ratbagctl",
    )
    # make 'default' profile the default option for profile
    #   ex. if the user doesn't provide a profile name, we'll use default
    #       TODO add a confirmation prompt for methods on the default profile
    parser.add_argument("profile", type=str, nargs="?", default="default")
    parser.add_argument(
        "-c",
        "--cycle",
        help="Cycle (up) to the next stored profile (if it exists)",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--new",
        help="Create a new profile with name <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--show",
        help="Show the profile settings, similar to 'ratbagctl <device> info'",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--load",
        help="Load <profile> onto the connected mouse",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="Update <profile> with the current mouse settings",
        action="store_true",
    )
    parser.add_argument("-d", "--delete", help="Delete <profile>", action="store_true")
    args = parser.parse_args()

    # show an error if more than one flag is set
    flag_count = len([v for v in args.__dict__.values() if v is True])
    if flag_count > 1:
        print("TODO SET SOME MESSAGE")
        return

    # init mouse
    mouse = Mouse()

    if args.new:
        mp = MouseProfile()
        d = mp.__dict__
        # TODO create a new profile with the existing settings
        # basically, just init a MouseProfile with the current settings
        # and save it to mouse["profiles"]["<profile_name>"]
        pass
    elif args.show:
        # TODO show the current mouse settings with ratbagctl
        pass
    elif args.load:
        # TODO set the profile to the mouse
        pass
    elif args.update:
        # TODO update profile with the current mouse settings
        pass
    elif args.delete:
        # TODO delete the profile
        pass

    # if no flags are set, just cycle the profile
    else:
        mouse = Mouse()
        if len(mouse.profiles) < 2:
            # TODO display an error message
            return
        mouse.cycle_profile()

    return


if __name__ == "__main__":
    main()
