#!/usr/bin/env python3
# lgmpm.py - Logitech G Mouse Profile Manager
#   a script to manage and cycle profiles for Logitech G mice with ratbagctl

import argparse
import sys

from mouse import Mouse
from mouseprofile import MouseProfile
from utils import print_help_msg


def main():
    parser = argparse.ArgumentParser(
        description="manages profiles for Logitech G mice using ratbagctl",
    )
    parser.add_argument(
        "profile_name",
        nargs="?",
        type=str,
        default="default",
        help="the name of the profile",
    )
    parser.add_argument(
        "-a",
        "--active",
        help="make <profile_name> the active profile",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--cycle",
        help="cycle (up) to the next stored profile, if one exists",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--delete",
        help="delete <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--list",
        help="list all saved profiles for the connected mouse",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--new",
        help="create a new profile with called <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--show",
        help="show the saved settings for <profile_name>",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="update <profile_name> with the current mouse settings",
        action="store_true",
    )

    args = parser.parse_args()

    # show an error if more than one flag is set
    flag_count = list(args.__dict__.values()).count(True)
    if flag_count > 1:
        print(f"Error: multiple flags received: {", ".join(sys.argv[1:])}")
        print("Please try again with only one flag")
        print_help_msg()
        return

    # init mouse
    mouse = Mouse()

    if args.active:
        mouse.set_active_profile(args.profile_name)
        return

    elif args.cycle:
        # we will check to see if there is only one profile saved, since we
        #   should always have default even if there was no json file prior to
        #       first time setup, so check if # of profiles == 1
        # NOTE the user could delete the default profile, so we will just show
        #   whatever profile name is there
        if len(mouse.profiles) == 1:
            sole_profile_name = tuple(mouse.profiles.keys())[0]
            print(f"Only 1 profile found: '{sole_profile_name}'")
            print_help_msg()
            return
        else:
            mouse.cycle_profile()
            return

    elif args.delete:
        mouse.delete_profile(args.profile_name)
        return

    elif args.list:
        print(f"Found the following {mouse.model.upper()} profiles:")
        for idx, name in enumerate(sorted(mouse.profiles)):
            print(f"  {idx + 1}. {name}")
        print_help_msg()
        return

    elif args.new:
        new_profile = MouseProfile(name=args.profile_name)
        mouse.add_new_profile(args.profile_name, new_profile.__dict__)
        return

    elif args.show:
        # TODO show the current mouse settings with ratbagctl
        # TODO I think this should be a mouseProfile method
        return

    elif args.update:
        updated_profile = MouseProfile(name=args.profile_name)
        mouse.update_profile(args.profile_name, updated_profile.__dict__)
        return

    # if no flags are set, show a message
    else:
        print("No flag(s) set")
        print_help_msg()
        return


if __name__ == "__main__":
    main()
