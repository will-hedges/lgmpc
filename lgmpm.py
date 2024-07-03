#!/usr/bin/env python3
# lgmpm.py - Logitech G Mouse Profile Manager - manages profiles for Logitech G
#   mice with ratbagctl

import sys

from mouse import Mouse
from utils import mouse_arg_parser, print_help_msg


def main():

    args = mouse_arg_parser()

    # show an error if more than one flag is set
    flag_count = list(args.__dict__.values()).count(True)
    if flag_count > 1:
        print(f"Error: multiple flags received: {", ".join(sys.argv[1:])}")
        print("Please try again with only one flag")
        print_help_msg()
        return

    mouse = Mouse()

    if args.active:
        mouse.set_active_profile(args.profile_name)

    # TODO --cycle, --list, and --new do not need a profile_name as an arg
    #   so should this throw an error if the user provides one?
    #       currently works fine without any handling
    elif args.cycle:
        mouse.cycle_profile()

    elif args.delete:
        mouse.delete_profile(args.profile_name)

    elif args.list:
        mouse.list_profiles()

    elif args.new:
        mouse.add_new_profile(args.profile_name)

    elif args.show:
        mouse.show_profile(args.profile_name)

    elif args.update:
        mouse.update_profile(args.profile_name)

    else:
        # if no flags are set, show a message
        print("No flag(s) set")
        print_help_msg()

    return


if __name__ == "__main__":
    main()
