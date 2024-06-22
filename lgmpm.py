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
    parser.add_argument(
        "profile_name",
        nargs="?",
        default="default",
        type=str,
        help="the name of the profile",
    )
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
        "-l",
        "--list",
        help="List all saved profiles for the connected mouse",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--show",
        help="Show the profile settings, similar to 'ratbagctl <device> info'",
        action="store_true",
    )
    parser.add_argument(
        "-w",
        "--write",
        help="Write <profile_name> to the connected mouse",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="Update <profile_name> with the current mouse settings",
        action="store_true",
    )
    parser.add_argument("-d", "--delete", help="Delete <profile>", action="store_true")

    args = parser.parse_args()

    # show an error if more than one flag is set
    flag_count = list(args.__dict__.values()).count(True)
    if flag_count > 1:
        print("TODO SET SOME MESSAGE")
        return

    # init mouse
    mouse = Mouse()

    if args.cycle:
        # TODO cycle method
        pass

    elif args.new:
        # create a new profile with the existing settings
        #   and save it to mouse.profiles as a new key-value pair
        #       where the key is the profile name and the value is the MouseProfile
        new_profile = MouseProfile(name=args.profile_name)
        mouse.add_profile(new_profile.name, new_profile.__dict__)

    elif args.list:
        # TODO show a list of profiles
        pass

    elif args.show:
        # TODO show the current mouse settings with ratbagctl
        pass

    elif args.write:
        # TODO write the mouse profile to the mouse
        pass

    elif args.update:
        # init a new profile with name given
        updated_profile = MouseProfile(name=args.profile_name)
        # update the existing profile
        # TODO add a try/except block for if the key doesn't exist
        mouse.update_profile(updated_profile.name, updated_profile.__dict__)
        # TODO set the current/last run profile to the new one
        # TODO write out the curernt/last run profile to json as well as the new profile data
        pass

    elif args.delete:
        mouse.delete_profile(args.profile_name)

    # if no flags are set, just cycle the profile
    else:
        if len(mouse.profiles) < 2:
            # TODO display an error message
            return
        mouse.cycle_profile()

    return


if __name__ == "__main__":
    main()
